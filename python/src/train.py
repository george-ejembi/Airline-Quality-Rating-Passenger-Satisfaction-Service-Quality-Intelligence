"""Model zoo, cross-validation and hyper-parameter tuning."""
from __future__ import annotations

from typing import Dict, Tuple

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (
    RandomizedSearchCV, StratifiedKFold, cross_validate,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .config import (
    CV_FOLDS, RANDOM_STATE, SCORING, TUNING_CV_FOLDS, TUNING_N_ITER,
)


def build_models() -> Dict[str, object]:
    """Baseline + three candidates.

    Linear models get impute + scale inside a Pipeline (leakage-safe);
    tree models receive NaN directly.
    """
    return {
        "baseline": DummyClassifier(strategy="prior"),
        "logreg": Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("sc", StandardScaler()),
            ("clf", LogisticRegression(max_iter=2000, C=1.0)),
        ]),
        "random_forest": Pipeline([
            ("imp", SimpleImputer(strategy="median")),
            ("clf", RandomForestClassifier(
                n_estimators=300, min_samples_leaf=5,
                n_jobs=-1, random_state=RANDOM_STATE)),
        ]),
        "hist_gb": HistGradientBoostingClassifier(random_state=RANDOM_STATE),
    }


def cross_validate_models(models, X_train, y_train) -> pd.DataFrame:
    """5-fold CV on the training split only. Returns a tidy results DataFrame."""
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True,
                         random_state=RANDOM_STATE)
    rows = []
    for name, model in models.items():
        s = cross_validate(model, X_train, y_train, cv=cv,
                           scoring=SCORING, n_jobs=-1)
        rows.append({
            "model": name,
            **{k: round(s[f"test_{k}"].mean(), 4) for k in SCORING},
            "auc_sd": round(s["test_roc_auc"].std(), 4),
        })
    return (pd.DataFrame(rows)
            .sort_values("roc_auc", ascending=False)
            .reset_index(drop=True))


def tune_hist_gb(
    X_train, y_train,
) -> Tuple[HistGradientBoostingClassifier, dict, float]:
    """Random search over depth / leaf / L2 / iter to control variance.

    Returns ``(best_estimator, best_params, best_cv_score)``.
    """
    param_dist = {
        "learning_rate": [0.03, 0.05, 0.1, 0.2],
        "max_depth": [None, 4, 6, 8],
        "max_leaf_nodes": [15, 31, 63],
        "min_samples_leaf": [20, 50, 100],
        "l2_regularization": [0.0, 0.1, 1.0, 10.0],
        "max_iter": [200, 400, 600],
    }
    search = RandomizedSearchCV(
        HistGradientBoostingClassifier(random_state=RANDOM_STATE,
                                       early_stopping=True),
        param_dist,
        n_iter=TUNING_N_ITER,
        scoring="roc_auc",
        cv=TUNING_CV_FOLDS,
        n_jobs=-1,
        random_state=RANDOM_STATE,
    )
    search.fit(X_train, y_train)
    return search.best_estimator_, search.best_params_, search.best_score_