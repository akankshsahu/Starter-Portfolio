import os, joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import precision_score, recall_score, roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "exoplanets_clean.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

df = pd.read_csv(DATA)
y = df['habitable_candidate']
X = df[['pl_orbsmax','pl_rade','pl_orbeccen','pl_insol','st_teff','st_rad','st_mass','st_lum','sy_dist','sy_snum','sy_pnum','disc_year']].fillna(0)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

logit = Pipeline([('scaler', StandardScaler()), ('clf', LogisticRegression(max_iter=500, class_weight='balanced'))])
rf = RandomForestClassifier(n_estimators=400, random_state=42, min_samples_leaf=2)

logit.fit(X_train, y_train)
rf.fit(X_train, y_train)

def eval(model, name):
    proba = model.predict_proba(X_test)[:,1] if hasattr(model, "predict_proba") else model.predict(X_test)
    yhat = (proba >= 0.5).astype(int)
    prec = precision_score(y_test, yhat, zero_division=0)
    rec = recall_score(y_test, yhat, zero_division=0)
    try:
        auc = roc_auc_score(y_test, proba)
    except Exception:
        auc = 0.5
    print(f"{name}: precision={prec:.3f} recall={rec:.3f} auc={auc:.3f}")
    return auc

auc_logit = eval(logit, "Logistic")
auc_rf = eval(rf, "RandomForest")
best = rf if auc_rf >= auc_logit else logit
import joblib
joblib.dump(best, os.path.join(MODEL_DIR, "classifier.joblib"))
print("Saved best model to models/classifier.joblib")
