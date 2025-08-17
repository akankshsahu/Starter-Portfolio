# Exoplanet Habitability Predictor
Run in order:
```bash
python src/fetch_data.py
python src/preprocess.py
python src/train_models.py
uvicorn projects.exoplanet_habitability.src.api:app --host 0.0.0.0 --port 8002
```
See DOCUMENTATION.md for details.
