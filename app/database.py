"""
SQLite database for storing call records.
"""

import sqlite3
import json
import logging
from pathlib import Path
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DB_PATH = "data/calls.db"


def get_connection() -> sqlite3.Connection:
    """Get a SQLite connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create the calls table if it doesn't exist."""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                mc_number TEXT,
                carrier_name TEXT,
                load_id TEXT,
                origin TEXT,
                destination TEXT,
                equipment_type TEXT,
                loadboard_rate REAL,
                agreed_rate REAL,
                negotiation_rounds INTEGER DEFAULT 0,
                call_outcome TEXT,
                carrier_sentiment TEXT,
                call_summary TEXT,
                call_duration INTEGER DEFAULT 0
            )
        """)

    logger.info("Database initialized.")


def seed_db(seed_path: str = "data/seed_calls.json") -> None:
    """Seed the database with sample call data if empty."""
    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM calls").fetchone()[0]
        if count > 0:
            logger.info(f"Database already has {count} records. Skipping seed.")
            return

    path = Path(seed_path)
    if not path.exists():
        logger.warning(f"Seed file not found: {seed_path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)

    with get_db() as conn:
        for r in records:
            conn.execute(
                """
                INSERT INTO calls (
                    timestamp, mc_number, carrier_name, load_id, origin,
                    destination, equipment_type, loadboard_rate, agreed_rate,
                    negotiation_rounds, call_outcome, carrier_sentiment,
                    call_summary, call_duration
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    r.get("timestamp"),
                    r.get("mc_number"),
                    r.get("carrier_name"),
                    r.get("load_id"),
                    r.get("origin"),
                    r.get("destination"),
                    r.get("equipment_type"),
                    r.get("loadboard_rate"),
                    r.get("agreed_rate"),
                    r.get("negotiation_rounds"),
                    r.get("call_outcome"),
                    r.get("carrier_sentiment"),
                    r.get("call_summary"),
                    r.get("call_duration"),
                ),
            )

    logger.info(f"Seeded database with {len(records)} call records.")
