import json
import shutil
from pathlib import Path

from src.logging.event_logger import log_message, log_event


BASE_DIR = Path(__file__).resolve().parents[2]
MODELS_DIR = BASE_DIR / "models"
PROMOTED_DIR = MODELS_DIR / "promoted"
CURRENT_MODEL_FILE = MODELS_DIR / "current_model.txt"


def _get_next_version():
    existing = list(PROMOTED_DIR.glob("v*.pkl"))
    if not existing:
        return 1
    versions = [int(f.stem.replace("v", "")) for f in existing]
    return max(versions) + 1


def promote_model(run_path, new_metrics):
    PROMOTED_DIR.mkdir(parents=True, exist_ok=True)

    """
    Promote model if RMSE improves.
    """

    if run_path is None:
        return False

    new_rmse = new_metrics.get("rmse")
    if new_rmse is None:
        return False

    # If no current model → promote immediately
    if not CURRENT_MODEL_FILE.exists() or CURRENT_MODEL_FILE.stat().st_size == 0:

        version = _get_next_version()
        model_dest = PROMOTED_DIR / f"v{version}.pkl"
        metrics_dest = PROMOTED_DIR / f"v{version}_metrics.json"

        shutil.copy(run_path / "model.pkl", model_dest)
        shutil.copy(run_path / "metrics.json", metrics_dest)

        CURRENT_MODEL_FILE.write_text(model_dest.name)

        log_message(f"First model promoted as {model_dest.name}")
        log_event("MODEL_PROMOTED", {
            "version": model_dest.name,
            "rmse": new_rmse
        })

        return True

    # Load current metrics
    current_version = CURRENT_MODEL_FILE.read_text().strip()
    current_metrics_file = PROMOTED_DIR / current_version.replace(".pkl", "_metrics.json")

    with open(current_metrics_file, "r") as f:
        current_metrics = json.load(f)

    current_rmse = current_metrics.get("rmse")

    # Compare
    if new_rmse < current_rmse:

        version = _get_next_version()
        model_dest = PROMOTED_DIR / f"v{version}.pkl"
        metrics_dest = PROMOTED_DIR / f"v{version}_metrics.json"

        shutil.copy(run_path / "model.pkl", model_dest)
        shutil.copy(run_path / "metrics.json", metrics_dest)

        CURRENT_MODEL_FILE.write_text(model_dest.name)

        log_message(f"New model promoted as {model_dest.name}")
        log_event("MODEL_PROMOTED", {
            "version": model_dest.name,
            "rmse": new_rmse
        })

        return True

    log_message("Model not promoted (no improvement).")
    log_event("PROMOTION_REJECTED", {
        "new_rmse": new_rmse,
        "current_rmse": current_rmse
    })

    return False
