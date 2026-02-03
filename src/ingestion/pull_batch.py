import pandas as pd
from sqlalchemy import text
from src.ingestion.db import engine
from src.logging.event_logger import log_message, log_event


MICRO_BATCH_SIZE = 10


def _get_last_processed_id(conn):
    result = conn.execute(
        text("SELECT value FROM pipeline_state WHERE key='last_processed_id'")
    ).fetchone()

    if result is None:
        conn.execute(
            text("INSERT INTO pipeline_state (key, value) VALUES ('last_processed_id', '0')")
        )
        return 0

    return int(result[0])


def _update_last_processed_id(conn, new_id):
    conn.execute(
        text("UPDATE pipeline_state SET value=:val WHERE key='last_processed_id'"),
        {"val": str(new_id)}
    )


def pull_batch():
    """
    Pull micro-batch from Postgres.
    Returns DataFrame or None.
    """

    with engine.begin() as conn:

        last_id = _get_last_processed_id(conn)

        query = text("""
            SELECT * FROM housing_data
            WHERE id > :last_id
            ORDER BY id
            LIMIT :limit
        """)

        df = pd.read_sql(query, conn, params={
            "last_id": last_id,
            "limit": MICRO_BATCH_SIZE
        })

        if df.empty:
            log_message("No new data found in Postgres.")
            log_event("NO_DATA", {"last_id": last_id})
            return None

        new_last_id = df["id"].max()
        _update_last_processed_id(conn, new_last_id)

        log_message(f"Ingested {len(df)} rows from Postgres.")
        log_event("DATA_INGESTED", {
            "rows": len(df),
            "previous_last_id": last_id,
            "new_last_id": new_last_id
        })
        df = df.drop(columns=["id", "created_at"], errors="ignore")


        return df
