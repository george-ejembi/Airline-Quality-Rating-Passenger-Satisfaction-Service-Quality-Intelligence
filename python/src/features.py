"""Leakage-safe feature engineering.

Every transform is a function of a single passenger's own record - no
cross-row statistics are fit here, so fitting on train and applying to test
is automatically safe.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from .config import DIGITAL, DROP_COLS, GROUND, INFLIGHT, RATING_COLS


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add row-wise derived features to a copy of ``df``."""
    d = df.copy()
    r = d[RATING_COLS]

    # --- experience profile --------------------------------------------- #
    d["rating_min"] = r.min(axis=1)             # worst touchpoint
    d["rating_std"] = r.std(axis=1)             # inconsistency across journey
    d["n_rated"] = r.notna().sum(axis=1)
    d["n_low_ratings"] = (r <= 2).sum(axis=1)   # pain points
    d["n_high_ratings"] = (r >= 4).sum(axis=1)  # delight points
    d["pct_low_ratings"] = d["n_low_ratings"] / d["n_rated"].replace(0, np.nan)

    # --- stage means & gap ---------------------------------------------- #
    d["digital_mean"] = d[DIGITAL].mean(axis=1)
    d["inflight_mean"] = d[INFLIGHT].mean(axis=1)
    d["ground_mean"] = d[GROUND].mean(axis=1)
    d["digital_vs_inflight"] = d["digital_mean"] - d["inflight_mean"]

    # --- skew-corrected transforms -------------------------------------- #
    d["log_dep_delay"] = np.log1p(d["departure_delay"].clip(lower=0))
    d["log_distance"] = np.log1p(d["flight_distance"])
    d["long_delay_flag"] = (d["departure_delay"] > 60).astype(int)

    # --- interactions --------------------------------------------------- #
    d["loyal_x_business_travel"] = d["is_loyal"] * d["is_business_travel"]
    d["business_class_x_travel"] = d["class_business"] * d["is_business_travel"]
    d["age_x_digital"] = d["age"] * d["digital_mean"]

    return d


def feature_columns(df: pd.DataFrame) -> List[str]:
    """Return all columns except IDs, target, split and redundant features."""
    return [c for c in df.columns if c not in DROP_COLS]


def split(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return ``(train, test)`` using the reproducible hash split from SQL."""
    return df[df["split"] == "train"].copy(), df[df["split"] == "test"].copy()


def prepare(df: pd.DataFrame) -> Dict[str, object]:
    """Full preparation step: engineer features, list columns, split.

    Returns a dict with keys:
        df, features, train, test, X_train, y_train, X_test, y_test
    """
    df = add_features(df)
    feats = feature_columns(df)
    train, test = split(df)
    return {
        "df": df,
        "features": feats,
        "train": train,
        "test": test,
        "X_train": train[feats],
        "y_train": train["target"],
        "X_test": test[feats],
        "y_test": test["target"],
    }