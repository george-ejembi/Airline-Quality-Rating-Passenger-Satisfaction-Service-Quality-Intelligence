"""Unsupervised passenger segmentation on service ratings.

The target is used only **after** clusters are formed, to profile them.
"""
from __future__ import annotations

from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from .config import RANDOM_STATE
from .config import RATING_COLS as _RATING_COLS  # local alias

SEG_COLS = _RATING_COLS + ["digital_mean", "inflight_mean", "ground_mean"]


def choose_k(Z: np.ndarray, k_range=range(2, 8),
             sample_size: int = 10_000) -> Tuple[int, pd.Series]:
    """Silhouette-based model selection on a subsample for speed."""
    rng = np.random.RandomState(RANDOM_STATE)
    idx = rng.choice(len(Z), size=min(sample_size, len(Z)), replace=False)
    scores: Dict[int, float] = {}
    for k in k_range:
        km = KMeans(n_clusters=k, n_init=10,
                    random_state=RANDOM_STATE).fit(Z)
        scores[k] = silhouette_score(Z[idx], km.labels_[idx])
    s = pd.Series(scores).round(3)
    return int(s.idxmax()), s


def fit_segments(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, int]:
    """Add a ``cluster`` column and return ``(df, silhouette_series, k)``."""
    Z = StandardScaler().fit_transform(
        SimpleImputer(strategy="median").fit_transform(df[SEG_COLS]))
    k, sil = choose_k(Z)
    df = df.copy()
    df["cluster"] = KMeans(
        n_clusters=k, n_init=10, random_state=RANDOM_STATE
    ).fit_predict(Z)
    return df, sil, k


def profile_clusters(df: pd.DataFrame) -> pd.DataFrame:
    """Post-hoc profiling - the target is used only for description."""
    return (df.groupby("cluster")
              .agg(passengers=("id", "count"),
                   satisfaction_pct=("target",
                                     lambda s: round(100 * s.mean(), 1)),
                   avg_age=("age", "mean"),
                   loyal_pct=("is_loyal",
                              lambda s: round(100 * s.mean(), 1)),
                   business_class_pct=("class_business",
                                       lambda s: round(100 * s.mean(), 1)),
                   digital=("digital_mean", "mean"),
                   inflight=("inflight_mean", "mean"),
                   ground=("ground_mean", "mean"))
              .round(2))