# %% [markdown]
# # Airline Passenger Satisfaction: ML and Feature Engineering
# Fed from PostgreSQL (`ml_training_set`). Cell-based (`# %%`): opens as a notebook in VS Code / Jupyter.
#
# Install: pip install pandas numpy scikit-learn sqlalchemy psycopg2-binary matplotlib joblib shap
#
# ## Theory notes (what each step is for)
# 1. **Problem framing**: binary classification (satisfied = 1). Two goals: *predict* and *explain*.
#    Explanation (drivers) matters more to the business than raw accuracy.
# 2. **Metrics**: check class balance first. ROC-AUC (ranking quality) is the main metric; F1 and
#    PR-AUC matter if the classes are imbalanced. Accuracy alone can hide a weak model.
# 3. **Data leakage**: fit imputers/scalers on training data only (done via Pipelines), and never use
#    features derived from the target. The train/test split is fixed in SQL (hash of id), so it is reproducible.
# 4. **Missingness is information**: a rating of 0 means "not applicable". It becomes NaN, and the
#    `*_na` flags keep that signal. Gradient boosting handles NaN natively; linear models need imputation.
# 5. **Bias-variance**: logistic regression = high bias, stable, interpretable baseline.
#    Random forest = low bias, variance reduced by averaging. Gradient boosting = usually strongest on
#    tabular data; tuned with regularisation (depth, min leaf size, L2).
# 6. **Redundancy**: raw ratings and their averages carry the same information. We use raw ratings plus
#    engineered summary features, and drop arrival delay (highly correlated with departure delay).
# 7. **Interpretation**: permutation importance (on held-out data) is more trustworthy than impurity
#    importance, which favours high-cardinality features. SHAP adds direction and per-passenger effects.
# 8. **Clustering** is unsupervised: it finds passenger archetypes from service ratings only; the target
#    is used afterwards to profile them, never to build them.

# %%
import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import joblib
from sqlalchemy import create_engine

from sklearn.model_selection import StratifiedKFold, cross_validate, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (roc_auc_score, average_precision_score, f1_score, accuracy_score,
                             classification_report, ConfusionMatrixDisplay, RocCurveDisplay)
from sklearn.inspection import permutation_importance
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

warnings.filterwarnings("ignore")
RANDOM_STATE = 42

# %% [markdown]
# ## 1. Load from PostgreSQL

# %%
DB_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@localhost:5432/airline")
engine = create_engine(DB_URL)

df = pd.read_sql("SELECT * FROM ml_training_set", engine)
print(df.shape)
print(df["target"].value_counts(normalize=True).round(3))   # class balance
print(df.isna().mean().sort_values(ascending=False).head(10).round(3))

# %% [markdown]
# ## 2. Feature engineering

# %%
RATING_COLS = ["time_convenience", "online_booking", "checkin", "online_boarding", "gate_location",
               "onboard_service", "seat_comfort", "leg_room", "cleanliness", "food_drink",
               "inflight_service", "wifi", "entertainment", "baggage"]
DIGITAL = ["online_booking", "online_boarding", "wifi"]
INFLIGHT = ["seat_comfort", "leg_room", "food_drink", "inflight_service", "entertainment",
            "cleanliness", "onboard_service"]
GROUND = ["checkin", "gate_location", "baggage", "time_convenience"]


