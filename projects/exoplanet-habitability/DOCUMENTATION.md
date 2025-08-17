# Exoplanet Habitability Predictor — Documentation
**Last updated:** 2025-08-16

## Purpose
Educational project predicting a **proxy habitability** label using NASA Exoplanet Archive (PS table). Not an official classification.

## Data source
- TAP endpoint (CSV): `https://exoplanetarchive.ipac.caltech.edu/TAP/sync`
- Example query fields: `pl_orbsmax, pl_rade, pl_orbeccen, pl_insol, st_teff, st_rad, st_mass, st_lum, sy_dist, sy_snum, sy_pnum, disc_year`

## Proxy label (heuristic)
`habitable_candidate = 1` if:
- `0.35 ≤ pl_insol ≤ 1.7`
- `0.5 ≤ pl_rade ≤ 1.75`
- `3000 ≤ st_teff ≤ 6500`
else `0`.

## Metrics on stratified split
- Precision, Recall, ROC‑AUC (best model saved).

## Files
- `src/fetch_data.py` — downloads CSV from TAP (falls back to sample data offline).
- `src/preprocess.py` — cleans and adds label.
- `src/train_models.py` — trains Logistic Regression and Random Forest; saves best to `models/classifier.joblib`.
- `src/api.py` — FastAPI endpoint `/predict_habitability` returns probability + label.
