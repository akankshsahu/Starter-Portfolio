from fastapi import FastAPI
import pandas as pd
import os

app = FastAPI(title="COVID Metrics API", version="1.0")

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "covid_features.csv")

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/metrics")
def metrics(location: str = "United States", limit: int = 30):
    df = pd.read_csv(DATA, parse_dates=['date'])
    dfl = df[df['location'] == location].sort_values('date').tail(limit)
    return dfl.to_dict(orient="records")
