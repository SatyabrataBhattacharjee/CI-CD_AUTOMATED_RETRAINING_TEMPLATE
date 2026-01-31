import pandas as pd
import yaml
from pathlib import Path

from src.logging.event_logger import log_message, log_event


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"

BUFFER_PATH = DATA_DIR / "buffer.csv"
SCHEMA_PATH = CONFIG_DIR / "schema.yaml"


def validate_buffer():
    """
    Validate buffer against schema contract.
    Raises Exception if validation fails.
    """

    if not BUFFER_PATH.exists() or BUFFER_PATH.stat().st_size == 0:
        log_message("Validation skipped: Buffer is empty.")
        log_event("VALIDATION_SKIPPED", {"reason": "empty_buffer"})
        return False


    # Load schema
    with open(SCHEMA_PATH, "r") as f:
        schema = yaml.safe_load(f)

    required_columns = schema["features"] + [schema["target"]]
    dtype_contract = schema["dtypes"]
    constraints = schema.get("constraints", {})

    # Load buffer
    df = pd.read_csv(BUFFER_PATH)

    # 1️⃣ Column presence check
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        log_message(f"Validation failed: Missing columns {missing_columns}")
        log_event("VALIDATION_FAILED", {"reason": "missing_columns", "columns": list(missing_columns)})
        raise Exception(f"Missing columns: {missing_columns}")

    # 2️⃣ Null check
    if df[required_columns].isnull().any().any():
        log_message("Validation failed: Null values detected.")
        log_event("VALIDATION_FAILED", {"reason": "null_values"})
        raise Exception("Null values detected in buffer.")

    # 3️⃣ Type compatibility check
    for col, expected_type in dtype_contract.items():
        if col in df.columns:
            if expected_type == "int" and not pd.api.types.is_integer_dtype(df[col]):
                raise Exception(f"Column {col} is not integer type.")
            if expected_type == "float" and not pd.api.types.is_numeric_dtype(df[col]):
                raise Exception(f"Column {col} is not numeric type.")

    # 4️⃣ Constraint checks (min only for now)
    for col, rule in constraints.items():
        if "min" in rule:
            if (df[col] < rule["min"]).any():
                log_message(f"Validation failed: {col} below minimum.")
                log_event("VALIDATION_FAILED", {"reason": "min_constraint", "column": col})
                raise Exception(f"{col} has values below minimum.")

    log_message("Validation passed successfully.")
    log_event("VALIDATION_PASSED", {"rows_validated": len(df)})

    return True
