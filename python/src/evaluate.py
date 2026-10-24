"""Hold-out evaluation and diagnostic plots."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import matplotlib
matplotlib.use("Agg")          # safe headless default; notebook can override
import matplotlib.pyplot as plt
from sklearn.metrics import (
    ConfusionMatrixDisplay, RocCurveDisplay,
    accuracy_score, average_precision_score, classification_report,
    f1_score, roc_auc_score,
)

from .config import OUTPUTS_DIR


def evaluate_on_test(model, X_test, y_test,
                     threshold: float = 0.5) -> Dict:
    """Compute headline metrics on the untouched test set."""
    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= threshold).astype(int)
    return {
        "roc_auc": round(roc_auc_score(y_test, proba), 4),
        "pr_auc": round(average_precision_score(y_test, proba), 4),
        "f1": round(f1_score(y_test, pred), 4),
        "accuracy": round(accuracy_score(y_test, pred), 4),
        "report": classification_report(
            y_test, pred, target_names=["not satisfied", "satisfied"]),
        "y_proba": proba,
        "y_pred": pred,
    }


def plot_diagnostics(y_test, y_pred, y_proba,
                     out_dir: Path = OUTPUTS_DIR) -> Path:
    """Save confusion matrix + ROC curve side by side; return path."""
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ConfusionMatrixDisplay.from_predictions(
        y_test, y_pred, ax=ax[0], colorbar=False)
    RocCurveDisplay.from_predictions(y_test, y_proba, ax=ax[1])
    fig.tight_layout()
    path = out_dir / "test_diagnostics.png"
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return path


def save_metrics(metrics: Dict, out_dir: Path = OUTPUTS_DIR) -> Path:
    """Persist scalar metrics to JSON (skips vectors and free-form reports)."""
    keep = {k: v for k, v in metrics.items()
            if isinstance(v, (int, float, str))}
    path = out_dir / "test_metrics.json"
    with open(path, "w") as f:
        json.dump(keep, f, indent=2)
    return path