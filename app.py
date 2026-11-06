import logging
import os

from dotenv import load_dotenv

load_dotenv()

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

from models import MovieFeedback, RecommendationHistory, Review, SearchHistory, User, db
from services.movie_engine import MovieEngine
from services.sentiment_service import SentimentService
from services.tmdb_service import TMDBService

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
if not app.secret_key or not app.secret_key.strip():
    raise RuntimeError("FLASK_SECRET_KEY must be set and non-empty")


app.config["SECRET_KEY"] = app.secret_key

# Database Configuration
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL not found")
database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
if not database_url.startswith("sqlite:"):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_size": 5,
        "pool_recycle": 1800,
        "pool_pre_ping": True,
    }
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

csrf = CSRFProtect(app)

rate_limit_storage_uri = os.environ.get("RATELIMIT_STORAGE_URI")
if not rate_limit_storage_uri:
    raise RuntimeError("RATELIMIT_STORAGE_URI must be set")

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri=rate_limit_storage_uri,
    default_limits=[],
    in_memory_fallback_enabled=False,
    swallow_errors=False,
)


@app.before_request
def require_authentication():
    public_endpoints = {"login", "signup", "signin", "static", "health"}
    if request.endpoint in public_endpoints or request.endpoint is None:
        return None

    if "user_id" not in session:
        if request.path.startswith("/api/"):
            return {"error": "Authentication required"}, 401
        return redirect(url_for("login"))

    return None


# Authentication Routes
@app.route("/login", methods=["GET"])
def login():
    if "user_id" in session:
        return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/signup", methods=["POST"])
def signup():
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    if User.query.filter_by(email=email).first():
        flash("Email already exists", "error")
        return redirect(url_for("login"))

    if User.query.filter_by(username=username).first():
        flash("Username already exists", "error")
        return redirect(url_for("login"))

    try:
        new_user = User(
            username=username, email=email, password=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please sign in.", "success")
        return redirect(url_for("login"))
    except Exception as e:
        db.session.rollback()
        logging.info(f"Signup error: {e}")
        flash("Signup failed. Try again.", "error")
        return redirect(url_for("login"))


@app.route("/signin", methods=["POST"])
def signin():
    username = request.form["signinUsername"]
    password = request.form["signinPassword"]

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password, password):
        flash("Please check your login details and try again.", "error")
        return redirect(url_for("login"))

    session["user_id"] = user.id
    session["username"] = user.username
    return redirect(url_for("home"))


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for("home"))


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
        homepage_movies.append(
            {
                "title": movie_titles[i],
                "poster": movie_posters[i]
                if i < len(movie_posters)
                else "https://via.placeholder.com/500x750?text=No+Poster",
            }
        )
    return render_template(
        "home.html",
        suggestions=suggestions,
        homepage_movies=homepage_movies,
        tmdb_configured=TMDBService.is_configured(),
    )


