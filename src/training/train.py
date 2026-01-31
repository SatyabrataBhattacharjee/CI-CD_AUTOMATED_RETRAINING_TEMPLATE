import yaml
from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

from src.logging.event_logger import log_message, log_event


BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "config"


def train_model(X, y):
    """
    Train model using config settings.
    Returns model, X_test, y_test.
    """

    if X is None or len(X) == 0:
        log_message("Training skipped: No data available.")
        log_event("TRAINING_SKIPPED", {"reason": "empty_dataset"})
        return None, None, None

    # Load training config
    with open(CONFIG_DIR / "training.yaml", "r") as f:
        training_config = yaml.safe_load(f)

    test_size = training_config["split"]["test_size"]
    random_state = training_config["split"]["random_state"]

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state
    )

    # Model instantiation (config-driven later)
    model = LinearRegression()

    model.fit(X_train, y_train)

    log_message(f"Training completed. Train size: {len(X_train)}, Test size: {len(X_test)}")
    log_event("TRAINING_COMPLETED", {
        "train_size": len(X_train),
        "test_size": len(X_test)
    })

    return model, X_test, y_test
