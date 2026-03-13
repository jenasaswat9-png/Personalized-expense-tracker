from contextlib import contextmanager
from mysql.connector import pooling, Error as MySQLError
from datetime import date, datetime
import os
from dotenv import load_dotenv
from backend.logging_setup import setup_logger
from typing import List, Dict, Optional, Any

load_dotenv()  # read .env in project root

logger = setup_logger("db_helper", log_file=os.getenv("LOG_FILE", "server.log"))

# Pool configuration (ENV or defaults)
_DB_POOL_NAME = os.getenv("DB_POOL_NAME", "expense_pool")
_DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 5))
_DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "root"),
    "database": os.getenv("DB_NAME", "expense_manager"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "pool_name": _DB_POOL_NAME,
    "pool_size": _DB_POOL_SIZE,
}

# Initialize pool on import; raise helpful error if pool can't be created
try:
    pool = pooling.MySQLConnectionPool(**_DB_CONFIG)
    logger.info(f"MySQL pool created (name={_DB_POOL_NAME}, size={_DB_POOL_SIZE})")
except MySQLError as e:
    pool = None
    logger.exception("Failed creating MySQL connection pool: %s", e)


@contextmanager
def get_db_cursor(commit: bool = False):
    """
    Context manager that yields a dictionary cursor from the connection pool.
    Ensures commit on success (if requested), rollback on error, and always
    closes connection/cursor.
    Usage:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(...)
    """
    if pool is None:
        raise RuntimeError("DB pool not initialized. Check DB configuration.")
    conn = None
    cursor = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        yield cursor
        if commit:
            conn.commit()
    except Exception:
        # roll back only if we opened a connection
        try:
            if conn:
                conn.rollback()
        except Exception:
            logger.exception("Failed during rollback")
        raise
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            logger.exception("Failed to close cursor")
        try:
            if conn:
                conn.close()
        except Exception:
            logger.exception("Failed to close connection")


def _normalize_date(d: Any) -> str:
    """
    Accepts date, datetime or string and returns ISO date string YYYY-MM-DD.
    Raises ValueError if not convertible.
    """
    if isinstance(d, date) and not isinstance(d, datetime):
        return d.isoformat()
    if isinstance(d, datetime):
        return d.date().isoformat()
    if isinstance(d, str):
        # assume user passes YYYY-MM-DD; can add more robust parsing if needed
        # keep simple for interview clarity
        return d
    raise ValueError("Invalid date value")


def fetch_expenses_for_date(expense_date: Any) -> List[Dict]:
    """Return list of expense rows for a given date (as dicts)."""
    ed = _normalize_date(expense_date)
    logger.info("fetch_expenses_for_date called with %s", ed)
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM expenses WHERE expense_date = %s", (ed,))
        rows = cur.fetchall()
        return rows or []


def delete_expenses_for_date(expense_date: Any) -> None:
    ed = _normalize_date(expense_date)
    logger.info("delete_expenses_for_date called with %s", ed)
    with get_db_cursor(commit=True) as cur:
        cur.execute("DELETE FROM expenses WHERE expense_date = %s", (ed,))


def insert_expense(expense_date: Any, amount: float, category: str, notes: Optional[str]):
    ed = _normalize_date(expense_date)
    logger.info("insert_expense called date=%s amount=%s category=%s", ed, amount, category)
    with get_db_cursor(commit=True) as cur:
        cur.execute(
            "INSERT INTO expenses (expense_date, amount, category, notes) VALUES (%s, %s, %s, %s)",
            (ed, amount, category, notes),
        )


def fetch_expense_summary(start_date: Any, end_date: Any) -> List[Dict]:
    sd = _normalize_date(start_date)
    ed = _normalize_date(end_date)
    logger.info("fetch_expense_summary called with start=%s end=%s", sd, ed)
    with get_db_cursor() as cur:
        cur.execute(
            """
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE expense_date BETWEEN %s AND %s
            GROUP BY category
            """,
            (sd, ed),
        )
        rows = cur.fetchall()
        return rows or []


# small demo/test when executed directly
if __name__ == "__main__":
    try:
        print(fetch_expenses_for_date("2024-09-30"))
        print(fetch_expense_summary("2024-08-01", "2024-08-05"))
    except Exception as e:
        logger.exception("Demo run failed: %s", e)