@app.route("/similarity", methods=["POST"])
def similarity():
    movie = request.form["name"]
    user_id = session.get("user_id")

    if user_id is not None:
        new_search = SearchHistory(user_id=user_id, search_term=movie)
        db.session.add(new_search)
        db.session.commit()

    movie_feedback = (
        MovieFeedback.query.filter_by(user_id=user_id).all()
        if user_id is not None
        else None
    )
    rec = MovieEngine.recommend_movies(movie, movie_feedback)

    if user_id is not None and isinstance(rec, list):
        rec_str = ",".join(rec)
        new_rec = RecommendationHistory(
            user_id=user_id, searched_movie=movie, recommended_movies=rec_str
        )
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
        title = request.form["title"]
        cast_ids = request.form["cast_ids"]
        cast_names = request.form["cast_names"]
        cast_chars = request.form["cast_chars"]
        cast_bdays = request.form["cast_bdays"]
        cast_bios = request.form["cast_bios"]
        cast_places = request.form["cast_places"]
        cast_profiles = request.form["cast_profiles"]
        imdb_id = request.form["imdb_id"]
        tmdb_movie_id = request.form.get("tmdb_movie_id", type=int)
        poster = request.form["poster"]
        genres = request.form["genres"]
        overview = request.form["overview"]
        vote_average = request.form["rating"]
        vote_count = request.form["vote_count"]
        release_date = request.form["release_date"]
        runtime = request.form["runtime"]
        status = request.form["status"]
        rec_movies = request.form["rec_movies"]
        rec_posters = request.form["rec_posters"]

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
        cast_ids = cast_ids.split(",")
        cast_ids[0] = cast_ids[0].replace("[", "")
        cast_ids[-1] = cast_ids[-1].replace("]", "")

        # Clean bios
        for i in range(len(cast_bios)):
            cast_bios[i] = cast_bios[i].replace(r"\n", "\n").replace(r"\"", '"')

        # Create dictionaries
        movie_cards = {rec_posters[i]: rec_movies[i] for i in range(len(rec_posters))}
        casts = {
            name: [cid, char, profile]
            for name, cid, char, profile in zip(
                cast_names, cast_ids, cast_chars, cast_profiles
            )
        }
        cast_details = {
            name: [cid, profile, bday, place, bio]
            for name, cid, profile, bday, place, bio in zip(
                cast_names, cast_ids, cast_profiles, cast_bdays, cast_places, cast_bios
            )
        }

        # Get trailer
        trailer_key = MovieEngine.get_trailer(imdb_id)

        # Get reviews
        db_reviews = Review.query.filter(Review.movie_title.ilike(title)).all()
        reviews_list = []
        reviews_status = []

        for rev in db_reviews:
            reviews_list.append(rev.content)
            reviews_status.append(rev.sentiment)

        # Create reviews dictionary
        movie_reviews = {
            reviews_list[i]: reviews_status[i] for i in range(len(reviews_list))
        }
        user_logged_in = "user_id" in session
        current_feedback = None
        user_id = session.get("user_id")
        if user_id is not None and tmdb_movie_id is not None and tmdb_movie_id > 0:
            saved_feedback = MovieFeedback.query.filter_by(
                user_id=user_id,
                tmdb_movie_id=tmdb_movie_id,
            ).first()
            if saved_feedback is not None:
                current_feedback = saved_feedback.preference

        return render_template(
            "recommender.html",
            title=title,
            poster=poster,
            overview=overview,
            vote_average=vote_average,
            vote_count=vote_count,
            release_date=release_date,
            runtime=runtime,
            status=status,
            genres=genres,
            movie_cards=movie_cards,
            reviews=movie_reviews,
            casts=casts,
            cast_details=cast_details,
            user_logged_in=user_logged_in,
            trailer_key=trailer_key,
            imdb_id=imdb_id,
            tmdb_movie_id=tmdb_movie_id,
            current_feedback=current_feedback,
        )

    except Exception:
        logging.exception("Error in /recommend route")
        return "Unable to load movie details. Please try again.", 500


@app.route("/add_review", methods=["POST"])
def add_review():
    if "user_id" not in session:
        return redirect(url_for("home"))

    user_id = session["user_id"]
    movie_title = request.form["movie_title"]
    content = request.form["review_content"]
    imdb_id = request.form.get("imdb_id")

    # Use SentimentService
    sentiment = SentimentService.predict(content)

    new_review = Review(
        user_id=user_id,
        movie_title=movie_title,
        imdb_id=imdb_id,
        content=content,
        sentiment=sentiment,
    )
    db.session.add(new_review)
    db.session.commit()

    flash("Review added successfully!", "success")
    return redirect(url_for("home"))


