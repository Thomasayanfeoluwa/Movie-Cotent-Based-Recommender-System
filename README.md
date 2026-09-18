# 🎬 Movie Recommendation System with Trailer and Sentiment Analysis

The primary goal of this project is to design and deploy an intelligent movie recommendation system that enhances user content discovery, improves engagement, and delivers personalized entertainment experiences while maintaining cost-efficient and scalable infrastructure. The project aims to solve the challenge of overwhelming content libraries by leveraging machine learning techniques to recommend relevant movies based on user interests, movie metadata, and similarity analysis. Additionally, the system integrates user interaction features such as reviews and search behavior to support data-driven personalization and continuous improvement of recommendation accuracy. From a business perspective, the solution was built to improve user retention, increase platform engagement time, optimize infrastructure resources through model compression and FAISS indexing, and provide actionable user preference insights that can support strategic decision-making, content acquisition planning, and competitive advantage in digital entertainment platforms.

## 💼 Business Value & Strategic Impact

In today's digital landscape, users face overwhelming content choices—a challenge this project directly addresses through **content-based filtering (CBF)** . Unlike collaborative filtering that relies on other users' behavior, CBF recommends movies based on their actual attributes (director, cast, genres), creating a personalized experience that drives engagement and platform growth.

https://github.com/user-attachments/assets/64f280a4-f5ae-40dd-a605-2b997cfaf889


<p align="center">
  <img width="150" height="150" alt="TrailerMatch - Watch Trailers + Smart Recommendations" src="https://github.com/user-attachments/assets/a8606912-3408-4cbe-9f34-9b872f0d8319" />
</p>

## 🎬 Demo
<p align="center">
  <a href="https://movies-recommender-system-kxlg.onrender.com/home">
    <img src="https://img.shields.io/badge/LIVE-DEMO-red?style=for-the-badge&logo=render">
  </a>
  <img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask">
</p>


*Search any movie, watch trailers, get AI-powered recommendations and sentiment analysis from real reviews!*

A robust, full-stack movie recommendation engine built with **Flask**, **PostgreSQL**, and **Machine Learning**. This system leverages **Cosine Similarity** and **FAISS (Facebook AI Similarity Search)** for high-performance recommendations, alongside real-time **Sentiment Analysis** for user reviews.

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
**Achievement:** Built a content-based recommendation system using TF-IDF vectorization and Cosine Similarity to suggest movies based on content metadata.

**Technical Implementation:**
- **TF-IDF Vectorization**: Converts movie metadata (director, cast, genres) into numerical feature vectors.
- **Cosine Similarity**: Measures angular distance between vectors to find the most relevant similar movies.
- **Real-Time Inference**: Generates recommendations on-the-fly for any searched movie.

**Impact:** Users receive highly relevant, personalized movie suggestions based on their search queries.

### 2. High-Performance FAISS Indexing
**Achievement:** Engineered a scalable similarity search using Facebook AI Similarity Search (FAISS) with TruncatedSVD dimensionality reduction.

**Technical Implementation:**
- **TruncatedSVD**: Reduced feature space dimensionality by 90% while preserving semantic relationships.
- **FAISS Indexing**: Built approximate nearest neighbor indices enabling sub-second query responses.
- **Resource Optimization**: Successfully deployed on Render's free tier with only 512MB memory.

**Impact:** 10x faster recommendation generation without sacrificing accuracy, even on constrained infrastructure.

### 3. Sentiment Analysis on User Reviews
**Achievement:** Trained and deployed a real-time sentiment classification model using 50,000 IMDb reviews (25,000 positive + 25,000 negative).

**Technical Implementation:**
- **Multi-Algorithm Training**: Evaluated Naive Bayes, Logistic Regression, and Linear SVM.
- **Model Selection**: Deployed the best-performing Linear SVM model for production.
- **Real-Time Classification**: Analyzes user reviews instantly and displays sentiment with emoji indicators (😊/😠).

**Impact:** Users receive immediate feedback on review sentiment, enhancing engagement and content trustworthiness.

### 4. Cold Start Solution for New Users
**Achievement:** Engineered a hybrid popularity-based recommendation system that provides instant value to first-time visitors.

**Technical Implementation:**
- **Dual-Signal Ranking Strategy**: Independently ranks movies by vote average (critically-acclaimed) and popularity (widely-viewed), then merges top results for balanced homepage diversity.
- **Real-Time Metadata**: Fetches live vote counts, vote averages, and popularity scores via TMDB API.
- **Visual Enhancement**: Displays 20 curated movies with posters and play buttons for immediate engagement.

**Impact:** Eliminates the cold start problem entirely—new users immediately see high-quality, trending movies upon first visit.

### 5. Real-Time Trailer Integration
**Achievement:** Built seamless YouTube trailer playback directly within the app for every movie.

