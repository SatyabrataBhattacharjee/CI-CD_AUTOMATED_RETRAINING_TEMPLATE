import json
from datetime import datetime
from pathlib import Path

# Define log file paths
BASE_DIR = Path(__file__).resolve().parents[2]
LOG_DIR = BASE_DIR / "logs"

HUMAN_LOG = LOG_DIR / "retraining.log"
EVENT_LOG = LOG_DIR / "events.jsonl"


def _timestamp():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def log_message(message: str):
    """
    Append a human-readable log message.
    """
    try:
        with open(HUMAN_LOG, "a") as f:
            f.write(f"[{_timestamp()}] {message}\n")
    except Exception:
        # Logging must never crash pipeline
        pass


def log_event(event_type: str, payload: dict):
    """
    Append structured JSON log.
    """
    try:
        event_record = {
            "timestamp": _timestamp(),
            "event": event_type,
            "data": payload
        }

        with open(EVENT_LOG, "a") as f:
            f.write(json.dumps(event_record) + "\n")

    except Exception:
        pass
