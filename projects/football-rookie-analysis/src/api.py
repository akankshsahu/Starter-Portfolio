from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import os, joblib

app = FastAPI(title="Football Rookie API", version="1.0")

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "rookie_features.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

class RookieInput(BaseModel):
    position: str
    team: str
    season: int
    games: int
    passing_yards: float = 0
    rushing_attempts: float = 0
    rushing_yards: float = 0
    receptions: float = 0
    receiving_yards: float = 0
    tackles: float = 0
    workload: float = 0
    efficiency_run: float = 0
    efficiency_rec: float = 0
    is_offense: int = 1

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/")
def root():
    return {"message": "Football Rookie API is running!"}

@app.get("/rookies")
def rookies(limit: int = 20):
    df = pd.read_csv(DATA)
    return df.head(limit).to_dict(orient="records")

@app.post("/predict_yards")
def predict_yards(x: RookieInput):
    model = joblib.load(os.path.join(MODEL_DIR, "regression.joblib"))
    df = pd.DataFrame([x.model_dump()])
    yhat = model.predict(df)[0]
    return {"predicted_total_yards": float(yhat)}

@app.post("/predict_pro_bowl")
def predict_pro_bowl(x: RookieInput):
    model = joblib.load(os.path.join(MODEL_DIR, "classification.joblib"))
    df = pd.DataFrame([x.model_dump()])
    prob = model.predict_proba(df)[0,1]
    return {"pro_bowl_probability": float(prob)}
