import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import urlparse

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from requests import HTTPError

from services.tmdb_service import TMDBService

# Keep tests isolated from any configured production database.
os.environ["DATABASE_URL"] = "sqlite:///tests/test_baseline.db"
os.environ["RATELIMIT_STORAGE_URI"] = "memory://"

from app import app
from services.movie_engine import MovieEngine


class BaselineRouteTests(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = True
        self.client = app.test_client()

    def test_sqlite_test_database_does_not_use_postgresql_pool_options(self):
        self.assertTrue(app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite:"))
        self.assertNotIn("pool_size", app.config.get("SQLALCHEMY_ENGINE_OPTIONS", {}))

    def get_csrf_token(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.get_data(as_text=True), "html.parser")
        token_meta = soup.select_one('meta[name="csrf-token"]')
        self.assertIsNotNone(token_meta)
        return token_meta["content"]

    def sign_in_test_session(self):
        with self.client.session_transaction() as session:
            session["user_id"] = 123
            session["username"] = "baseline-user"

    def get_recommend_form_data(self):
        return {
            "title": "Example Movie",
            "cast_ids": "[]",
            "cast_names": "[]",
            "cast_chars": "[]",
            "cast_bdays": "[]",
            "cast_bios": "[]",
            "cast_places": "[]",
            "cast_profiles": "[]",
            "imdb_id": "tt1234567",
            "tmdb_movie_id": "550",
            "poster": "",
            "genres": "",
            "overview": "",
            "rating": "7",
            "vote_count": "10",
            "release_date": "",
            "runtime": "0",
            "status": "Released",
            "rec_movies": "[]",
            "rec_posters": "[]",
        }

    def test_login_page_renders_both_csrf_protected_forms(self):
        token = self.get_csrf_token()
        self.assertTrue(token)
        response = self.client.get("/login")
        page = response.get_data(as_text=True)
        self.assertIn('action="/signin"', page)
        self.assertIn('action="/signup"', page)
        self.assertIn('id="signin-tab"', page)
        self.assertIn('id="signup-tab"', page)
        self.assertIn('href="/static/login.css"', page)
        self.assertIn('src="/static/login.js"', page)
        self.assertIn('placeholder="Enter your username"', page)
        self.assertIn('data-auth-panel="signup"', page)
        self.assertIn(' hidden>', page)
        self.assertNotIn('href="/static/style.css"', page)
        self.assertNotIn('id="chatbot-launcher"', page)

    def test_signin_sets_session_for_valid_credentials(self):
        token = self.get_csrf_token()
        user = type(
            "TestUser",
            (),
            {"id": 123, "username": "baseline-user", "password": "hashed"},
        )()

        with app.app_context():
            with (
                patch("app.User.query") as user_query,
                patch("app.check_password_hash", return_value=True),
            ):
                user_query.filter_by.return_value.first.return_value = user
                response = self.client.post(
                    "/signin",
                    data={
                        "signinUsername": "baseline-user",
                        "signinPassword": "secret",
                    },
                    headers={"X-CSRFToken": token},
                )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/home")
        with self.client.session_transaction() as session:
            self.assertEqual(session["user_id"], 123)
            self.assertEqual(session["username"], "baseline-user")

    def test_anonymous_users_are_redirected_to_login(self):
        root_response = self.client.get("/")
        self.assertEqual(root_response.status_code, 302)
        self.assertEqual(urlparse(root_response.location).path, "/login")

        response = self.client.get("/home")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/login")

        api_response = self.client.get("/api/tmdb/search?query=Movie")
        self.assertEqual(api_response.status_code, 401)
        self.assertEqual(
            api_response.get_json(),
            {"error": "Authentication required"},
        )
        for asset in (
            "style.css",
            "streaming.css",
            "login.css",
            "login.js",
        ):
            with self.subTest(asset=asset):
                static_response = self.client.get(f"/static/{asset}")
                self.assertEqual(static_response.status_code, 200)
                static_response.close()

    def test_authenticated_user_can_open_home_and_get_recommendations(self):
        token = self.get_csrf_token()
        expected = ["Movie One", "Movie Two"]

        self.sign_in_test_session()
        with app.app_context():
            with (
                patch.object(MovieEngine, "recommend_movies", return_value=expected),
                patch.object(MovieEngine, "get_suggestions", return_value=[]),
                patch.object(
                    MovieEngine,
                    "get_homepage_recommendations",
                    return_value=["Featured Movie"],
                ),
                patch.object(
                    MovieEngine,
                    "get_homepage_posters",
                    return_value=["https://image.tmdb.org/t/p/w500/featured.jpg"],
                ),
                patch("app.MovieFeedback.query") as movie_feedback_query,
                patch("app.db.session.add"),
                patch("app.db.session.commit"),
            ):
                movie_feedback_query.filter_by.return_value.all.return_value = []
                home_response = self.client.get("/home")
                response = self.client.post(
                    "/similarity",
                    data={"name": "Example Movie"},
                    headers={"X-CSRFToken": token},
                )

        self.assertEqual(home_response.status_code, 200)
        self.assertIn(b'href="/static/streaming.css"', home_response.data)
        self.assertIn(b'class="stream-hero"', home_response.data)
        self.assertIn(b'data-movie-title="Featured Movie"', home_response.data)
        self.assertIn(b'class="movie-content stream-rail"', home_response.data)
        self.assertNotIn(b"chatbot", home_response.data.lower())
        self.assertNotIn(b"puter", home_response.data.lower())
        self.assertEqual(self.client.get("/static/chatbot.js").status_code, 404)
        self.assertEqual(self.client.get("/static/chatbot.css").status_code, 404)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"chatbot", response.data.lower())
        self.assertEqual(response.get_data(as_text=True), "Movie One---Movie Two")

    def test_homepage_uses_local_catalogue_without_tmdb_configuration(self):
        catalog = pd.DataFrame(
            {"movie_title": ["Local Movie One", "Local Movie Two", None]}
        )
        with (
            patch.object(MovieEngine, "get_df_engine", return_value=(catalog, None, None)),
            patch.object(TMDBService, "is_configured", return_value=False),
        ):
            titles = MovieEngine.get_homepage_recommendations(2)
            posters = MovieEngine.get_homepage_posters(titles)

        self.assertEqual(titles, ["Local Movie One", "Local Movie Two"])
        self.assertEqual(posters, ["", ""])

    def test_homepage_renders_local_catalogue_without_poster_images(self):
        self.sign_in_test_session()
        with (
            patch.object(MovieEngine, "get_suggestions", return_value=[]),
            patch.object(
                MovieEngine,
                "get_homepage_recommendations",
                return_value=["Local Movie One"],
            ),
            patch.object(MovieEngine, "get_homepage_posters", return_value=[""]),
            patch.object(TMDBService, "is_configured", return_value=False),
        ):
            response = self.client.get("/home")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Local Movie One", response.data)
        self.assertIn(b'class="stream-poster-fallback"', response.data)
        self.assertIn(b"Showing movie titles from the local catalogue.", response.data)

    def test_tmdb_search_reports_missing_api_key_without_requesting_tmdb(self):
        self.sign_in_test_session()
        with (
            patch.dict(os.environ, {"TMDB_API_KEY": ""}),
            patch("services.tmdb_service.requests.get") as get_request,
        ):
            response = self.client.get("/api/tmdb/search?query=Movie")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.get_json(),
            {"error": "TMDB_API_KEY is not configured"},
        )
        get_request.assert_not_called()

    def test_tmdb_search_explains_rejected_api_key_without_exposing_it(self):
        self.sign_in_test_session()
        upstream_response = SimpleNamespace(status_code=401)
        http_error = HTTPError(response=upstream_response)

        with (
            patch.dict(os.environ, {"TMDB_API_KEY": "test-key-not-for-logs"}),
            patch("services.tmdb_service.requests.get") as get_request,
        ):
            get_request.return_value.status_code = 401
            get_request.return_value.raise_for_status.side_effect = http_error
            response = self.client.get("/api/tmdb/search?query=Movie")

        self.assertEqual(response.status_code, 502)
        self.assertEqual(
            response.get_json(),
            {
                "error": (
                    "TMDB rejected the API key. Verify that TMDB_API_KEY is "
                    "a valid API v3 key, not a v4 read access token."
                )
            },
        )
        self.assertNotIn(b"test-key-not-for-logs", response.data)

    def test_anonymous_review_submission_requires_login(self):
        token = self.get_csrf_token()

        response = self.client.post(
            "/add_review",
            data={
                "movie_title": "Example Movie",
                "review_content": "Example review",
            },
            headers={"X-CSRFToken": token},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(urlparse(response.location).path, "/login")

    def test_logout_requires_post_and_clears_session(self):
        token = self.get_csrf_token()

        self.sign_in_test_session()

        get_response = self.client.get("/logout")
        self.assertEqual(get_response.status_code, 405)

        post_response = self.client.post(
            "/logout",
            headers={"X-CSRFToken": token},
        )
        self.assertEqual(post_response.status_code, 302)

        with self.client.session_transaction() as session:
            self.assertNotIn("user_id", session)
            self.assertNotIn("username", session)

    def test_state_changing_routes_reject_posts_without_csrf_token(self):
        requests = [
            (
                "/signup",
                {"username": "test", "email": "test@example.com", "password": "test"},
            ),
            ("/signin", {"signinUsername": "test", "signinPassword": "test"}),
            ("/similarity", {"name": "Example Movie"}),
            ("/recommend", {}),
            (
                "/add_review",
                {"movie_title": "Example Movie", "review_content": "Review"},
            ),
        ]

        for path, data in requests:
            with self.subTest(path=path):
                response = self.client.post(path, data=data)
                self.assertEqual(response.status_code, 400)

    def test_tmdb_search_rejects_empty_or_oversized_query(self):
        self.sign_in_test_session()
        with patch.object(TMDBService, "search_movie") as search_movie:
            empty_response = self.client.get("/api/tmdb/search?query=")
            oversized_response = self.client.get(
                "/api/tmdb/search?query=" + ("x" * 201)
            )

        self.assertEqual(empty_response.status_code, 400)
        self.assertEqual(oversized_response.status_code, 400)
        search_movie.assert_not_called()

    def test_tmdb_proxy_routes_share_rate_limit(self):
        self.sign_in_test_session()
        test_address = {"REMOTE_ADDR": "192.0.2.10"}

        with (
            patch.object(TMDBService, "search_movie", return_value={"results": []}),
            patch.object(TMDBService, "get_movie_details", return_value={}),
        ):
            for _ in range(120):
                response = self.client.get(
                    "/api/tmdb/search?query=Movie",
                    environ_base=test_address,
                )
                self.assertEqual(response.status_code, 200)

            response = self.client.get(
                "/api/tmdb/movie/1",
                environ_base=test_address,
            )

        self.assertEqual(response.status_code, 429)
        self.assertEqual(
            response.get_json(),
            {"error": "Too many requests. Please try again later."},
        )

    def test_recommend_error_does_not_expose_exception_details(self):
        token = self.get_csrf_token()
        self.sign_in_test_session()

        response = self.client.post(
            "/recommend",
            headers={"X-CSRFToken": token},
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.get_data(as_text=True),
            "Unable to load movie details. Please try again.",
        )

    def test_recommendation_shows_saved_reviews_without_imdb_fetch(self):
        token = self.get_csrf_token()
        self.sign_in_test_session()

        with app.app_context():
            with (
                patch("app.Review.query") as review_query,
                patch("app.MovieFeedback.query") as movie_feedback_query,
                patch("app.MovieEngine.get_trailer", return_value=None),
                patch("requests.get") as get_request,
            ):
                review_query.filter.return_value.all.return_value = [
                    type(
                        "SavedReview",
                        (),
                        {
                            "content": "A review saved by an app user",
                            "sentiment": "Good",
                        },
                    )()
                ]
                movie_feedback_query.filter_by.return_value.first.return_value = None
                response = self.client.post(
                    "/recommend",
                    data=self.get_recommend_form_data(),
                    headers={"X-CSRFToken": token},
                )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"A review saved by an app user", response.data)
        self.assertIn(b'class="stream-detail"', response.data)
        self.assertIn(b'class="movie-feedback"', response.data)
        self.assertNotIn(b'id="chatbot-launcher"', response.data)
        get_request.assert_not_called()

    def test_recommendation_renders_when_no_reviews_are_saved(self):
        token = self.get_csrf_token()
        self.sign_in_test_session()
        form_data = self.get_recommend_form_data()
        form_data.update(
            {
                "cast_ids": "[123, 456]",
                "cast_names": '["Example Actor","Second Actor"]',
                "cast_chars": '["Lead","Detective"]',
                "cast_bdays": '["Jan 1 1990","Feb 2 1985"]',
                "cast_bios": '["First biography","Second biography"]',
                "cast_places": '["London","Toronto"]',
                "cast_profiles": '["actor-one.jpg","actor-two.jpg"]',
                "rec_movies": '["Pirates of the Caribbean: The Curse of the Black Pearl"]',
                "rec_posters": '["pirates.jpg"]',
            }
        )

        with app.app_context():
            with (
                patch("app.Review.query") as review_query,
                patch("app.MovieFeedback.query") as movie_feedback_query,
                patch("app.MovieEngine.get_trailer", return_value="trailer-key"),
                patch("requests.get") as get_request,
            ):
                review_query.filter.return_value.all.return_value = []
                movie_feedback_query.filter_by.return_value.first.return_value = None
                responses = [
                    self.client.post(
                        "/recommend",
                        data=form_data,
                        headers={"X-CSRFToken": token},
                    )
                    for _ in range(2)
                ]

        for response in responses:
            page = response.get_data(as_text=True).lower()
            self.assertEqual(response.status_code, 200)
            self.assertIn("no reviews yet for this movie!", page)
            self.assertIn('class="stream-detail-title', page)
            self.assertIn("play-trailer-button", page)
            self.assertIn('data-trailer-key="trailer-key"', page)
            self.assertIn('class="poster-trailer-trigger"', page)
            self.assertIn('aria-label="Play trailer for Example Movie"', page)
            self.assertIn('class="cast-character"', page)
            self.assertIn("character: lead", page)
            self.assertIn('class="modal fade cast-profile-modal"', page)
            self.assertIn('class="cast-profile-info"', page)
            self.assertIn('class="cast-profile-biography"', page)
            self.assertIn("pirates of the caribbean: the curse of the black pearl", page)
            self.assertNotIn("<!doctype", page)
            self.assertNotIn("<html", page)
            self.assertNotIn("<head", page)
            self.assertNotIn("<body", page)
            self.assertNotIn("<script", page)
            self.assertNotIn('class="results"', page)
            self.assertNotIn('id="chatbot-launcher"', page)
        get_request.assert_not_called()

    def test_movie_feedback_is_saved_and_can_be_changed(self):
        token = self.get_csrf_token()
        self.sign_in_test_session()

        with app.app_context():
            with (
                patch("app.MovieFeedback.query") as feedback_query,
                patch(
                    "app.TMDBService.get_movie_details",
                    return_value={"title": "Movie"},
                ),
                patch(
                    "app.TMDBService.get_movie_credits",
                    return_value={"crew": [], "cast": []},
                ),
                patch.object(
                    MovieEngine,
                    "_extract_features_from_tmdb",
                    return_value="Director Actor Genre",
                ),
                patch("app.db.session.add") as add_feedback,
                patch("app.db.session.commit") as commit,
            ):
                feedback_query.filter_by.return_value.first.return_value = None
                response = self.client.post(
                    "/api/movie-feedback",
                    data={"tmdb_movie_id": "550", "preference": "1"},
                    headers={"X-CSRFToken": token},
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["preference"], 1)
        saved_feedback = add_feedback.call_args.args[0]
        self.assertEqual(saved_feedback.tmdb_movie_id, 550)
        self.assertEqual(saved_feedback.feature_text, "Director Actor Genre")
        commit.assert_called_once()

        existing_feedback = SimpleNamespace(
            movie_title="Movie",
            preference=1,
        )
        with app.app_context():
            with (
                patch("app.MovieFeedback.query") as feedback_query,
                patch("app.TMDBService.get_movie_details") as get_details,
                patch("app.db.session.commit") as commit,
            ):
                feedback_query.filter_by.return_value.first.return_value = existing_feedback
                response = self.client.post(
                    "/api/movie-feedback",
                    data={"tmdb_movie_id": "550", "preference": "-1"},
                    headers={"X-CSRFToken": token},
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(existing_feedback.preference, -1)
        get_details.assert_not_called()
        commit.assert_called_once()

    def test_movie_feedback_is_not_saved_when_tmdb_features_are_unavailable(self):
        token = self.get_csrf_token()
        self.sign_in_test_session()

        with app.app_context():
            with (
                patch("app.MovieFeedback.query") as feedback_query,
                patch(
                    "app.TMDBService.get_movie_details",
                    return_value={"title": "Movie"},
                ),
                patch(
                    "app.TMDBService.get_movie_credits",
                    return_value={"error": "TMDB unavailable"},
                ),
                patch("app.db.session.add") as add_feedback,
            ):
                feedback_query.filter_by.return_value.first.return_value = None
                response = self.client.post(
                    "/api/movie-feedback",
                    data={"tmdb_movie_id": "550", "preference": "1"},
                    headers={"X-CSRFToken": token},
                )

        self.assertEqual(response.status_code, 502)
        add_feedback.assert_not_called()

    def test_movie_feedback_rejects_invalid_values_and_anonymous_users(self):
        token = self.get_csrf_token()
        invalid_response = self.client.post(
            "/api/movie-feedback",
            data={"tmdb_movie_id": "0", "preference": "5"},
            headers={"X-CSRFToken": token},
        )
        self.assertEqual(invalid_response.status_code, 401)

        self.sign_in_test_session()
        invalid_response = self.client.post(
            "/api/movie-feedback",
            data={"tmdb_movie_id": "550", "preference": "5"},
            headers={"X-CSRFToken": token},
        )
        self.assertEqual(invalid_response.status_code, 400)
        self.assertEqual(
            invalid_response.get_json(),
            {"error": "preference must be 1 (like) or -1 (dislike)."},
        )

    def test_personalization_reranks_candidates_and_keeps_cold_start_order(self):
        class FakeVectorizer:
            vectors = {
                "source": [1.0, 0.0],
                "query-near": [0.95, 0.31],
                "like-near": [0.5, 0.866],
                "other": [0.8, -0.6],
                "liked": [0.0, 1.0],
            }

            def transform(self, texts):
                return np.asarray(
                    [self.vectors[text] for text in texts],
                    dtype="float32",
                )

        class FakeSvd:
            def transform(self, vectors):
                return vectors

        class FakeFaissIndex:
            ntotal = 4

            def search(self, query_vector, k):
                indices = np.full((1, k), -1, dtype="int64")
                distances = np.zeros((1, k), dtype="float32")
                count = min(k, self.ntotal)
                indices[0, :count] = np.arange(count)
                distances[0, :count] = [1.0, 0.9, 0.8, 0.7][:count]
                return distances, indices

        df = pd.DataFrame(
            {
                "movie_title": ["Source", "Query Near", "Like Near", "Other"],
                "movie_title_clean": ["source", "query near", "like near", "other"],
                "combined_columns": [
                    "source",
                    "query-near",
                    "like-near",
                    "other",
                ],
            }
        )
        feedback = [SimpleNamespace(feature_text="liked", preference=1)]

        with (
            patch.object(
                MovieEngine,
                "get_df_engine",
                return_value=(df, FakeSvd(), FakeFaissIndex()),
            ),
            patch.object(MovieEngine, "get_vectorizer", return_value=FakeVectorizer()),
        ):
            cold_start = MovieEngine.recommend_movies("Source")
            personalized = MovieEngine.recommend_movies("Source", feedback)

        self.assertEqual(cold_start[0], "Query Near")
        self.assertEqual(personalized[0], "Like Near")


if __name__ == "__main__":
    unittest.main()
