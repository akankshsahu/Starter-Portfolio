import os
import pandas as pd
import numpy as np

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "exoplanets.csv")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(RAW)

num_cols = ['pl_orbsmax','pl_rade','pl_orbeccen','pl_insol','st_teff','st_rad','st_mass','st_lum','sy_dist','sy_snum','sy_pnum','disc_year']
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='coerce')

df = df.dropna(subset=['pl_rade','pl_insol','st_teff'])

def label(row):
    ok_insol = 0.35 <= row.get('pl_insol', np.inf) <= 1.7
    ok_size = 0.5 <= row.get('pl_rade', np.inf) <= 1.75
    ok_star = 3000 <= row.get('st_teff', 0) <= 6500
    return int(ok_insol and ok_size and ok_star)

df['habitable_candidate'] = df.apply(label, axis=1)
df.to_csv(os.path.join(OUT_DIR, "exoplanets_clean.csv"), index=False)
print("Wrote processed/exoplanets_clean.csv", df.shape)
