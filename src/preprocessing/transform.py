import yaml
from pathlib import Path
import pandas as pd

from src.logging.event_logger import log_message, log_event


BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"
SCHEMA_PATH = CONFIG_DIR / "schema.yaml"


def preprocess(df: pd.DataFrame):
    """
    Prepare data for model ingestion based on customer_7day_summary schema.
    Returns (X, y).
    """

    if df is None or df.empty:
        log_message("Preprocessing skipped: DataFrame empty.")
        log_event("PREPROCESS_SKIPPED", {"reason": "empty_dataframe"})
        return pd.DataFrame(), pd.Series(dtype=float)

    # Drop non-feature columns if present


    # -----------------------------
    # Load schema
    # -----------------------------
    with open(SCHEMA_PATH, "r") as f:
        schema = yaml.safe_load(f)

    features = schema["features"]
    target = schema["target"]

    required_columns = features + [target]
    missing_columns = set(required_columns) - set(df.columns)

    if missing_columns:
        raise Exception(f"Preprocessing error: Missing columns {missing_columns}")

    # -----------------------------
    # Enforce column selection
    # -----------------------------
    X = df[features].copy()
    y = df[target].astype(float)

    # -----------------------------
    # Basic type normalization (SAFE)
    # -----------------------------
    if "discount_applied" in X.columns:
        X["discount_applied"] = X["discount_applied"].astype(bool)

    # Optional: ensure categorical columns are strings
    categorical_cols = schema.get("categorical_features", [])
    for col in categorical_cols:
        if col in X.columns:
            X[col] = X[col].astype(str)

    log_message(f"Preprocessing completed. Rows processed: {len(df)}")
    log_event(
        "PREPROCESS_COMPLETED",
        {
            "rows_processed": len(df),
            "features_used": features,
            "target": target
        }
    )

    return X, y

