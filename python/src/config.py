"""Central configuration - constants, paths and feature groups.

Keeping these in one place means the notebook, the CLI and any downstream
consumer all agree on the same feature list, random seed and file locations.
"""
from __future__ import annotations

from pathlib import Path

# --------------------------------------------------------------------------- #
# Reproducibility
# --------------------------------------------------------------------------- #
RANDOM_STATE: int = 42

# --------------------------------------------------------------------------- #
# Project paths (this file lives at <project>/src/config.py)
# --------------------------------------------------------------------------- #
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
MODELS_DIR: Path = PROJECT_ROOT / "models"
OUTPUTS_DIR: Path = PROJECT_ROOT / "outputs"
MODELS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH: Path = MODELS_DIR / "airline_satisfaction_model.joblib"

# --------------------------------------------------------------------------- #
# Database
# --------------------------------------------------------------------------- #
DEFAULT_DB_URL: str = (
    "postgresql+psycopg2://user:password@localhost:5432/airline"
)

# --------------------------------------------------------------------------- #
# Feature groups (must match the SQL clean view)
# --------------------------------------------------------------------------- #
RATING_COLS = [
    "time_convenience", "online_booking", "checkin", "online_boarding",
    "gate_location", "onboard_service", "seat_comfort", "leg_room",
    "cleanliness", "food_drink", "inflight_service", "wifi",
    "entertainment", "baggage",
]

DIGITAL = ["online_booking", "online_boarding", "wifi"]
INFLIGHT = [
    "seat_comfort", "leg_room", "food_drink", "inflight_service",
    "entertainment", "cleanliness", "onboard_service",
]
GROUND = ["checkin", "gate_location", "baggage", "time_convenience"]

# Columns removed from the feature matrix after feature engineering.
DROP_COLS = [
    "id", "target", "split",
    # redundant with departure_delay
    "arrival_delay", "arr_delayed_flag", "dep_delayed_flag",
    # SQL composites duplicate raw ratings once engineered features exist
    "avg_service_score", "digital_score", "inflight_score", "ground_score",
]

# --------------------------------------------------------------------------- #
# CV / tuning
# --------------------------------------------------------------------------- #
CV_FOLDS: int = 5
TUNING_N_ITER: int = 20
TUNING_CV_FOLDS: int = 3

SCORING = {
    "roc_auc": "roc_auc",
    "pr_auc": "average_precision",
    "f1": "f1",
    "accuracy": "accuracy",
}