@app.route("/api/movie-feedback", methods=["POST"])
@limiter.shared_limit("120 per minute", scope="tmdb-proxy")
def save_movie_feedback():
    try:
        tmdb_movie_id = int(request.form.get("tmdb_movie_id", ""))
        preference = int(request.form.get("preference", ""))
    except ValueError:
        return {"error": "Valid movie and preference values are required."}, 400

    if tmdb_movie_id < 1:
        return {"error": "tmdb_movie_id must be positive."}, 400
    if preference not in (-1, 1):
        return {"error": "preference must be 1 (like) or -1 (dislike)."}, 400

    user_id = session["user_id"]
    feedback = MovieFeedback.query.filter_by(
        user_id=user_id,
        tmdb_movie_id=tmdb_movie_id,
    ).first()

    if feedback is None:
        movie_details = TMDBService.get_movie_details(tmdb_movie_id)
        if movie_details.get("error"):
            return {
                "error": "Movie data is unavailable; your feedback was not saved."
            }, 502

        movie_credits = TMDBService.get_movie_credits(tmdb_movie_id)
        if movie_credits.get("error"):
            return {
                "error": "Movie data is unavailable; your feedback was not saved."
            }, 502

        movie_title = movie_details.get("title")
        if not isinstance(movie_title, str):
            return {"error": "Movie details could not be verified."}, 404
        movie_title = movie_title.strip()
        if not movie_title or len(movie_title) > 200:
            return {"error": "Movie details could not be verified."}, 404

        feature_text = MovieEngine._extract_features_from_tmdb(tmdb_movie_id)
        if not feature_text.strip():
            return {
                "error": "Movie features are unavailable; your feedback was not saved."
            }, 502

        feedback = MovieFeedback(
            user_id=user_id,
            tmdb_movie_id=tmdb_movie_id,
            movie_title=movie_title,
            feature_text=feature_text,
            preference=preference,
        )
        db.session.add(feedback)
    else:
        feedback.preference = preference

    db.session.commit()
    return {
        "movie_title": feedback.movie_title,
        "preference": feedback.preference,
    }


# API Routes for TMDB (proxies)
@app.errorhandler(429)
def rate_limit_exceeded(error):
    return {"error": "Too many requests. Please try again later."}, 429


@app.route("/api/tmdb/search", methods=["GET"])
@limiter.shared_limit("120 per minute", scope="tmdb-proxy")
def tmdb_search():
    query = request.args.get("query", "").strip()
    if not query:
        return {"error": "query is required"}, 400
    if len(query) > 200:
        return {"error": "query must be 200 characters or fewer"}, 400
    return _tmdb_response(TMDBService.search_movie(query))


@app.route("/api/tmdb/movie/<int:movie_id>", methods=["GET"])
@limiter.shared_limit("120 per minute", scope="tmdb-proxy")
def tmdb_movie_details(movie_id):
    if movie_id < 1:
        return {"error": "movie_id must be positive"}, 400
    return _tmdb_response(TMDBService.get_movie_details(movie_id))


@app.route("/api/tmdb/movie/<int:movie_id>/credits", methods=["GET"])
@limiter.shared_limit("120 per minute", scope="tmdb-proxy")
def tmdb_movie_credits(movie_id):
    if movie_id < 1:
        return {"error": "movie_id must be positive"}, 400
    return _tmdb_response(TMDBService.get_movie_credits(movie_id))


@app.route("/api/tmdb/person/<int:person_id>", methods=["GET"])
@limiter.shared_limit("120 per minute", scope="tmdb-proxy")
def tmdb_person_details(person_id):
    if person_id < 1:
        return {"error": "person_id must be positive"}, 400
    return _tmdb_response(TMDBService.get_person_details(person_id))


def _tmdb_response(result):
    if "error" not in result:
        return result

    status_code = (
        503
        if result["error"] == "TMDB_API_KEY is not configured"
        or result["error"].startswith("TMDB rate limit")
        else 502
    )
    return result, status_code


@app.route("/health")
def health():
    try:
        db.session.execute(db.text("SELECT 1"))
        return {"status": "ok"}, 200
    except Exception as e:
        app.logger.error(f"Health check error: {e}")
        return {"status": "error"}, 503


if __name__ == "__main__":
    with app.app_context():
        MovieEngine.get_clf_vectorizer()
        MovieEngine.get_df_engine()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