def add_features(d: pd.DataFrame) -> pd.DataFrame:
    """Row-wise features only (no target use, no cross-row statistics) so they are leakage-safe."""
    d = d.copy()
    r = d[RATING_COLS]

    # Experience profile
    d["rating_min"] = r.min(axis=1)                       # worst touchpoint
    d["rating_std"] = r.std(axis=1)                       # inconsistency across the journey
    d["n_rated"] = r.notna().sum(axis=1)
    d["n_low_ratings"] = (r <= 2).sum(axis=1)             # pain points
    d["n_high_ratings"] = (r >= 4).sum(axis=1)            # delight points
    d["pct_low_ratings"] = d["n_low_ratings"] / d["n_rated"].replace(0, np.nan)

    # Stage gaps
    d["digital_mean"] = d[DIGITAL].mean(axis=1)
    d["inflight_mean"] = d[INFLIGHT].mean(axis=1)
    d["ground_mean"] = d[GROUND].mean(axis=1)
    d["digital_vs_inflight"] = d["digital_mean"] - d["inflight_mean"]

    # Delay and distance transforms (right-skewed -> log)
    d["log_dep_delay"] = np.log1p(d["departure_delay"].clip(lower=0))
    d["log_distance"] = np.log1p(d["flight_distance"])
    d["long_delay_flag"] = (d["departure_delay"] > 60).astype(int)

    # Interactions
    d["loyal_x_business_travel"] = d["is_loyal"] * d["is_business_travel"]
    d["business_class_x_travel"] = d["class_business"] * d["is_business_travel"]
    d["age_x_digital"] = d["age"] * d["digital_mean"]
    return d


df = add_features(df)

DROP = ["id", "target", "split",
        "arrival_delay", "arr_delayed_flag", "dep_delayed_flag",            # redundant with departure delay
        "avg_service_score", "digital_score", "inflight_score", "ground_score"]  # SQL composites duplicate raw ratings
FEATURES = [c for c in df.columns if c not in DROP]
print(len(FEATURES), "features")

train, test = df[df["split"] == "train"], df[df["split"] == "test"]
X_train, y_train = train[FEATURES], train["target"]
X_test, y_test = test[FEATURES], test["target"]

# %% [markdown]
# ## 3. Models and cross-validation (training data only)
# Baseline -> logistic regression -> random forest -> gradient boosting.

