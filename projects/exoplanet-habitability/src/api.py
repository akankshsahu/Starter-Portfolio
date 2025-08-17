from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import os, joblib

app = FastAPI(title="Exoplanet Habitability API", version="1.0")

MODEL = os.path.join(os.path.dirname(__file__), "..", "models", "classifier.joblib")

class ExoInput(BaseModel):
    pl_orbsmax: float
    pl_rade: float
    pl_orbeccen: float = 0.0
    pl_insol: float
    st_teff: float
    st_rad: float = 1.0
    st_mass: float = 1.0
    st_lum: float = 1.0
    sy_dist: float = 100.0
    sy_snum: float = 1.0
    sy_pnum: float = 1.0
    disc_year: int = 2015

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/predict_habitability")
def predict(x: ExoInput):
    model = joblib.load(MODEL)
    import pandas as pd
    df = pd.DataFrame([x.model_dump()])
    proba = float(model.predict_proba(df)[:,1][0])
    label = int(proba >= 0.5)
    return {"probability_habitable_candidate": proba, "label": label}