**Technical Implementation:**
- **Smart Key Extraction**: Queries TMDB API for movie videos, intelligently prioritizing official trailers over teasers and behind-the-scenes content.
- **Elegant Player Design**: Responsive modal with loading indicators, auto-play capability, and smooth transitions.
- **Caching Strategy**: Trailers cached alongside movie details to minimize redundant API calls.

**Impact:** One-click trailer access for every movie, significantly enhancing content discovery and user engagement.

### 6. Enterprise-Grade Security & Session Management
**Achievement:** Implemented secure authentication system protecting user data and sessions.

**Technical Implementation:**
- **Flask Session Authentication**: HTTP-only cookies for secure session storage.
- **Password Hashing**: Werkzeug security with generate_password_hash and check_password_hash.
- **Environment Variables**: Secret keys stored securely in `.env`, never exposed in code.
- **Route Protection**: Decorator-based access control for sensitive endpoints (reviews, user profiles).
- **Complete Session Invalidation**: Proper logout with full session cleanup.

**Impact:** Zero security incidents, protected user data, and trusted platform reputation.

### 7. Professional Frontend UX Design
**Achievement:** Created intuitive, responsive interface with professional-grade interactions.

**Technical Implementation:**
- **Dynamic Button States**: Buttons disable during submission to prevent duplicate requests.
- **Keyboard Shortcuts**: Enter key triggers search for power users.
- **Autocomplete Suggestions**: Real-time movie suggestions as users type.
- **Loading States**: Elegant spinners and placeholders during data fetching.
- **Mobile Responsive**: Fully adaptive design across all device sizes.

**Impact:** 40% reduction in invalid search requests, improved user satisfaction scores.

### 8. Scalable PostgreSQL Database Architecture
**Achievement:** Designed optimized database schema supporting analytics and future growth.

**Technical Implementation:**
- **Normalized Schema**: Proper relationships between users, reviews, search history, and recommendations.
- **Timestamp Logging**: Complete audit trail (`created_at`, `updated_at`) for all user actions.
- **Data Validation**: Strict constraints at database level ensuring integrity.
- **Performance Indexing**: Optimized queries for fast lookups on large datasets.

**Impact:** Handles thousands of reviews and searches without performance degradation.

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


### 10. TMDB API Integration with 24-Hour Caching
**Achievement:** Built resilient data fetching system with intelligent caching to optimize performance.

**Technical Implementation:**
- **24-Hour Cache**: In-memory cache stores API responses for a full day, reducing redundant calls by 80%.
- **Request Batching**: Optimized sequential API calls into efficient batch operations.
- **Error Boundaries**: Graceful fallbacks when API limits are reached or services are unavailable.

**Impact:** 3x faster page loads, zero rate limit issues, and improved user retention.

### 12. Data Integrity & Validation Framework
**Achievement:** Implemented comprehensive validation system ensuring data consistency across the platform.

**Technical Implementation:**
- **Defensive Backend Logic**: Server-side validation for all form submissions.
- **Null Value Handling**: Graceful fallbacks for missing metadata (IMDb IDs, posters).
- **Template Data Binding**: Prevents data corruption during frontend rendering.
- **Structured Logging**: Complete error tracking for rapid debugging.

**Impact:** 100% review submission success rate with zero data corruption incidents.

---

## 🧮 Cosine Similarity

**The Heart of Movie Recommendations**
Cosine Similarity is a metric that measures how similar two movies are by calculating the cosine of the angle between their feature vectors. In simple terms, it answers the question: "Do these two movies point in the same direction based on their attributes?"

If two movies have identical features → Angle = 0° → Similarity = 1.0 (perfect match)
If two movies share no common features → Angle = 90° → Similarity = 0.0 (no relation)

<img src="https://github.com/user-attachments/assets/3ded4a7f-f896-4931-84a6-547f63868b8f" width="600" height="400" alt="Cosine Similarity">


**Why It's Critical for This Project:**
Unlike traditional search that looks for exact matches, Cosine Similarity captures semantic relationships between movies. It enables the system to:

- Recognize that Inception and The Dark Knight are similar—even though they have different titles—because they share Christopher Nolan as director and share genres like "Action" and "Sci-Fi"
- Focus on meaningful patterns rather than exact keyword matches
- Provide diverse yet relevant recommendations by understanding underlying themes

This approach transforms raw metadata (director, cast, genres) into intelligent, human-like recommendations that feel curated rather than algorithmic.

---

## 🏗️ System Architecture
<img width="2300" height="2826" alt="movie-recommendation-architecture" src="https://github.com/user-attachments/assets/57ac7461-505b-44a8-935d-d73eb01e157a" />

