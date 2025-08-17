import os
import pandas as pd

RAW = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "covid_owid.csv")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv(RAW, parse_dates=['date'])
keep = ['iso_code','continent','location','date','total_cases','new_cases','total_deaths','new_deaths','total_vaccinations','people_vaccinated','people_fully_vaccinated','new_vaccinations','population']
df = df[keep].dropna(subset=['location','date'])

df = df.sort_values(['location','date'])

df['new_cases_7d_avg'] = df.groupby('location')['new_cases'].transform(lambda s: s.rolling(7, min_periods=1).mean())
df['new_deaths_7d_avg'] = df.groupby('location')['new_deaths'].transform(lambda s: s.rolling(7, min_periods=1).mean())
df['people_vaccinated_pct'] = (df['people_vaccinated'] / df['population'] * 100).fillna(0)
df['people_fully_vaccinated_pct'] = (df['people_fully_vaccinated'] / df['population'] * 100).fillna(0)

df.to_csv(os.path.join(OUT, "covid_features.csv"), index=False)
print("Wrote processed/covid_features.csv", df.shape)
