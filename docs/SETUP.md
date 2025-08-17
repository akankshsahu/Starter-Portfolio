# Setup 

## 1) Install the tools
- **Python 3.11+**
- **Git**
- **VS Code or another IDE** 
- **Tableau Public** 

Install them with the default options. Open **VS Code** when done.

## 2) Get this code


## 3) Make a Python sandbox (virtual env)
Open a terminal in the project folder and run:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4) Run the data pipelines
Do these one by one

```bash
# Football
python projects/football-rookie-analysis/src/fetch_data.py
python projects/football-rookie-analysis/src/analyze_rookies.py
python projects/football-rookie-analysis/src/preprocess.py
python projects/football-rookie-analysis/src/train_models.py

# Exoplanets
python projects/exoplanet-habitability/src/fetch_data.py
python projects/exoplanet-habitability/src/preprocess.py
python projects/exoplanet-habitability/src/train_models.py

# COVID
python projects/covid19-dashboard/src/fetch_data.py
python projects/covid19-dashboard/src/build_features.py
```

## 5) Start the APIs (football + exoplanets + covid)
Open three terminals (or run in the background) and start each service:

```bash
uvicorn projects.football-rookie-analysis.src.api:app --host 0.0.0.0 --port 8001
uvicorn projects.exoplanet-habitability.src.api:app --host 0.0.0.0 --port 8002
uvicorn projects.covid19-dashboard.src.api:app --host 0.0.0.0 --port 8003
```

Visit:
- http://localhost:8001/docs
- http://localhost:8002/docs
- http://localhost:8003/docs

## 6) Visualize in Tableau
Open Tableau Public → connect to each project's `data/processed/*.csv` and build dashboards with filters. Publish to Tableau Public and embed links into the portfolio site.


## 7) Deploy the APIs with Render
- Create an account at https://render.com and connect your GitHub.
- Click **New +** → **Blueprint** → select this repo (Render reads `render.yaml`).
- It will create three services (rookie-api, exoplanet-api, covid-metrics-api).
- Click **Deploy** for each.
- After they boot, copy the public URLs and paste them into `portfolio/index.html` TODOs.
