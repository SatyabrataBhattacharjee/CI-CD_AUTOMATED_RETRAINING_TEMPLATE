from sqlalchemy import text
from src.ingestion.db import engine

def init_database():
    with engine.begin() as conn:

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS housing_data (
                id SERIAL PRIMARY KEY,
                size INTEGER,
                bedrooms INTEGER,
                age INTEGER,
                location_score FLOAT,
                income_index FLOAT,
                price FLOAT,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS pipeline_state (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        """))
