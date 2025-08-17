import os, joblib, warnings
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, roc_auc_score
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

warnings.filterwarnings("ignore")

DATA = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "rookie_features.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

df = pd.read_csv(DATA)

cat = ['position','team']
num = ['games','passing_yards','rushing_attempts','rushing_yards','receptions','receiving_yards','tackles','workload','efficiency_run','efficiency_rec','is_offense','season']

X = df[cat+num]
y_reg = df['total_yards']
y_cls = df['pro_bowl']

pre = ColumnTransformer([
    ('cat', OneHotEncoder(handle_unknown='ignore'), cat),
    ('num', StandardScaler(), num)
])

lin = Pipeline([('pre', pre), ('model', LinearRegression())])
rf_reg = Pipeline([('pre', pre), ('model', RandomForestRegressor(n_estimators=200, random_state=42))])

X_train, X_test, y_train, y_test = train_test_split(X, y_reg, test_size=0.2, random_state=42)
lin.fit(X_train, y_train)
rf_reg.fit(X_train, y_train)

r2_lin = r2_score(y_test, lin.predict(X_test))
r2_rf = r2_score(y_test, rf_reg.predict(X_test))
best_reg = lin if r2_lin >= r2_rf else rf_reg
joblib.dump(best_reg, os.path.join(MODEL_DIR, "regression.joblib"))

logit = Pipeline([('pre', pre), ('model', LogisticRegression(max_iter=200))])
rf_cls = Pipeline([('pre', pre), ('model', RandomForestClassifier(n_estimators=300, random_state=42))])
Xc_train, Xc_test, yc_train, yc_test = train_test_split(X, y_cls, test_size=0.2, random_state=42, stratify=y_cls)
logit.fit(Xc_train, yc_train)
rf_cls.fit(Xc_train, yc_train)

def auc(m):
    try:
        return roc_auc_score(yc_test, m.predict_proba(Xc_test)[:,1])
    except Exception:
        return 0.5

auc_logit = auc(logit)
auc_rf = auc(rf_cls)
best_cls = logit if auc_logit >= auc_rf else rf_cls
joblib.dump(best_cls, os.path.join(MODEL_DIR, "classification.joblib"))

print("Saved models. R2 lin/rf:", round(r2_lin,3), round(r2_rf,3), " AUC logit/rf:", round(auc_logit,3), round(auc_rf,3))
