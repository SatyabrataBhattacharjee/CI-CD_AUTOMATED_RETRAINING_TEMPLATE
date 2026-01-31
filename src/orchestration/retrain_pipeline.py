import yaml
from pathlib import Path

from src.ingestion.pull_batch import pull_batch
from src.validation.sanity_check import validate_buffer
from src.preprocessing.transform import preprocess
from src.training.train import train_model
from src.training.evaluate import evaluate_model
from src.registry.versioning import register_experiment
from src.registry.promotion import promote_model
from src.logging.event_logger import log_message, log_event


BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
BUFFER_PATH = DATA_DIR / "buffer.csv"


def clear_buffer():
    if BUFFER_PATH.exists():
        BUFFER_PATH.unlink()
        log_message("Buffer cleared after promotion.")
        log_event("BUFFER_CLEARED", {})


def main():

    log_message("Retraining pipeline started.")
    log_event("PIPELINE_STARTED", {})

    # Step 1: Ingestion
    rows_pulled = pull_batch()
    if rows_pulled == 0:
        log_message("Pipeline exiting: No new data.")
        return

    # Step 2: Validation
    valid = validate_buffer()
    if not valid:
        log_message("Pipeline exiting: Validation skipped or failed.")
        return

    # Step 3: Preprocessing
    X, y = preprocess()
    if len(X) == 0:
        log_message("Pipeline exiting: No data after preprocessing.")
        return

    # Step 4: Training
    model, X_test, y_test = train_model(X, y)
    if model is None:
        log_message("Pipeline exiting: Training skipped.")
        return

    # Step 5: Evaluation
    metrics = evaluate_model(model, X_test, y_test)
    if not metrics:
        log_message("Pipeline exiting: Evaluation skipped.")
        return

    # Step 6: Register Experiment
    run_path = register_experiment(model, metrics)

    # Step 7: Promotion
    promoted = promote_model(run_path, metrics)

    # Step 8: Clear Buffer if configured
    with open(CONFIG_DIR / "pipeline.yaml", "r") as f:
        pipeline_config = yaml.safe_load(f)

    if promoted and pipeline_config.get("clear_buffer_on_promotion", False):
        clear_buffer()

    log_message("Retraining pipeline completed.")
    log_event("PIPELINE_COMPLETED", {"promoted": promoted})


if __name__ == "__main__":
    main()
