# Project State and Remediation Roadmap

## Purpose

This document records the repository review and the staged plan for addressing the reviewer findings. Work will proceed one stage at a time, with tests and acceptance checks before moving on. No remediation changes have been made yet.

## Current state

The source review confirmed the following:

1. **Flask secret key has a known fallback.** `app.py` assigns `"dev-secret-key"` when `FLASK_SECRET_KEY` is missing.
2. **CSRF protection was not found.** Signup, signin, and review forms do not include CSRF tokens, and there is no CSRF middleware or dependency visible in the repository. Logout changes session state through GET.
3. **TMDB proxy routes are accessible without authentication.** The app has no application-level rate limit on these routes. The TMDB service uses an in-memory cache, which is not a substitute for limiting requests and may not be shared across production workers.
4. **`/recommend` returns exception text.** The route logs the exception and sends `str(e)` to the client with status 500.
5. **IMDb review scraping has no timeout.** The source review does not determine whether the scraping complies with IMDb's terms.
6. **README impact claims lack measurement evidence in the repository.** Claims include 10x faster recommendations, 40% fewer invalid searches, zero security incidents, 100% review submission success, and 3x faster page loads.
7. **No offline recommendation ranking evaluation was found.** The repository contains sentiment-classification metrics, but those do not evaluate recommender relevance. No relevance labels for recommender evaluation have yet been established.
8. **README demo URLs conflict.** The badge near the top and the setup section near the bottom link to different Render apps. The correct live URL remains unverified.
9. **README describes FAISS as approximate nearest-neighbor search, but the notebook builds `IndexFlatIP`, an exact flat index.**
10. **The sentiment-model selection claim should be revisited.** The checked-in notebook output shows Logistic Regression scoring higher than Linear SVM on the reported metrics, while the README says Linear SVM was the best-performing model.

The repository contains a Flask application, database models, and a TF-IDF/SVD/FAISS recommendation path. The source alone does not establish that the database is Neon or that the deployment is currently live.

## Proposed stages

### Stage 1 - Establish a baseline

- Add or identify focused tests for the routes and user flows that will be changed.
- Map all state-changing routes, including browser form and AJAX requests.
- Record which movie-discovery features must remain available to signed-out visitors.
- Inspect available deployment configuration for the demo URL and shared rate-limit storage.

**Acceptance checks**

- Existing key flows have tests or a documented verification procedure.
- Any intentional behavior changes are identified before implementation.
- Existing unrelated work is preserved.

### Stage 2 - Require a configured Flask secret

- Remove the known development fallback from `app.py`.
- Fail startup clearly when `FLASK_SECRET_KEY` is missing or blank.
- Document secure local and deployment configuration without adding a real secret to the repository.
- Add tests for missing, blank, and configured values.

**Acceptance checks**

- The application cannot start with a missing or blank secret key.
- A configured secret allows startup.
- No production secret is committed.

### Stage 3 - Protect state-changing requests against CSRF

- Add a Flask-compatible CSRF protection dependency and initialize it following the project's patterns.
- Add CSRF tokens to signup, signin, and review forms.
- Update AJAX submissions that issue state-changing requests so they send valid tokens.
- Change logout from GET to POST and protect it.
- Test that missing/invalid tokens are rejected and legitimate requests succeed.

**Acceptance checks**

- Every state-changing route is covered by CSRF protection.
- The normal signed-in and signed-out flows continue to work.
- Logout cannot be triggered by an unprotected GET request.

### Stage 4 - Limit TMDB proxy usage

- Keep anonymous movie discovery available unless product requirements say otherwise.
- Add request limits and sensible input bounds to the proxy endpoints.
- Prefer a shared rate-limit backend for multi-worker production. A per-process limiter must not be presented as reliable cross-worker protection.
- Preserve the existing UI's access to search, movie, credits, and person data.
- Test normal requests, invalid/oversized inputs, and requests over the limit.

**Acceptance checks**

- Anonymous browsing continues to work within configured limits.
- Excessive proxy use is rejected predictably.
- The chosen storage backend and its deployment requirements are documented.

### Stage 5 - Avoid returning internal exception details

- Keep diagnostic detail in server logs.
- Return a stable, generic error response from `/recommend`.
- Add a test that forces an exception and verifies internal exception text is not present in the response.

**Acceptance checks**

- The client gets a clear failure status/message without a traceback or exception details.
- The exception remains available in server logs for diagnosis.

### Stage 6 - Remove or replace IMDb scraping

- Default proposal: remove the IMDb scrape and continue showing reviews stored in the application's database.
- Retain external reviews only if an approved source and access method are identified.
- If an external request remains, set an explicit timeout and handle its failure without breaking recommendation rendering.
- Test rendering when no external reviews are available.

**Acceptance checks**

- There is no unbounded IMDb request.
- Recommendation pages render even when an external review source is unavailable or unused.
- Any retained source has an approved use basis documented by the project owner.

### Stage 7 - Establish offline recommendation evaluation

- First identify or create defensible, held-out relevance judgments for recommendations.
- Do not treat sentiment scores, popularity, or similarity to the query item as user relevance unless clearly labeled as proxy measures.
- Implement a reproducible evaluation for metrics such as Precision@K and NDCG@K, with a fixed split and documented parameters.
- Keep recommender evaluation separate from sentiment-classification evaluation.
- Correct the sentiment-model README claim to match the notebook evidence, or retrain/re-evaluate before making a different claim.

**Acceptance checks**

- Evaluation can be rerun and produces the documented metric outputs.
- The test data is held out from fitting/tuning as described.
- Metrics are not claimed until their relevance labels and methodology are explained.

### Stage 8 - Correct README claims and demo links

- Remove or qualify performance, reliability, security, and impact figures unless supporting measurements and methodology can be provided.
- Correct the FAISS description to reflect the exact flat index currently used, or update the description only if the implementation is deliberately changed and validated.
- Verify which Render URL is current and use one consistent URL in all README locations.
- If neither URL can be verified, label the demo as unverified rather than choosing one by assumption.
- Reconcile the claimed best-performing sentiment model with notebook results.

**Acceptance checks**

- README statements match implementation and checked-in evidence.
- Unsupported numerical claims are removed or accompanied by reproducible evidence.
- All demo links use the same verified destination.

### Stage 9 - Regression verification and closeout

- Run focused tests for each changed stage and the repository's available broader checks.
- Review the complete diff for regressions and unrelated edits.
- Record test results, deployment-only follow-up, and any remaining limitations here.

**Acceptance checks**

- Relevant tests and checks pass, or any environment limitation is reported explicitly.
- No unrelated user changes have been reverted.
- Remaining work is clearly identified before calling the remediation complete.

## Decisions to confirm before implementation

1. **Anonymous TMDB access:** Proposed default is to preserve it and add rate limiting, since the current movie-discovery UI relies on it.
2. **IMDb reviews:** Proposed default is to remove IMDb scraping and use application-submitted reviews unless an approved alternative source is specified.
3. **Recommendation relevance data:** A meaningful ranking evaluation requires relevance judgments. The project owner must provide or approve the data and the assumptions used to label relevance.
4. **Demo URL:** The current Render app must be verified before changing the README destination.

## Progress log

- Review and roadmap prepared.
- No application code, tests, dependencies, or deployment configuration have been changed.