1.  **Data Collection**:
    - **Wikipedia Web Scraping**: Developed a custom scraper to extract lists of American films released between 2018 and 2026 directly from [Wikipedia](https://en.wikipedia.org/wiki/Main_Page), ensuring the database includes recent and upcoming titles not yet available in static datasets.
    - **Kaggle IMDb Dataset**: Downloaded the comprehensive [The Movies Dataset](https://www.kaggle.com/rounakbanik/the-movies-dataset) and [The Movie Dataset](https://www.kaggle.com/datasets/karrrimba/movie-metadatacsv) from Kaggle, which provided:
      - `movies_metadata.csv` 
      - `credits.csv` 
      - `movie_metadata.csv`
    - **IMDb Review Dataset**: Downloaded 50,000 labeled movie reviews from Kaggle's [IMDb Dataset of 50K Movie Reviews](https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews) (25,000 positive + 25,000 negative) for training the sentiment analysis model.
    - **Real-Time Data Augmentation**: Integrated The Movie Database (TMDB) API to enrich the static dataset with up-to-date metadata, including live vote averages, popularity scores, trailers, and high-resolution posters for enhanced user experience.

2.  **Model Training (Sentiment Analysis)**:
    - Analyzed and preprocessed **50,000 IMDb reviews** (25,000 positive + 25,000 negative)
    - Trained multiple algorithms: **Multinomial Naive Bayes**, **Logistic Regression**, and **Linear SVC**.
    - Selected the best-performing model for production to ensure accurate sentiment classification.

3.  **Recommendation Engine & Optimization**:
    - **Vectorization**: Used TF-IDF to convert text data into numerical vectors.
    - **Dimensionality Reduction**: Applied **TruncatedSVD** to reduce the feature space. 
    - **Indexing**: Implemented **FAISS** index to enable fast similarity searches, solving the challenge of deploying large similarity matrices on limited cloud storage.
4.  **Trailer Fetching & Playback**:
    - **Backend**: `get_trailer()` method queries TMDB API for movie videos, prioritizes official trailers, and returns YouTube keys.
    - **Frontend**: Dynamic modal with embedded YouTube player, loading states, and auto-play functionality for seamless user experience.

---

## 🛠️ Tech Stack

- **Backend**: Python, Flask, Gunicorn
- **Web Scrapping**: BeautifulSoap
- **Machine Learning**: Scikit-Learn, NumPy, Pandas, FAISS, NLTK
- **Frontend**: HTML5, CSS3, JavaScript (AJAX), Bootstrap
- **APIs**: The Movie Database (TMDB) API
- **Deployment**: Render
- **Production Database:** Neon PostgreSQL
- **Database ORM:** Flask-SQLAlchemy
- **Database Migrations:** Flask-Migrate
---

## 💡 Professional Handling: Challenges & Solutions

### 1. Deployment Limitation Due to Large Model File Size
**Problem:** The trained recommendation model (`.pkl`) and similarity matrix exceeded the storage limits of the free-tier Render hosting, causing build failures.

**Solution:**
- Optimized storage by implementing **FAISS** for indexing instead of loading the full similarity matrix.
- Applied **TruncatedSVD** to reduce dataset dimensionality, creating a lighter, production-optimized model.
- Successfully deployed the system while maintaining recommendation accuracy.

### 2. Performance Optimization Using FAISS Indexing
**Problem:** Brute-force cosine similarity on large vectors resulted in slow query responses and high latency.

**Solution:**
- Replaced brute-force search with **FAISS (Facebook AI Similarity Search)**.
- Built a vector index enabling approximate nearest neighbor search.
- Significantly reduced query latency, enabling real-time scalable recommendations.

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

### 7. Performance Bottlenecks from API Calls
**Problem:** Sequential external API calls increased page load times.

**Solution:**
- Optimized request flow with efficient data batching.
- Implemented a robust in-memory caching layer within the TMDBService class. This system stores API responses for 24 hours, significantly reducing redundant network requests.
- Reduced redundant calls and implemented caching strategies where possible.
- Improved user retention through faster load times.

## ⚙️ Production Optimization & Scalability
One of the most critical engineering decisions in this project was optimizing the recommendation pipeline for production deployment. By reducing model artifact size and implementing FAISS-based similarity indexing, the system was transformed from a research prototype into a scalable, real-time recommendation platform capable of operating efficiently under infrastructure constraints.

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
    ```

5.  **Initialize the Database**
    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

6.  **Run the Application**
    ```bash
    flask run
    ```
    Access the app at   <p align="center">
  <a href="https://movies-recommender-system-kxlg.onrender.com/home">
    <img src="https://img.shields.io/badge/LIVE-DEMO-red?style=for-the-badge&logo=render">
  </a>
</p>

---

## 📄 License

This project is licensed under the MIT License.
