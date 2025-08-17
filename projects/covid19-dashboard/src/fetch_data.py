import os
import pandas as pd
import requests

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(RAW, exist_ok=True)

URL = "https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/owid-covid-data.csv"
SAVE_PATH = os.path.join(RAW, "covid_owid.csv")

def fetch():
    try:
        print("Downloading OWID data…")
        r = requests.get(URL, timeout=300)
        r.raise_for_status()
        with open(SAVE_PATH, "wb") as f:
            f.write(r.content)
        print("✅ Saved to:", SAVE_PATH)
    except Exception as e:
        print("⚠️ Download failed:", e)
        if os.path.exists(SAVE_PATH):
            print("Using existing local copy:", SAVE_PATH)
        else:
            raise RuntimeError("No data available. Please download manually.")

if __name__ == "__main__":
    fetch()
