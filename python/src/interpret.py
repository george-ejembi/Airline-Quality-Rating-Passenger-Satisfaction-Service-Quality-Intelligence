"""Model interpretation: permutation importance, logistic coefficients, SHAP."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.inspection import permutation_importance

from .config import OUTPUTS_DIR, RANDOM_STATE


def permutation_importance_plot(
    model, X_test, y_test, features,
    top_n: int = 15, out_dir: Path = OUTPUTS_DIR,
) -> pd.Series:
    """Model-agnostic importance on held-out data (drop in ROC-AUC)."""
    perm = permutation_importance(
        model, X_test, y_test, scoring="roc_auc",
        n_repeats=5, random_state=RANDOM_STATE, n_jobs=-1)
    imp = (pd.Series(perm.importances_mean, index=features)
             .sort_values(ascending=False)
             .head(top_n))
    ax = imp[::-1].plot(kind="barh", figsize=(7, 5),
                        title="Permutation importance (drop in ROC-AUC)")
    ax.set_xlabel("mean drop in ROC-AUC")
    plt.tight_layout()
    plt.savefig(out_dir / "permutation_importance.png",
                dpi=130, bbox_inches="tight")
    plt.close()
    return imp


def logistic_coefficients_plot(
    logreg_pipeline, features,
    top_n: int = 8, out_dir: Path = OUTPUTS_DIR,
) -> pd.Series:
    """Signed, standardised coefficients of the logistic baseline."""
    coefs = pd.Series(logreg_pipeline.named_steps["clf"].coef_[0],
                      index=features).sort_values()
    shown = pd.concat([coefs.head(top_n), coefs.tail(top_n)])
    ax = shown.plot(kind="barh", figsize=(7, 5),
                    title="Logistic regression coefficients")
    ax.axvline(0, color="black", linewidth=0.8)
    plt.tight_layout()
    plt.savefig(out_dir / "logreg_coefficients.png",
                dpi=130, bbox_inches="tight")
    plt.close()
    return coefs


def shap_summary(
    model, X_train, X_test,
    sample_n: int = 2000, background_n: int = 200,
    out_dir: Path = OUTPUTS_DIR,
) -> Optional[Path]:
    """SHAP summary plot. Returns path, or ``None`` if ``shap`` is missing."""
    try:
        import shap
    except ImportError:
        print("SHAP not installed - skipping.")
        return None

    sample = X_test.sample(min(sample_n, len(X_test)),
                           random_state=RANDOM_STATE)
    explainer = shap.Explainer(model.predict,
                               shap.sample(X_train, background_n))
    shap.summary_plot(explainer(sample), sample, show=False)
    path = out_dir / "shap_summary.png"
    plt.tight_layout()
    plt.savefig(path, dpi=130, bbox_inches="tight")
    plt.close()
    return path