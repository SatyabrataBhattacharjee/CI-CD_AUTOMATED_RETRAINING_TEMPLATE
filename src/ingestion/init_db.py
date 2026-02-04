from sqlalchemy import text
from src.ingestion.db import engine

def init_database():
    with engine.begin() as conn:

        # -----------------------------
        # CUSTOMER 7-DAY SUMMARY TABLE
        # -----------------------------
        conn.execute(text("""
          CREATE TABLE IF NOT EXISTS customer_7day_summary (

    -- Numerical (mean aggregated)
    quantity FLOAT CHECK (quantity >= 0),
    line_net_amount FLOAT CHECK (line_net_amount >= 0),
    total_items FLOAT CHECK (total_items >= 0),
    total_cost FLOAT CHECK (total_cost >= 0),

    -- Categorical (mode aggregated)
    loyalty_status TEXT,
    payment_method TEXT,
    discount_applied BOOLEAN
);

        """))

        # -----------------------------
        # PIPELINE STATE TABLE
        # -----------------------------
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS pipeline_state (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        """))
