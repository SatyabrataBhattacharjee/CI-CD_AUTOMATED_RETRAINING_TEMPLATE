import numpy as np
from sklearn.metrics import mean_squared_error

from src.logging.event_logger import log_message, log_event


def evaluate_model(model, X_test, y_test):
    """
    Evaluate trained model.
    Returns metrics dictionary.
    """

    if model is None:
        log_message("Evaluation skipped: No trained model.")
        log_event("EVALUATION_SKIPPED", {"reason": "no_model"})
        return {}

    if X_test is None or len(X_test) == 0:
        log_message("Evaluation skipped: No test data.")
        log_event("EVALUATION_SKIPPED", {"reason": "no_test_data"})
        return {}

    predictions = model.predict(X_test)

    mse = mean_squared_error(y_test, predictions)
    rmse = float(np.sqrt(mse))

    metrics = {
        "rmse": rmse
    }

    log_message(f"Evaluation completed. RMSE: {rmse:.4f}")
    log_event("EVALUATION_COMPLETED", metrics)

    return metrics
