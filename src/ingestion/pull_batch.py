import pandas as pd
import yaml
from pathlib import Path

from src.logging.event_logger import log_message, log_event


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"

LAKEHOUSE_PATH = DATA_DIR / "lakehouse.csv"
BUFFER_PATH = DATA_DIR / "buffer.csv"
POINTER_PATH = DATA_DIR / "pointer.txt"


def pull_batch():
    """
    Pull micro-batch from lakehouse into buffer.
    Returns number of rows pulled.
    """

    # Load pipeline config
    with open(CONFIG_DIR / "pipeline.yaml", "r") as f:
        pipeline_config = yaml.safe_load(f)

    micro_batch_size = pipeline_config["micro_batch_size"]

    # Load pointer
    with open(POINTER_PATH, "r") as f:
        pointer = int(f.read().strip())

    # Load lakehouse
    lakehouse_df = pd.read_csv(LAKEHOUSE_PATH)

    if pointer >= len(lakehouse_df):
        log_message("No new data available in lakehouse.")
        log_event("NO_DATA", {"pointer": pointer})
        return 0

    # Slice batch
    end_pointer = min(pointer + micro_batch_size, len(lakehouse_df))
    batch_df = lakehouse_df.iloc[pointer:end_pointer]

    # Append to buffer
    if BUFFER_PATH.exists() and BUFFER_PATH.stat().st_size > 0:
        batch_df.to_csv(BUFFER_PATH, mode="a", header=False, index=False)
    else:
        batch_df.to_csv(BUFFER_PATH, mode="w", header=True, index=False)

    # Update pointer
    with open(POINTER_PATH, "w") as f:
        f.write(str(end_pointer))

    rows_pulled = len(batch_df)

    log_message(f"Ingested {rows_pulled} rows into buffer.")
    log_event("DATA_INGESTED", {
        "rows_pulled": rows_pulled,
        "pointer_before": pointer,
        "pointer_after": end_pointer
    })

    return rows_pulled
