import yaml
from pathlib import Path
import pandas as pd

from src.logging.event_logger import log_message, log_event


BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"
SCHEMA_PATH = CONFIG_DIR / "schema.yaml"


def preprocess(df: pd.DataFrame):
    """
    Split incoming DataFrame into X and y based on schema.
    Returns (X, y).
    """

    if df is None or df.empty:
        log_message("Preprocessing skipped: DataFrame empty.")
        log_event("PREPROCESS_SKIPPED", {"reason": "empty_dataframe"})
        return pd.DataFrame(), pd.Series(dtype=float)
    df = df.drop(columns=["id", "created_at"], errors="ignore")

    # Load schema
    with open(SCHEMA_PATH, "r") as f:
        schema = yaml.safe_load(f)

    features = schema["features"]
    target = schema["target"]

    required_columns = features + [target]
    missing_columns = set(required_columns) - set(df.columns)

    if missing_columns:
        raise Exception(f"Preprocessing error: Missing columns {missing_columns}")

    # Drop DB-specific columns like id, created_at if present
    df = df.copy()

    X = df[features]
    y = df[target]

    log_message(f"Preprocessing completed. Rows processed: {len(df)}")
    log_event("PREPROCESS_COMPLETED", {"rows_processed": len(df)})

    return X, y
