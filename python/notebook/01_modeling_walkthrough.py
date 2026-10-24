# %% [markdown]
# # Airline Passenger Satisfaction — Modeling Walkthrough
#
# **Thin narrative notebook.** All heavy logic lives in `python/src/`; this
# notebook imports those modules so the code is testable, reusable and callable
# from the CLI (`python -m src.pipeline`).
#
# **Run order**
# 1. From `python/`: `python -m src.pipeline` (headless, writes all artefacts)
# 2. Or open this file in VS Code — `# %%` opens as a notebook — and step through.

# %%
# Make the sibling `src` package importable when running from notebooks/.
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent))

import joblib
import pandas as pd

from src import db, features, train, evaluate, interpret, segment
from src.config import MODEL_PATH

pd.set_option("display.width", 140)

# %% [markdown]
# ## 1. Load the training set from PostgreSQL

# %%
raw = db.load_training_set()
print(raw.shape)
print(raw["target"].value_counts(normalize=True).round(3))
print(raw.isna().mean().sort_values(ascending=False).head(10).round(3))

# %% [markdown]
# ## 2. Feature engineering + reproducible train/test split

# %%
prep = features.prepare(raw)
feats = prep["features"]
X_train, y_train = prep["X_train"], prep["y_train"]
X_test, y_test = prep["X_test"], prep["y_test"]
print(len(feats), "features")

# %% [markdown]
# ## 3. Cross-validation on the training split only

# %%
models = train.build_models()
cv_results = train.cross_validate_models(models, X_train, y_train)
cv_results

# %% [markdown]
# ## 4. Tune gradient boosting

# %%
best, best_params, best_cv = train.tune_hist_gb(X_train, y_train)
best_params, round(best_cv, 4)

# %% [markdown]
# ## 5. Evaluation on the untouched test set

# %%
metrics = evaluate.evaluate_on_test(best, X_test, y_test)
{k: metrics[k] for k in ("roc_auc", "pr_auc", "f1", "accuracy")}

# %%
evaluate.plot_diagnostics(y_test, metrics["y_pred"], metrics["y_proba"])
print(metrics["report"])

# %% [markdown]
# ## 6. Interpretation

# %%
imp = interpret.permutation_importance_plot(best, X_test, y_test, feats)
imp

# %%
logreg = models["logreg"].fit(X_train, y_train)
interpret.logistic_coefficients_plot(logreg, feats)

# %%
interpret.shap_summary(best, X_train, X_test)

# %% [markdown]
# ## 7. Passenger segmentation

# %%
df_seg, sil, k = segment.fit_segments(prep["df"])
segment.profile_clusters(df_seg)

# %% [markdown]
# ## 8. Persist artefacts

# %%
joblib.dump({"model": best, "features": feats}, MODEL_PATH)

out = df_seg[["id", "split", "cluster"]].copy()
out["pred_prob_satisfied"] = best.predict_proba(df_seg[feats])[:, 1].round(4)
out["pred_label"] = (out["pred_prob_satisfied"] >= 0.5).astype(int)
out["actual"] = df_seg["target"]
n = db.write_predictions(out)
print(f"Wrote {n:,} rows to ml_predictions")