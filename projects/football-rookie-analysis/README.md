# Football Rookie Performance Analysis
Run in order:
```bash
python src/fetch_data.py
python src/preprocess.py
python src/train_models.py
uvicorn projects.football_rookie_analysis.src.api:app --host 0.0.0.0 --port 8001
```
Tableau: connect to `data/processed/rookie_features.csv`.
