from src.ingestion.pull_batch import pull_batch
from src.validation.sanity_check import validate_buffer
from src.preprocessing.transform import preprocess
from src.training.train import train_model
from src.training.evaluate import evaluate_model

# Step 1: Ingest
pull_batch()

# Step 2: Validate
validate_buffer()

# Step 3: Preprocess
X, y = preprocess()

# Step 4: Train
model, X_test, y_test = train_model(X, y)

# Step 5: Evaluate
metrics = evaluate_model(model, X_test, y_test)

print("Model:", model)
print("Metrics:", metrics)

from src.registry.versioning import register_experiment

run_path = register_experiment(model, metrics)
print("Run path:", run_path)
from src.registry.promotion import promote_model

promoted = promote_model(run_path, metrics)
print("Promoted:", promoted)


