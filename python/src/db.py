"""Database helpers: read the ML training set, write predictions back."""
from __future__ import annotations

import os
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from .config import DEFAULT_DB_URL


def get_engine(url: Optional[str] = None) -> Engine:
    """Return a SQLAlchemy engine. ``DATABASE_URL`` env var wins over argument."""
    url = url or os.getenv("DATABASE_URL", DEFAULT_DB_URL)
    return create_engine(url)


def load_training_set(engine: Optional[Engine] = None) -> pd.DataFrame:
    """Load the ``ml_training_set`` view produced by the SQL layer."""
    engine = engine or get_engine()
    return pd.read_sql("SELECT * FROM ml_training_set", engine)


def write_predictions(df: pd.DataFrame,
                      engine: Optional[Engine] = None,
                      table: str = "ml_predictions") -> int:
    """Persist ``id / split / cluster / pred_*`` back to PostgreSQL.

    Uses ``if_exists='replace'`` so re-runs are idempotent. Returns row count.
    """
    engine = engine or get_engine()
    df.to_sql(table, engine, if_exists="replace",
              index=False, method="multi", chunksize=5000)
    return len(df)