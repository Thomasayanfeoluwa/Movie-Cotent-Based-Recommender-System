import os
import pandas as pd
import numpy as np
import json
import logging
import requests
from flask_migrate import Migrate
from flask import Flask, request, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Review, SearchHistory, RecommendationHistory
from services.movie_engine import MovieEngine
from services.tmdb_service import TMDBService
from services.sentiment_service import SentimentService
from bs4 import BeautifulSoup
from dotenv import load_dotenv



load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

# Database Configuration
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL not found")
database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 5,
    'pool_recycle': 1800,
    'pool_pre_ping': True,
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Authentication Routes
@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    if User.query.filter_by(email=email).first():
        flash('Email already exists', 'error')
        return redirect(url_for('home'))

    if User.query.filter_by(username=username).first():
        flash('Username already exists', 'error')
        return redirect(url_for('home'))

    try:
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please sign in.', 'success')
        return redirect(url_for('home'))
    except Exception as e:
        db.session.rollback()
        logging.info(f"Signup error: {e}")
        flash('Signup failed. Try again.', 'error')
        return redirect(url_for('home'))

@app.route('/signin', methods=['POST'])
def signin():
    username = request.form['signinUsername']
    password = request.form['signinPassword']
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.', 'error')
        return redirect(url_for('home'))

    session['user_id'] = user.id
    session['username'] = user.username
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('home'))

# Main Routes
@app.route("/")
@app.route("/home")
def home():
    suggestions = MovieEngine.get_suggestions()
    # Get homepage recommendations
    movie_titles = MovieEngine.get_homepage_recommendations(20)
    # Get posters for these movies
    movie_posters = MovieEngine.get_homepage_posters(movie_titles)
    # Combine into list of dictionaries for easier template handling
    homepage_movies = []
    for i in range(len(movie_titles)):
        homepage_movies.append({
            'title': movie_titles[i],
            'poster': movie_posters[i] if i < len(movie_posters) else "https://via.placeholder.com/500x750?text=No+Poster"
        })
    return render_template("home.html", 
                         suggestions=suggestions,
                         homepage_movies=homepage_movies)

@app.route("/similarity", methods=["POST"])
def similarity():
    movie = request.form["name"]
    
    if 'user_id' in session:
        user_id = session['user_id']
        new_search = SearchHistory(user_id=user_id, search_term=movie)
        db.session.add(new_search)
        db.session.commit()

    rec = MovieEngine.recommend_movies(movie)
    
    if 'user_id' in session and isinstance(rec, list):
        user_id = session['user_id']
        rec_str = ",".join(rec)
        new_rec = RecommendationHistory(user_id=user_id, searched_movie=movie, recommended_movies=rec_str)
        db.session.add(new_rec)
        db.session.commit()

    if isinstance(rec, str):
        return rec
    else:
        return "---".join(rec)

