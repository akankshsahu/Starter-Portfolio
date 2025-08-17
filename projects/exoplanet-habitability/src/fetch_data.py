import os, io
import pandas as pd
import requests

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(RAW, exist_ok=True)

TAP = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
QUERY = (
    "select pl_name,pl_orbsmax,pl_rade,pl_orbeccen,pl_insol,st_teff,st_rad,st_mass,st_lum,sy_dist,sy_snum,sy_pnum,disc_year "
    "from ps where default_flag=1"
)

def fetch():
    try:
        params = {"query": QUERY, "format": "csv"}
        r = requests.get(TAP, params=params, timeout=60)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        print("Fetched from NASA TAP:", df.shape)
        df.to_csv(os.path.join(RAW, "exoplanets.csv"), index=False)
    except Exception as e:
        print("Online fetch failed, using sample data. Error:", e)
        sample = os.path.join(RAW, "sample_exoplanets.csv")
        df = pd.read_csv(sample)
        df.to_csv(os.path.join(RAW, "exoplanets.csv"), index=False)
    return True

if __name__ == "__main__":
    fetch()
    print("Saved raw/exoplanets.csv")
