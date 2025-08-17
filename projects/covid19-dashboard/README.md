# COVID‑19 Data Trends Dashboard
Run:
```bash
python src/fetch_data.py
python src/build_features.py
uvicorn projects.covid19_dashboard.src.api:app --host 0.0.0.0 --port 8003
```
In Tableau, connect to `data/processed/covid_features.csv`.
