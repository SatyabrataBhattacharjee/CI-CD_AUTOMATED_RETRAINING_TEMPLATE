import yaml
from pathlib import Path

from src.ingestion.pull_batch import pull_batch
from src.validation.sanity_check import validate_df
from src.preprocessing.transform import preprocess
from src.training.train import train_model
from src.training.evaluate import evaluate_model
from src.registry.versioning import register_experiment
from src.registry.promotion import promote_model
from src.logging.event_logger import log_message, log_event
from src.ingestion.init_db import init_database


BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"


def main():

    log_message("Retraining pipeline started.")
    log_event("PIPELINE_STARTED", {})

    # Step 0: Ensure DB schema exists
    init_database()

    # Step 1: Ingestion (Postgres → DataFrame)
    df = pull_batch()
    if df is None or df.empty:
        log_message("Pipeline exiting: No new data.")
        return

    # Step 2: Validation
    valid = validate_df(df)
    if not valid:
        log_message("Pipeline exiting: Validation failed.")
        return

    # Step 3: Preprocessing
    X, y = preprocess(df)
    if X is None or len(X) == 0:
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

    log_message("Retraining pipeline completed.")
    log_event("PIPELINE_COMPLETED", {"promoted": promoted})


if __name__ == "__main__":
    main()
