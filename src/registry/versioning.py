import json
import joblib
from datetime import datetime
from pathlib import Path

from src.logging.event_logger import log_message, log_event


BASE_DIR = Path(__file__).resolve().parents[2]
MODELS_DIR = BASE_DIR / "models"
EXPERIMENTS_DIR = MODELS_DIR / "experiments"


def register_experiment(model, metrics):
    """
    Save model and metrics to a timestamped experiment folder.
    Returns run_path.
    """

    if model is None:
        log_message("Experiment registration skipped: No model.")
        log_event("REGISTRATION_SKIPPED", {"reason": "no_model"})
        return None

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    run_dir = EXPERIMENTS_DIR / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    model_path = run_dir / "model.pkl"
    metrics_path = run_dir / "metrics.json"

    # Save model
    joblib.dump(model, model_path)

    # Save metrics
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=4)

    log_message(f"Experiment registered at {run_dir.name}")
    log_event("EXPERIMENT_REGISTERED", {
        "run": run_dir.name,
        "metrics": metrics
    })

    return run_dir
