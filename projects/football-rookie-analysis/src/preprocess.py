import pandas as pd
import numpy as np
import os

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "rookies_filtered.csv")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv(RAW)

df['total_yards'] = df[['passing_yards','rushing_yards','receiving_yards']].fillna(0).sum(axis=1)
df['workload'] = df[['rushing_attempts','receptions']].fillna(0).sum(axis=1)
df['efficiency_run'] = (df['rushing_yards'] / df['rushing_attempts']).replace([np.inf,-np.inf], np.nan).fillna(0)
df['efficiency_rec'] = (df['receiving_yards'] / df['receptions']).replace([np.inf,-np.inf], np.nan).fillna(0)
df['is_offense'] = df['position'].isin(['QB','RB','WR','TE']).astype(int)

keep = ['player','position','team','season','games','passing_yards','rushing_attempts','rushing_yards','receptions','receiving_yards','tackles','pro_bowl','total_yards','workload','efficiency_run','efficiency_rec','is_offense']
df = df[keep]

df.to_csv(os.path.join(OUT, "rookie_features.csv"), index=False)
print("Wrote processed/rookie_features.csv", df.shape)