# %%
models = {
    "baseline": DummyClassifier(strategy="prior"),
    "logreg": Pipeline([("imp", SimpleImputer(strategy="median")),
                        ("sc", StandardScaler()),
                        ("clf", LogisticRegression(max_iter=2000, C=1.0))]),
    "random_forest": Pipeline([("imp", SimpleImputer(strategy="median")),
                               ("clf", RandomForestClassifier(n_estimators=300, min_samples_leaf=5,
                                                              n_jobs=-1, random_state=RANDOM_STATE))]),
    "hist_gb": HistGradientBoostingClassifier(random_state=RANDOM_STATE),   # handles NaN natively
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
scoring = {"roc_auc": "roc_auc", "pr_auc": "average_precision", "f1": "f1", "accuracy": "accuracy"}

rows = []
for name, model in models.items():
    s = cross_validate(model, X_train, y_train, cv=cv, scoring=scoring, n_jobs=-1)
    rows.append({"model": name, **{k: s[f"test_{k}"].mean().round(4) for k in scoring},
                 "auc_sd": s["test_roc_auc"].std().round(4)})
cv_results = pd.DataFrame(rows).sort_values("roc_auc", ascending=False)
print(cv_results)

# %% [markdown]
# ## 4. Tuning the best family (gradient boosting)
# Regularise with depth, leaf size and L2 to control variance.

# %%
param_dist = {
    "learning_rate": [0.03, 0.05, 0.1, 0.2],
    "max_depth": [None, 4, 6, 8],
    "max_leaf_nodes": [15, 31, 63],
    "min_samples_leaf": [20, 50, 100],
    "l2_regularization": [0.0, 0.1, 1.0, 10.0],
    "max_iter": [200, 400, 600],
}
search = RandomizedSearchCV(HistGradientBoostingClassifier(random_state=RANDOM_STATE,
                                                           early_stopping=True),
                            param_dist, n_iter=20, scoring="roc_auc", cv=3,
                            n_jobs=-1, random_state=RANDOM_STATE)
search.fit(X_train, y_train)
best = search.best_estimator_
print(search.best_params_, round(search.best_score_, 4))

# %% [markdown]
# ## 5. Final evaluation on the untouched test set

# %%
proba = best.predict_proba(X_test)[:, 1]
pred = (proba >= 0.5).astype(int)

print("ROC-AUC :", round(roc_auc_score(y_test, proba), 4))
print("PR-AUC  :", round(average_precision_score(y_test, proba), 4))
print("F1      :", round(f1_score(y_test, pred), 4))
print("Accuracy:", round(accuracy_score(y_test, pred), 4))
print(classification_report(y_test, pred, target_names=["not satisfied", "satisfied"]))

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ConfusionMatrixDisplay.from_predictions(y_test, pred, ax=ax[0], colorbar=False)
RocCurveDisplay.from_predictions(y_test, proba, ax=ax[1])
plt.tight_layout(); plt.show()

# %% [markdown]
# ## 6. Interpretation: what drives satisfaction?

# %%
# 6a. Permutation importance on held-out data
perm = permutation_importance(best, X_test, y_test, scoring="roc_auc",
                              n_repeats=5, random_state=RANDOM_STATE, n_jobs=-1)
imp = (pd.Series(perm.importances_mean, index=FEATURES)
         .sort_values(ascending=False).head(15))
imp[::-1].plot(kind="barh", figsize=(7, 5), title="Permutation importance (drop in ROC-AUC)")
plt.tight_layout(); plt.show()

# 6b. Logistic regression coefficients: direction and size (standardised features)
logreg = models["logreg"].fit(X_train, y_train)
coefs = pd.Series(logreg.named_steps["clf"].coef_[0], index=FEATURES).sort_values()
pd.concat([coefs.head(8), coefs.tail(8)]).plot(kind="barh", figsize=(7, 5),
                                               title="Logistic regression coefficients")
plt.tight_layout(); plt.show()

# 6c. SHAP (optional): direction + per-passenger effects
try:
    import shap
    sample = X_test.sample(2000, random_state=RANDOM_STATE)
    explainer = shap.Explainer(best.predict, shap.sample(X_train, 200))
    shap.summary_plot(explainer(sample), sample, show=True)
except Exception as e:
    print("SHAP skipped:", e)

# %% [markdown]
# ## 7. Passenger segmentation (unsupervised)
# Cluster on service ratings only, then profile clusters with satisfaction.

# %%
seg_cols = RATING_COLS + ["digital_mean", "inflight_mean", "ground_mean"]
Z = StandardScaler().fit_transform(SimpleImputer(strategy="median").fit_transform(df[seg_cols]))

sil = {}
sample_idx = np.random.RandomState(RANDOM_STATE).choice(len(Z), size=min(10000, len(Z)), replace=False)
for k in range(2, 8):
    km = KMeans(n_clusters=k, n_init=10, random_state=RANDOM_STATE).fit(Z)
    sil[k] = silhouette_score(Z[sample_idx], km.labels_[sample_idx])
print(pd.Series(sil).round(3))

K = max(sil, key=sil.get)          # or set manually after reviewing the profiles
df["cluster"] = KMeans(n_clusters=K, n_init=10, random_state=RANDOM_STATE).fit_predict(Z)

profile = (df.groupby("cluster")
             .agg(passengers=("id", "count"),
                  satisfaction_pct=("target", lambda s: round(100 * s.mean(), 1)),
                  avg_age=("age", "mean"),
                  loyal_pct=("is_loyal", lambda s: round(100 * s.mean(), 1)),
                  business_class_pct=("class_business", lambda s: round(100 * s.mean(), 1)),
                  digital=("digital_mean", "mean"),
                  inflight=("inflight_mean", "mean"),
                  ground=("ground_mean", "mean"))
             .round(2))
print(profile)

# %% [markdown]
# ## 8. Save the model and write results back to PostgreSQL
# Predictions and clusters land in `ml_predictions` so SQL and Power BI can join them on `id`.
# Note: rows with split = 'train' are in-sample predictions; filter on `split = 'test'` for honest metrics.

# %%
joblib.dump({"model": best, "features": FEATURES}, "airline_satisfaction_model.joblib")

out = df[["id", "split", "cluster"]].copy()
out["pred_prob_satisfied"] = best.predict_proba(df[FEATURES])[:, 1].round(4)
out["pred_label"] = (out["pred_prob_satisfied"] >= 0.5).astype(int)
out["actual"] = df["target"]

out.to_sql("ml_predictions", engine, if_exists="replace", index=False, method="multi", chunksize=5000)
print("Wrote", len(out), "rows to ml_predictions")
