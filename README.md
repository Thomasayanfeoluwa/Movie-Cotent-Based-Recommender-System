# 🎬 Movie Recommendation System with Trailer and Sentiment Analysis

This project is a Flask movie-discovery application with content-based recommendations, TMDB movie metadata and trailers, user accounts, and sentiment analysis for reviews submitted through the application. Users must sign in or create an account before accessing movie discovery and recommendations. Signed-in users can like or dislike movies to personalize future content-based recommendations.

## 💼 System Overview

The recommender uses **content-based filtering (CBF)**. It compares movie attributes such as director, cast, and genres rather than learning from interactions across users as collaborative filtering does. Explicit likes and dislikes create a per-user content profile that adjusts the ranking of similar candidates. Review-text sentiment is not used as a preference signal, and users without explicit feedback retain the existing ranking.

https://github.com/user-attachments/assets/64f280a4-f5ae-40dd-a605-2b997cfaf889


<p align="center">
  <img width="150" height="150" alt="TrailerMatch - Watch Trailers + Smart Recommendations" src="https://github.com/user-attachments/assets/a8606912-3408-4cbe-9f34-9b872f0d8319" />
</p>

## 🎬 Demo

**Live demo:** [Open the Render app](https://movie-recommender-mu4e.onrender.com/home). Checked on November 5, 2026: `/home` loads successfully. The currently deployed revision does not yet include the local login page (`/login` returns 404) or personalized feedback changes; these require deployment and the database migration before they are live.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/Flask-3.1.3-black?style=for-the-badge&logo=flask">
</p>


*Search movies, watch available trailers, get content-based recommendations, and view sentiment analysis for reviews submitted through the app.*

A full-stack movie recommendation application built with **Flask**, **PostgreSQL**, and machine-learning components. The recommender uses **TF-IDF**, **TruncatedSVD**, and a **FAISS exact inner-product index** over normalized movie vectors. The app also classifies the sentiment of submitted reviews.

---

## ⭐ Support the Project

If you find this project useful or interesting, please consider:

- **Starring** the repository ⭐ – it helps others discover it
- **Watching** for updates 👀 – stay informed about new features
- **Forking** to experiment 🍴 – try it out for yourself
- **Sharing** with friends who love movies 🎬

Your support motivates me to keep improving and adding new features!

<p align="center">
  <a href="https://github.com/Thomasayanfeoluwa/Movie-Cotent-Based-Recommender-System/stargazers">
    <img src="https://img.shields.io/github/stars/Thomasayanfeoluwa/Movie-Cotent-Based-Recommender-System?style=social">
  </a>
  <a href="https://github.com/Thomasayanfeoluwa/Movie-Cotent-Based-Recommender-System/network/members">
    <img src="https://img.shields.io/github/forks/Thomasayanfeoluwa/Movie-Cotent-Based-Recommender-System?style=social">
  </a>
  <a href="https://github.com/Thomasayanfeoluwa/Movie-Cotent-Based-Recommender-System/watchers">
    <img src="https://img.shields.io/github/watchers/Thomasayanfeoluwa/Movie-Cotent-Based-Recommender-System?style=social">
  </a>
</p>

## 🚀 Key Features & Technical Achievements

### 1. Advanced Recommendation Engine
**Achievement:** Built a content-based recommendation system using TF-IDF vectorization, TruncatedSVD, and normalized movie-feature vectors.

**Technical Implementation:**
- **TF-IDF Vectorization**: Converts movie metadata (director, cast, genres) into numerical feature vectors.
- **FAISS inner-product search**: Searches normalized vectors, making inner product equivalent to cosine similarity.
- **Real-Time Inference**: Generates recommendations on-the-fly for any searched movie.
- **Explicit preference feedback**: Stores per-user likes/dislikes by TMDB movie ID; review text and sentiment are not treated as preference signals.

When a user has saved likes or dislikes, up to 100 similar candidates are reranked using a 50/50 blend of similarity to the searched movie and similarity to the user's content-preference profile. The profile uses the existing TF-IDF vectorizer, SVD transform, and FAISS candidate index; no model retraining is required. Users with no feedback keep the original ranking.

Recommendation quality has not yet been measured against held-out relevance judgments, so no ranking-quality metrics are claimed. The planned evaluation compares baseline and personalized top-12 results on identical user/query cases, with users blindly rating the pooled results; NDCG@10 is the primary metric and Precision@10 is secondary.

### 2. Movie Feature Index
**Achievement:** Implemented movie-vector search using FAISS and TruncatedSVD dimensionality reduction.

**Technical Implementation:**
- **TruncatedSVD**: Projects TF-IDF movie features into 128 dimensions.
- **FAISS Indexing**: Uses `IndexFlatIP`, an exact inner-product index over L2-normalized vectors; this is not an approximate-nearest-neighbor index.

No benchmark results are currently documented for recommendation latency or memory use.

### 3. Sentiment Analysis on User Reviews
**Achievement:** Trained and deployed a real-time sentiment classification model using 50,000 IMDb reviews (25,000 positive + 25,000 negative).

**Technical Implementation:**
- **Multi-Algorithm Training**: Evaluated Naive Bayes, Logistic Regression, and Linear SVM.
- **Production Artifact**: The checked-in sentiment artifact is trained with `LinearSVC(C=2, max_iter=2000)`. In the notebook's recorded model comparison, Logistic Regression scored slightly higher than Linear SVM on the reported metrics.
- **Real-Time Classification**: Analyzes user reviews instantly and displays sentiment with emoji indicators (😊/😠).

The sentiment label is a model prediction about review text; it does not establish whether the author personally liked the movie.

### 4. Homepage Movie Discovery
**Achievement:** The homepage can show movies without requiring a signed-in user's history.

**Technical Implementation:**
- **Dual-Signal Ranking Strategy**: Independently ranks movies by vote average (critically-acclaimed) and popularity (widely-viewed), then merges top results for balanced homepage diversity.
- **Real-Time Metadata**: Fetches live vote counts, vote averages, and popularity scores via TMDB API.
- **Visual Enhancement**: Displays up to 20 movies with posters and trailer controls when data is available.

The homepage can show movie recommendations without user history. It uses TMDB ratings and popularity data where available.

### 5. TMDB Trailer Integration
**Achievement:** Supports YouTube trailer playback for movies when TMDB provides a suitable video.

**Technical Implementation:**
- **Video Lookup**: Queries TMDB for movie videos and selects a YouTube trailer, then a teaser, when available.
- **Player**: Uses a responsive modal with loading indicators and playback controls.

### 6. Authentication & Session Management
**Achievement:** Implemented account sign-up/sign-in, password hashing, CSRF protection, and session logout.

**Technical Implementation:**
- **Flask Session Authentication**: Uses Flask's signed session cookies.
- **Password Hashing**: Werkzeug security with generate_password_hash and check_password_hash.
- **Environment Variables**: Requires `FLASK_SECRET_KEY` and database configuration at startup.
- **CSRF Protection**: Validates tokens on state-changing requests.
- **Logout**: Clears the session through a CSRF-protected POST route.

### 7. Professional Frontend UX Design
**Achievement:** Created intuitive, responsive interface with professional-grade interactions.

**Technical Implementation:**
- **Dynamic Button States**: Buttons disable during submission to prevent duplicate requests.
- **Keyboard Shortcuts**: Enter key triggers search for power users.
- **Autocomplete Suggestions**: Real-time movie suggestions as users type.
- **Loading States**: Elegant spinners and placeholders during data fetching.
- **Mobile Responsive**: Fully adaptive design across all device sizes.
- **Movie Discovery Layout**: A responsive, streaming-service-inspired catalogue with featured movie art and horizontal poster rails. The app provides movie details and trailers, not full-film streaming.
- **Local Catalogue Fallback**: Homepage movie titles come from the local movie dataset when TMDB is unavailable. Live posters, external movie search, metadata, and trailers still require a valid `TMDB_API_KEY`.

### 8. PostgreSQL Persistence
**Achievement:** Uses PostgreSQL-compatible storage for user accounts, submitted reviews, explicit movie preferences, search history, and recommendation history.

**Technical Implementation:**
- **Normalized Schema**: Proper relationships between users, reviews, search history, and recommendations.
- **Timestamp Logging**: Review, search, and recommendation records include timestamps.
- **Data Constraints**: Usernames and email addresses are unique; required model fields are non-null.

### 9. Database Architecture
**Achievement:** The application uses **Neon PostgreSQL** as its production database and **Render** for application deployment.
The deployed Flask application connects to the Neon PostgreSQL database through the `DATABASE_URL` environment variable.

GitHub
   │
   │ Source Code
   ▼
Render
   │
   │ DATABASE_URL
   ▼
Neon PostgreSQL


### 10. TMDB API Integration with In-Memory Caching
**Achievement:** Fetches movie metadata, credits, person details, ratings, popularity, and videos through TMDB endpoints.

**Technical Implementation:**
- **24-Hour Cache**: Cached responses are held in process memory with a 24-hour time-to-live.
- **TMDB Proxy Rate Limit**: The app applies a shared 120-requests-per-minute limit to its TMDB proxy routes; production storage is configured through `RATELIMIT_STORAGE_URI`.
- **Error Handling**: TMDB service methods log request failures and return an error result.

### 12. Data Integrity & Validation Framework
**Achievement:** Implemented comprehensive validation system ensuring data consistency across the platform.

**Technical Implementation:**
- **Defensive Backend Logic**: Server-side validation for all form submissions.
- **Null Value Handling**: Graceful fallbacks for missing metadata (IMDb IDs, posters).
- **Template Data Binding**: Prevents data corruption during frontend rendering.
- **Structured Logging**: Complete error tracking for rapid debugging.

---

## 🧮 Cosine Similarity

The recommender creates TF-IDF vectors from movie metadata, projects them with TruncatedSVD, and L2-normalizes the resulting vectors. It searches those vectors with FAISS `IndexFlatIP`; because vectors are normalized, inner product gives the same ranking as cosine similarity.

If two movies have identical features → Angle = 0° → Similarity = 1.0 (perfect match)
If two movies share no common features → Angle = 90° → Similarity = 0.0 (no relation)

<img src="https://github.com/user-attachments/assets/3ded4a7f-f896-4931-84a6-547f63868b8f" width="600" height="400" alt="Cosine Similarity">


For this project, the score compares transformed metadata vectors. It can rank titles with overlapping or related metadata above less similar titles; the base similarity score by itself is not a user-preference or relevance judgment.

---

## 🏗️ System Architecture
<img width="2300" height="2826" alt="movie-recommendation-architecture" src="https://github.com/user-attachments/assets/57ac7461-505b-44a8-935d-d73eb01e157a" />

1.  **Data Collection**:
    - **Wikipedia Movie Lists**: A preprocessing notebook fetches American film-list tables for years 2018 through 2025 from [Wikipedia](https://en.wikipedia.org/wiki/Main_Page).
    - **Kaggle IMDb Dataset**: Downloaded the comprehensive [The Movies Dataset](https://www.kaggle.com/rounakbanik/the-movies-dataset) and [The Movie Dataset](https://www.kaggle.com/datasets/karrrimba/movie-metadatacsv) from Kaggle, which provided:
      - `movies_metadata.csv` 
      - `credits.csv` 
      - `movie_metadata.csv`
    - **IMDb Review Dataset**: Downloaded 50,000 labeled movie reviews from Kaggle's [IMDb Dataset of 50K Movie Reviews](https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews) (25,000 positive + 25,000 negative) for training the sentiment analysis model.
    - **Real-Time Data Augmentation**: Integrated The Movie Database (TMDB) API to enrich the static dataset with up-to-date metadata, including live vote averages, popularity scores, trailers, and high-resolution posters for enhanced user experience.

2.  **Model Training (Sentiment Analysis)**:
    - Analyzed and preprocessed **50,000 IMDb reviews** (25,000 positive + 25,000 negative)
    - Trained multiple algorithms: **Multinomial Naive Bayes**, **Logistic Regression**, and **Linear SVC**.
    - The checked-in model comparison reports Logistic Regression slightly above Linear SVM; the checked-in production artifact is trained with `LinearSVC(C=2, max_iter=2000)`.

3.  **Recommendation Engine & Optimization**:
    - **Vectorization**: Used TF-IDF to convert text data into numerical vectors.
    - **Dimensionality Reduction**: Applied **TruncatedSVD** to reduce the feature space. 
    - **Indexing**: Implemented a FAISS `IndexFlatIP` exact inner-product index over normalized movie vectors. No recommender latency benchmark is documented.
4.  **Trailer Fetching & Playback**:
    - **Backend**: `get_trailer()` method queries TMDB API for movie videos, prioritizes official trailers, and returns YouTube keys.
    - **Frontend**: Dynamic modal with embedded YouTube player, loading states, and auto-play functionality for seamless user experience.

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask, Gunicorn
- **Data Preparation**: Jupyter notebooks, pandas, and Requests for dataset processing and Wikipedia movie-list collection
- **Machine Learning**: Scikit-Learn, NumPy, Pandas, FAISS, NLTK
- **Frontend**: HTML5, CSS3, JavaScript (AJAX), Bootstrap
- **APIs**: The Movie Database (TMDB) API
- **Deployment**: Render
- **Production Database:** Neon PostgreSQL
- **Database ORM:** Flask-SQLAlchemy
- **Database Migrations:** Flask-Migrate
---

## 💡 Professional Handling: Challenges & Solutions

### 1. Recommendation Index
The preprocessing notebook fits a 128-component TruncatedSVD transform, L2-normalizes the resulting movie vectors, and builds a FAISS `IndexFlatIP` index. Because the vectors are normalized, inner-product ranking corresponds to cosine-similarity ranking. `IndexFlatIP` performs exact flat search; it is not an approximate-nearest-neighbor index.

### 2. Dataset Preparation
The checked-in preprocessing notebooks process the movie datasets and collect movie-list tables from Wikipedia. Runtime movie details, credits, posters, and trailer lookups use TMDB. IMDb review-page scraping is not used by the runtime application.

### 3. Integrating Cosine Similarity with Flask
**Problem:** Aligning data preprocessing, model loading, and real-time query handling created sync issues and potential crashes.

**Solution:**
- Implemented robust validation checks before querying the index.
- Added graceful fallback messaging for missing movies.
- Optimized data serialization to prevent memory spikes during runtime.

### 4. TMDB API Integration & Synchronization
**Problem:** Asynchronous API calls for metadata, posters, and trailers led to incomplete page loads and synchronization issues.

**Solution:**
- Designed structured **AJAX request chains** for sequential data loading.
- Implemented comprehensive error handling and loading indicators (spinners) to improve UX.
- Ensured consistent UI rendering even if partial API data fails.

### 5. Handling Null or Missing Metadata
**Problem:** Critical identifiers (like IMDb IDs) returning null values caused review submission errors.

**Solution:**
- Added hidden form validation and defensive backend logic.
- Improved template data binding to prevent data corruption.
- Ensured data consistency across user sessions.

### 6. Internal Server Errors During Reviews
**Problem:** Server crashes during review submission due to improper form handling.

**Solution:**
- Implemented structured error logging.
- Validated all form parameters server-side before database insertion.
- Strengthened Flask route exception handling for stability.

### 7. TMDB Response Caching
The `TMDBService` keeps cached responses in process memory for up to 24 hours. Cache behavior and performance have not been benchmarked.

## ⚙️ Recommendation Artifacts
The application loads its preprocessed movie data, fitted vectorizer, TruncatedSVD transform, and FAISS index from the checked-in model artifacts. The repository does not include a reproducible benchmark for recommendation latency, memory consumption, or scaling capacity.

---

### Home Page
## 📸 Screenshots
<img width="1364" height="733" alt="Screenshot (269)" src="https://github.com/user-attachments/assets/3ec88e5c-d8bd-4c45-9b7e-88e36b63ddba" />


### Movie Details & Trailer
<img width="1366" height="732" alt="Screenshot (262)" src="https://github.com/user-attachments/assets/86f1ab95-c2cd-4d6c-b7a3-366b5e8359c3" />

### Reviews
<img width="1366" height="733" alt="Screenshot (264)" src="https://github.com/user-attachments/assets/38098191-aeb5-4b1d-af22-b066eadb2603" />

### Recommendations
<img width="1366" height="733" alt="Screenshot (263)" src="https://github.com/user-attachments/assets/95c5b9c8-ca45-4d0d-826d-fb1ef053a832" />


### 🗄️ Database Schema 
## 📸 Screenshots

### 🎬 Movie Recommendations History
<img width="1366" height="768" alt="Screenshot (265)" src="https://github.com/user-attachments/assets/67ea7d51-364a-495b-91fa-282261b0fc7c" />

### ⭐ User Reviews with Sentiment Analysis
<img width="1366" height="768" alt="Screenshot (266)" src="https://github.com/user-attachments/assets/5f4bbadc-5d08-4af4-9b54-cd22d9f9793d" />

### 👤 User Accounts
<img width="1366" height="768" alt="Screenshot (268)" src="https://github.com/user-attachments/assets/096e4c58-bddf-4f4c-80cc-3a21a85a1a82" />

### 🔍 Search History
<img width="1366" height="768" alt="Screenshot (267)" src="https://github.com/user-attachments/assets/9811ff8a-c9a2-4896-808a-2dae8774508b" />

---

## ⚙️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Thomasayanfeoluwa/Movie-Cotent-Based-Recommender-System
    cd Movie-Cotent-Based-Recommender-System
    ```

2.  **Create a Virtual Environment**
    ```bash
    conda create -n rec_sys python=3.11
    conda activate rec_sys
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up Environment Variables**
    Create a `.env` file in the root directory:
    ```env
    TMDB_API_KEY=your_tmdb_api_key
    DATABASE_URL=postgresql://user:password@localhost/dbname
    FLASK_SECRET_KEY=your_secret_key
    RATELIMIT_STORAGE_URI=memory://
    ```
    For isolated local development, set `DATABASE_URL=sqlite:///local.db`; this creates a SQLite database under Flask's instance folder. `memory://` is suitable locally and does not share rate-limit counters between worker processes. TMDB search, trailers, and movie metadata also require `TMDB_API_KEY`. In production, use the PostgreSQL connection string for `DATABASE_URL` and a shared Redis URL for `RATELIMIT_STORAGE_URI`; never commit credentials.

5.  **Initialize the Database**
    ```bash
    flask db upgrade
    ```
    This applies the checked-in migrations, including the per-user movie-feedback table.

6.  **Run the Application**
    ```bash
    flask run
    ```
    Access the local app at http://127.0.0.1:5000. For the deployed app, use the verified Render link in the Demo section above.

---

## 📄 License

This project is licensed under the MIT License.
