import pandas as pd
import numpy as np
import pickle
import faiss
import requests
import os
import logging
from bs4 import BeautifulSoup
from services.tmdb_service import TMDBService


logging.basicConfig(level=logging.INFO)

class MovieEngine:
    clf = None
    vectorizer = None
    df = None
    svd = None
    faiss_index = None

    @classmethod
    def _get_project_root(cls):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(current_dir)

    @classmethod
    def get_clf_vectorizer(cls):
        if cls.clf is None or cls.vectorizer is None:
            try:
                project_root = cls._get_project_root()
                
                model_path = os.path.join(project_root, "models", "comment_sentiments.pkl")
                vectorizer_path = os.path.join(project_root, "models", "transformed.pkl")

                with open(model_path, "rb") as f:
                    cls.clf = pickle.load(f)
                with open(vectorizer_path, "rb") as f:
                    cls.vectorizer = pickle.load(f)
                logging.info(f"Models Loaded Successfully from {project_root}/models/")
            except FileNotFoundError as e:
                logging.error(f"Models Loading Failed: {e}")
                raise e
        return cls.clf, cls.vectorizer

    @classmethod
    def get_df_engine(cls):
        if cls.df is None:
            try:
                project_root = cls._get_project_root()
                
                df_path = os.path.join(project_root, "models", "df.pkl")
                svd_path = os.path.join(project_root, "models", "svd.pkl")
                faiss_path = os.path.join(project_root, "models", "faiss_movies.index")
                
                with open(df_path, "rb") as f:
                    cls.df = pickle.load(f)
                cls.df["movie_title_clean"] = cls.df["movie_title"].str.strip().str.lower()
                if not hasattr(cls, "lookup_dict"):
                    cls.lookup_dict = dict(zip(cls.df["movie_title_clean"], cls.df.index))

                if cls.svd is None:
                    with open(svd_path, "rb") as f:
                        cls.svd = pickle.load(f) 
                    
                if cls.faiss_index is None:
                    cls.faiss_index = faiss.read_index(faiss_path)  

                logging.info(f"FAISS Models Loaded Successfully from {project_root}/models/")
            except FileNotFoundError as e:
                logging.error(f"FAISS Models Loading Failed: {e}")
                raise e
        return cls.df, cls.svd, cls.faiss_index

    @classmethod
    def get_vectorizer(cls):
        if cls.vectorizer is None:
            try:
                project_root = cls._get_project_root()
                vectorizer_path = os.path.join(project_root, "models", "transformed.pkl")
                
                with open(vectorizer_path, "rb") as f:
                    cls.vectorizer = pickle.load(f)
                logging.info(f"Vectorizer Loaded Successfully!")
            except FileNotFoundError as e:
                logging.error(f"Vectorizer Loading Failed: {e}")
                raise e
        return cls.vectorizer

    @classmethod
    def _extract_features_from_tmdb(cls, movie_id):
        from services.tmdb_service import TMDBService
        
        # Get movie details and credits
        details = TMDBService.get_movie_details(movie_id)
        credits = TMDBService.get_movie_credits(movie_id)
        
        # Extract director
        director = ""
        for crew in credits.get('crew', []):
            if crew['job'] == 'Director':
                director = crew['name']
                break
        
        # Extract top 3 actors
        actors = []
        for i, cast in enumerate(credits.get('cast', [])):
            if i < 3:  
                actors.append(cast['name'])
            else:
                break
        
        # Pad with empty strings if less than 3 actors
        while len(actors) < 3:
            actors.append("")
        
        # Extract genres
        genres = [g['name'] for g in details.get('genres', [])]
        feature_parts = [
            director,
            actors[0],
            actors[1],
            actors[2],
            " ".join(genres)
        ]
        
        return " ".join(feature_parts)

    @classmethod
    def get_homepage_recommendations(cls, count=20):
        df, _, _ = cls.get_df_engine()
        fallback_movies = (
            df["movie_title"]
            .dropna()
            .drop_duplicates()
            .head(count)
            .tolist()
        )

        if not TMDBService.is_configured():
            logging.warning(
                "TMDB_API_KEY is not configured; showing movies from the local catalog."
            )
            return fallback_movies
        
        # Get movies with live TMDB data
        candidate_count = count * 2
        all_movies = df['movie_title'].head(candidate_count).tolist()
        enriched_movies = []
        
        for title in all_movies[:20]:  # Limit to first 20 for performance
            enriched = EnrichedMovie(title)
            if enriched.error:
                break
            if enriched.vote_average or enriched.popularity:
                enriched_movies.append(enriched)
        
        # Sort for best-rated
        best_rated = sorted(
            enriched_movies, 
            key=lambda m: m.vote_average or 0, 
            reverse=True
        )[:count//2]  # Top 10 best-rated
        
        # Sort for most popular
        most_popular = sorted(
            enriched_movies, 
            key=lambda m: m.popularity or 0, 
            reverse=True
        )[:count//2]  # Top 10 most popular
        
        # Combine and remove duplicates
        combined = list({m.title: m for m in best_rated + most_popular}.values())
        
        # Fill with the best of the remaining
        if len(combined) < count:
            remaining = [m for m in enriched_movies if m not in combined]
            remaining_sorted = sorted(
                remaining,
                key=lambda m: (m.vote_average or 0) * 0.6 + (m.popularity or 0) * 0.4,
                reverse=True
            )
            combined.extend(remaining_sorted[:count - len(combined)])
        
        if not combined:
            logging.warning(
                "TMDB returned no homepage movie data; showing movies from the local catalog."
            )
            return fallback_movies

        return [m.title for m in combined[:count]]

    @classmethod
    def get_homepage_posters(cls, movie_titles):
        if not TMDBService.is_configured():
            return ["" for _ in movie_titles]

        posters = []
        for title in movie_titles:
            try:
                # Search for the movie on TMDB
                result = TMDBService.search_movie(title)
                if result.get("error"):
                    logging.warning(
                        "Could not load TMDB posters; using local title cards."
                    )
                    return posters + ["" for _ in movie_titles[len(posters):]]
                if result.get('results') and len(result['results']) > 0:
                    poster_path = result['results'][0].get('poster_path')
                    if poster_path:
                        posters.append(f"https://image.tmdb.org/t/p/w500{poster_path}")
                    else:
                        posters.append("")
                else:
                    posters.append("")
            except Exception as e:
                logging.error(f"Error fetching poster for {title}: {e}")
                posters.append("")
        
        return posters

    @classmethod
    def _build_preference_profile(cls, movie_feedback, vectorizer, svd):
        feedback = [
            item
            for item in (movie_feedback or [])
            if item.preference in (-1, 1) and item.feature_text.strip()
        ]
        if not feedback:
            return None

        feature_texts = [item.feature_text for item in feedback]
        feedback_vectors = svd.transform(
            vectorizer.transform(feature_texts)
        ).astype("float32")
        faiss.normalize_L2(feedback_vectors)

        liked_vectors = [
            feedback_vectors[index]
            for index, item in enumerate(feedback)
            if item.preference == 1
        ]
        disliked_vectors = [
            feedback_vectors[index]
            for index, item in enumerate(feedback)
            if item.preference == -1
        ]

        if liked_vectors and disliked_vectors:
            profile = np.mean(liked_vectors, axis=0) - np.mean(
                disliked_vectors, axis=0
            )
        elif liked_vectors:
            profile = np.mean(liked_vectors, axis=0)
        else:
            profile = -np.mean(disliked_vectors, axis=0)

        profile = np.asarray(profile, dtype="float32")
        magnitude = np.linalg.norm(profile)
        if magnitude == 0:
            return None
        return profile / magnitude

    @classmethod
    def recommend_movies(cls, movie_title, movie_feedback=None):
        df, svd, faiss_index = cls.get_df_engine()
        vectorizer = cls.get_vectorizer()

        m_clean = movie_title.strip().lower()
        lookup_dict = dict(zip(df["movie_title_clean"], df.index))
        query_index = None
        # CASE 1: New movie 
        if m_clean in lookup_dict:
            query_index = lookup_dict[m_clean]
            movies_text = df.loc[query_index, "combined_columns"]
            tfidf_vec = vectorizer.transform([movies_text])
            query_vector = svd.transform(tfidf_vec).astype("float32")
            faiss.normalize_L2(query_vector)
        else:
            search_result = TMDBService.search_movie(movie_title)
            if not search_result.get('results'):
                return "Sorry! The movie you requested for is not available."

            movie_id = search_result['results'][0]['id']
            movie_text = cls._extract_features_from_tmdb(movie_id)
            tfidf_vec = vectorizer.transform([movie_text])
            query_vector = svd.transform(tfidf_vec).astype("float32")
            faiss.normalize_L2(query_vector)

        preference_profile = cls._build_preference_profile(
            movie_feedback, vectorizer, svd
        )
        candidate_count = 13
        if preference_profile is not None:
            candidate_count = min(100, faiss_index.ntotal)

        distances, indices = faiss_index.search(
            query_vector, k=candidate_count
        )
        candidate_indices = [
            int(index)
            for index in indices[0]
            if index >= 0 and index != query_index
        ]
        if preference_profile is None:
            return [df["movie_title"].iloc[index] for index in candidate_indices][
                :12
            ]

        candidate_texts = df.iloc[candidate_indices]["combined_columns"].tolist()
        candidate_vectors = svd.transform(
            vectorizer.transform(candidate_texts)
        ).astype("float32")
        faiss.normalize_L2(candidate_vectors)
        query_scores = candidate_vectors @ query_vector[0]
        preference_scores = candidate_vectors @ preference_profile
        combined_scores = 0.5 * query_scores + 0.5 * preference_scores
        ranked_positions = sorted(
            range(len(candidate_indices)),
            key=lambda position: (-combined_scores[position], position),
        )
        return [
            df["movie_title"].iloc[candidate_indices[position]]
            for position in ranked_positions[:12]
        ]

    
    @classmethod
    def convert_to_list(cls, my_list):
        try:
            if isinstance(my_list, list):
                return my_list
            if not my_list or my_list == "[]":
                return []
            my_list = my_list.split('","')
            if len(my_list) > 0:
                my_list[0] = my_list[0].replace('["','')
                my_list[-1] = my_list[-1].replace('"]', '')
            return my_list
        except Exception as e:
            logging.info(f"Error Converting List: {e}")
            return []

        
    @classmethod
    def get_suggestions(cls):
        df, _, _ = cls.get_df_engine()
        return list(df["movie_title"].str.capitalize())


    @classmethod
    def get_trailer(cls, imdb_id):
        api_key = os.environ.get("TMDB_API_KEY")
        if not api_key:
            logging.error("TMDB_API_KEY not found in environment variables!")
            return None
        try:
            find_url = f"https://api.themoviedb.org/3/find/{imdb_id}?api_key={api_key}&external_source=imdb_id"
            response = requests.get(find_url)
            data = response.json()
            if not data.get("movie_results"):
                return None
            tmdb_id = data['movie_results'][0]['id']
            video_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/videos?api_key={api_key}"
            video_response = requests.get(video_url)
            video_data = video_response.json()
            results = video_data.get('results', [])
            youtube_videos = [v for v in results if v['site'] == 'YouTube']
            if not youtube_videos:
                return None
            trailers = [v for v in youtube_videos if v['type'] == 'Trailer']
            if trailers:
                return trailers[0]['key']
            teasers = [v for v in youtube_videos if v['type'] == 'Teaser']
            if teasers:
                return teasers[0]['key']
            return youtube_videos[0]['key']
        except Exception as e:
            logging.info(f"Error fetching trailer: {e}")
            return None

class EnrichedMovie:
    def __init__(self, title, static_data=None):
        self.title = title
        self.static_data = static_data or {}
        self.live_data = None
        self.vote_average = None
        self.popularity = None
        self.error = None
        self._fetch_live_data()
    
    def _fetch_live_data(self):
        try:
            from services.tmdb_service import TMDBService
            result = TMDBService.search_movie(self.title)
            if result.get("error"):
                self.error = result["error"]
                return
            if result.get('results') and len(result['results']) > 0:
                movie_data = result['results'][0]
                self.live_data = movie_data
                self.vote_average = movie_data.get('vote_average', 0)
                self.popularity = movie_data.get('popularity', 0)
                
                # Get detailed info for more signals
                details = TMDBService.get_movie_details(movie_data['id'])
                if details:
                    self.vote_count = details.get('vote_count', 0)
        except Exception as e:
            logging.error(f"Error fetching live data for {self.title}: {e}")
    
    def get_quality_score(self, base_score=1.0):
        """Combine static quality with live popularity"""
        score = base_score
        
        # Live popularity signals
        if self.popularity:
            # Normalize popularity (TMDB popularity can be 0-1000+)
            score += min(self.popularity / 100, 5)  # Cap at +5
        
        if self.vote_average:
            # vote_average is 0-10
            score += self.vote_average / 2  # Convert to 0-5 scale
        
        if hasattr(self, 'vote_count') and self.vote_count:
            # More votes = more reliable
            score += min(self.vote_count / 1000, 2)  # Cap at +2
        
        return score

if __name__ == "__main__":
    MovieEngine().get_df_engine()
