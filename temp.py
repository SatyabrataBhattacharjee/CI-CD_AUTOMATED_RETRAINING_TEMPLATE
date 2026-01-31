import numpy as np
import pandas as pd
from pathlib import Path

# -----------------------------
# Config
# -----------------------------
N = 1200  # Change to 2000, 5000, etc.
np.random.seed(42)

from pathlib import Path

BASE_DIR = Path.cwd()

DATA_DIR = BASE_DIR / "data"
LAKEHOUSE_PATH = DATA_DIR / "lakehouse.csv"
POINTER_PATH = DATA_DIR / "pointer.txt"
BUFFER_PATH = DATA_DIR / "buffer.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)

print("Saving lakehouse to:", LAKEHOUSE_PATH)


# -----------------------------
# Feature Generation
# -----------------------------
size = np.random.randint(700, 3000, N)

bedrooms = np.clip(
    (size // 400) + np.random.randint(0, 2, N),
    1, 6
)

age = np.random.randint(0, 40, N)

location_score = np.round(
    np.random.uniform(5.5, 9.5, N),
    2
)

income_index = np.round(
    0.7 + (location_score - 5.5) * 0.12 +
    np.random.normal(0, 0.05, N),
    2
)

# -----------------------------
# Price Formula
# -----------------------------
base_price = (
    size * 140 +
    bedrooms * 12000 -
    age * 1500 +
    location_score * 18000 +
    income_index * 50000
)

noise = np.random.normal(0, 20000, N)

price = np.round(base_price + noise, 0)

# -----------------------------
# DataFrame
# -----------------------------
df = pd.DataFrame({
    "size": size,
    "bedrooms": bedrooms,
    "age": age,
    "location_score": location_score,
    "income_index": income_index,
    "price": price
})

# -----------------------------
# Save to lakehouse
# -----------------------------
df.to_csv(LAKEHOUSE_PATH, index=False)

# Reset pointer to 0
POINTER_PATH.write_text("0")

# Clear buffer if exists
if BUFFER_PATH.exists():
    BUFFER_PATH.unlink()

print("Lakehouse regenerated successfully.")
print("Saving lakehouse to:", LAKEHOUSE_PATH)

print(f"Rows generated: {len(df)}")
print(f"Saved to: {LAKEHOUSE_PATH}")
