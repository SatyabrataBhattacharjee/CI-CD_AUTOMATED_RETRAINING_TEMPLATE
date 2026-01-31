import pandas as pd
import yaml
from pathlib import Path

from src.logging.event_logger import log_message, log_event


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"

BUFFER_PATH = DATA_DIR / "buffer.csv"
SCHEMA_PATH = CONFIG_DIR / "schema.yaml"


def preprocess():
    """
    Load buffer and split into X and y based on schema.
    Always returns DataFrame and Series (possibly empty).
    """

    if not BUFFER_PATH.exists() or BUFFER_PATH.stat().st_size == 0:
        log_message("Preprocessing skipped: Buffer is empty.")
        log_event("PREPROCESS_SKIPPED", {"reason": "empty_buffer"})
        return pd.DataFrame(), pd.Series(dtype=float)

    df = pd.read_csv(BUFFER_PATH)

    if df.empty:
        log_message("Preprocessing skipped: Buffer dataframe empty.")
        log_event("PREPROCESS_SKIPPED", {"reason": "empty_dataframe"})
        return pd.DataFrame(), pd.Series(dtype=float)

    # Load schema
    with open(SCHEMA_PATH, "r") as f:
        schema = yaml.safe_load(f)

    features = schema["features"]
    target = schema["target"]

    required_columns = features + [target]
    missing_columns = set(required_columns) - set(df.columns)

    if missing_columns:
        raise Exception(f"Preprocessing error: Missing columns {missing_columns}")

    X = df[features]
    y = df[target]

    log_message(f"Preprocessing completed. Rows processed: {len(df)}")
    log_event("PREPROCESS_COMPLETED", {"rows_processed": len(df)})

    return X, y
