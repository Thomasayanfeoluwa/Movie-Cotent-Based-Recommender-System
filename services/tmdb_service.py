import requests
import os
import time
import logging

class TMDBService:
    BASE_URL = "https://api.themoviedb.org/3"
    REQUEST_TIMEOUT = 8

    _cache = {}
    _cache_ttl = 86400  # 24 hours

    @classmethod
    def is_configured(cls):
        return bool(os.environ.get("TMDB_API_KEY", "").strip())

    @classmethod
    def _missing_api_key(cls):
        return {"error": "TMDB_API_KEY is not configured"}

    @classmethod
    def _request_json(cls, path, params, operation):
        try:
            response = requests.get(
                f"{cls.BASE_URL}{path}",
                params=params,
                timeout=cls.REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError:
            status_code = response.status_code
            logging.error(
                "TMDB %s request failed with HTTP %s",
                operation,
                status_code,
            )
            if status_code in (401, 403):
                return {
                    "error": (
                        "TMDB rejected the API key. Verify that TMDB_API_KEY is "
                        "a valid API v3 key, not a v4 read access token."
                    )
                }
            if status_code == 429:
                return {"error": "TMDB rate limit reached. Try again shortly."}
            return {"error": f"TMDB returned HTTP {status_code}"}
        except requests.Timeout:
            logging.error("TMDB %s request timed out", operation)
            return {"error": "TMDB request timed out. Try again shortly."}
        except requests.RequestException as error:
            logging.error(
                "TMDB %s request failed (%s)",
                operation,
                type(error).__name__,
            )
            return {"error": "Could not connect to TMDB. Check your connection."}
        except ValueError:
            logging.error("TMDB %s returned invalid JSON", operation)
            return {"error": "TMDB returned an invalid response"}
    
    @classmethod
    def get_movie_with_ratings(cls, title):
        cache_key = f"enriched_{title}"
        
        # Use existing cache system
        cached = cls._get_cached(cache_key)
        if cached:
            return cached
        
        # Fetch fresh data
        result = cls.search_movie(title)
        if result.get('results'):
            movie_id = result['results'][0]['id']
            details = cls.get_movie_details(movie_id)
            enriched_data = {
                'vote_average': details.get('vote_average'),
                'popularity': details.get('popularity'),
                'vote_count': details.get('vote_count')
            }
            # Use existing cache setter
            cls._set_cache(cache_key, enriched_data)
            return enriched_data
        return None

    @classmethod
    def _get_cached(cls, key):
        if key in cls._cache:
            data, timestamp = cls._cache[key]
            # Check if cache is still valid (less than 24 hours old)
            if time.time() - timestamp < cls._cache_ttl:
                logging.info(f"Cache hit for: {key}")
                return data
            else:
                logging.info(f"Cache expired for: {key}")
        return None
    
    @classmethod
    def _set_cache(cls, key, data):
        cls._cache[key] = (data, time.time())
        logging.info(f"Cached data for: {key}")
    
    @classmethod
    def search_movie(cls, query):
        api_key = os.environ.get("TMDB_API_KEY", "").strip()
        if not api_key:
            return cls._missing_api_key()

        cache_key = f"search_{query}"
        cached = cls._get_cached(cache_key)
        if cached:
            return cached
        result = cls._request_json(
            "/search/movie",
            {"api_key": api_key, "query": query},
            "movie search",
        )
        if "error" not in result:
            cls._set_cache(cache_key, result)
        return result
    
    @classmethod
    def get_movie_details(cls, movie_id):
        api_key = os.environ.get("TMDB_API_KEY", "").strip()
        if not api_key:
            return cls._missing_api_key()

        cache_key = f"details_{movie_id}"
        cached = cls._get_cached(cache_key)
        if cached:
            return cached
        result = cls._request_json(
            f"/movie/{movie_id}",
            {"api_key": api_key},
            "movie details",
        )
        if "error" not in result:
            cls._set_cache(cache_key, result)
        return result
    
    @classmethod
    def get_movie_credits(cls, movie_id):
        api_key = os.environ.get("TMDB_API_KEY", "").strip()
        if not api_key:
            return cls._missing_api_key()

        cache_key = f"credits_{movie_id}"
        cached = cls._get_cached(cache_key)
        if cached:
            return cached
        result = cls._request_json(
            f"/movie/{movie_id}/credits",
            {"api_key": api_key},
            "movie credits",
        )
        if "error" not in result:
            cls._set_cache(cache_key, result)
        return result
    
    @classmethod
    def get_person_details(cls, person_id):
        api_key = os.environ.get("TMDB_API_KEY", "").strip()
        if not api_key:
            return cls._missing_api_key()

        cache_key = f"person_{person_id}"
        cached = cls._get_cached(cache_key)
        if cached:
            return cached
        result = cls._request_json(
            f"/person/{person_id}",
            {"api_key": api_key},
            "person details",
        )
        if "error" not in result:
            cls._set_cache(cache_key, result)
        return result