@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        # Get data from AJAX request
        title = request.form['title']
        cast_ids = request.form['cast_ids']
        cast_names = request.form['cast_names']
        cast_chars = request.form['cast_chars']
        cast_bdays = request.form['cast_bdays']
        cast_bios = request.form['cast_bios']
        cast_places = request.form['cast_places']
        cast_profiles = request.form['cast_profiles']
        imdb_id = request.form['imdb_id']
        poster = request.form['poster']
        genres = request.form['genres']
        overview = request.form['overview']
        vote_average = request.form['rating']
        vote_count = request.form['vote_count']
        release_date = request.form['release_date']
        runtime = request.form['runtime']
        status = request.form['status']
        rec_movies = request.form['rec_movies']
        rec_posters = request.form['rec_posters']

        # Convert lists
        rec_movies = MovieEngine.convert_to_list(rec_movies)
        rec_posters = MovieEngine.convert_to_list(rec_posters)
        cast_names = MovieEngine.convert_to_list(cast_names)
        cast_chars = MovieEngine.convert_to_list(cast_chars)
        cast_profiles = MovieEngine.convert_to_list(cast_profiles)
        cast_bdays = MovieEngine.convert_to_list(cast_bdays)
        cast_bios = MovieEngine.convert_to_list(cast_bios)
        cast_places = MovieEngine.convert_to_list(cast_places)

        # Process cast IDs
        cast_ids = cast_ids.split(',')
        cast_ids[0] = cast_ids[0].replace("[","")
        cast_ids[-1] = cast_ids[-1].replace("]","")

        # Clean bios
        for i in range(len(cast_bios)):
            cast_bios[i] = cast_bios[i].replace(r'\n', '\n').replace(r'\"', '\"')

        # Create dictionaries
        movie_cards = {rec_posters[i]: rec_movies[i] for i in range(len(rec_posters))}
        casts = {name: [cid, char, profile] for name, cid, char, profile in zip(cast_names, cast_ids, cast_chars, cast_profiles)}
        cast_details = {name: [cid, profile, bday, place, bio] for name, cid, profile, bday, place, bio in zip(cast_names, cast_ids, cast_profiles, cast_bdays, cast_places, cast_bios)}

        # Get trailer
        trailer_key = MovieEngine.get_trailer(imdb_id)
        
        # Get reviews
        db_reviews = Review.query.filter(Review.movie_title.ilike(title)).all()
        reviews_list = []
        reviews_status = []
        
        for rev in db_reviews:
            reviews_list.append(rev.content)
            reviews_status.append(rev.sentiment)

        # Scrape IMDB reviews
        url = f'https://www.imdb.com/title/{imdb_id}/reviews/?ref_=tt_ov_rt'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }
    
        try:
            response = requests.get(url, headers=headers)
            logging.info(f"IMDB response status: {response.status_code}")
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'lxml')
                soup_result = soup.find_all("div", {"class": "ipc-html-content-inner-div"})
                
                for review in soup_result:
                    try:
                        content = review.get_text(strip=True)
                        if not content:
                            continue
                        reviews_list.append(content)
                        # Use SentimentService
                        sentiment = SentimentService.predict(content)
                        reviews_status.append(sentiment)
                    except Exception as e:
                        logging.info(f"Skipping review: {e}")
        except Exception as e:
            logging.info(f"IMDB Scraping Error: {e}")

        # Create reviews dictionary
        movie_reviews = {reviews_list[i]: reviews_status[i] for i in range(len(reviews_list))}
        user_logged_in = 'user_id' in session
        
        return render_template('recommender.html',
            title=title, poster=poster, overview=overview, vote_average=vote_average,
            vote_count=vote_count, release_date=release_date, runtime=runtime,
            status=status, genres=genres, movie_cards=movie_cards, reviews=movie_reviews,
            casts=casts, cast_details=cast_details, user_logged_in=user_logged_in,
            trailer_key=trailer_key, imdb_id=imdb_id)
                
    except Exception as e:
        logging.exception("Error in /recommend route")
        return str(e), 500

@app.route("/add_review", methods=["POST"])
def add_review():
    if 'user_id' not in session:
        return redirect(url_for('home'))
        
    user_id = session['user_id']
    movie_title = request.form['movie_title']
    content = request.form['review_content']
    imdb_id = request.form.get('imdb_id')
    
    # Use SentimentService
    sentiment = SentimentService.predict(content)
    
    new_review = Review(
        user_id=user_id, 
        movie_title=movie_title, 
        imdb_id=imdb_id, 
        content=content, 
        sentiment=sentiment
    )
    db.session.add(new_review)
    db.session.commit()
    
    flash("Review added successfully!", 'success')
    return redirect(url_for('home'))

# API Routes for TMDB (proxies)
@app.route("/api/tmdb/search", methods=["GET"])
def tmdb_search():
    query = request.args.get('query')
    return TMDBService.search_movie(query)

@app.route("/api/tmdb/movie/<int:movie_id>", methods=["GET"])
def tmdb_movie_details(movie_id):
    return TMDBService.get_movie_details(movie_id)

@app.route("/api/tmdb/movie/<int:movie_id>/credits", methods=["GET"])
def tmdb_movie_credits(movie_id):
    return TMDBService.get_movie_credits(movie_id)

@app.route("/api/tmdb/person/<int:person_id>", methods=["GET"])
def tmdb_person_details(person_id):
    return TMDBService.get_person_details(person_id)

@app.route('/health')
def health():
    try:
        db.session.execute(db.text('SELECT 1'))
        return {'status': 'ok'}, 200
    except Exception as e:
        app.logger.error(f"Health check error: {e}")
        return {'status': 'error'}, 503

if __name__ == '__main__':
    with app.app_context():
        MovieEngine.get_clf_vectorizer()
        MovieEngine.get_df_engine()
    port = int(os.environ.get("PORT", 10000))  
    app.run(host="0.0.0.0", port=port, debug=False)



