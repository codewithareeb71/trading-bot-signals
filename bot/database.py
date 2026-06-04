import sqlite3
from datetime import datetime
from typing import List, Optional, Dict

from .config import DB_PATH, SIGNALS_ENABLED
from .logger import logger

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    joined_at TEXT,
    receive_signals INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    entry_time TEXT NOT NULL,
    expiry_time TEXT NOT NULL,
    confidence REAL NOT NULL,
    technical_reasoning TEXT NOT NULL,
    risk_warning TEXT NOT NULL,
    trend TEXT NOT NULL,
    price REAL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database() -> None:
    conn = get_connection()
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
        if get_setting("signals_enabled") is None:
            set_setting("signals_enabled", str(int(SIGNALS_ENABLED)))
    except Exception as exc:
        logger.exception("Failed to initialize database: %s", exc)
        raise
    finally:
        conn.close()


def save_user(user_id: int, username: str, first_name: str, last_name: str) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users(user_id, username, first_name, last_name, joined_at) VALUES (?, ?, ?, ?, ?)"
            "ON CONFLICT(user_id) DO UPDATE SET username = excluded.username, first_name = excluded.first_name, last_name = excluded.last_name",
            (user_id, username, first_name, last_name, datetime.utcnow().isoformat()),
        )
        conn.commit()
    except Exception:
        logger.exception("Unable to save user %s", user_id)
    finally:
        conn.close()


def save_signal(signal_data: Dict) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO signals(symbol, signal_type, entry_time, expiry_time, confidence, technical_reasoning, risk_warning, trend, price, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                signal_data["symbol"],
                signal_data["signal_type"],
                signal_data["entry_time"],
                signal_data["expiry_time"],
                signal_data["confidence"],
                signal_data["technical_reasoning"],
                signal_data["risk_warning"],
                signal_data["trend"],
                signal_data.get("price"),
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()
    except Exception:
        logger.exception("Unable to save signal %s", signal_data)
    finally:
        conn.close()


def list_recent_signals(limit: int = 10) -> List[sqlite3.Row]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM signals ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return rows
    except Exception:
        logger.exception("Unable to fetch recent signals")
        return []
    finally:
        conn.close()


def list_users() -> List[sqlite3.Row]:
    conn = get_connection()
    try:
        return conn.execute("SELECT * FROM users ORDER BY joined_at DESC").fetchall()
    except Exception:
        logger.exception("Unable to fetch users")
        return []
    finally:
        conn.close()


def get_setting(key: str) -> Optional[str]:
    conn = get_connection()
    try:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else None
    except Exception:
        logger.exception("Unable to read setting %s", key)
        return None
    finally:
        conn.close()


def set_setting(key: str, value: str) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO settings(key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        conn.commit()
    except Exception:
        logger.exception("Unable to set setting %s", key)
    finally:
        conn.close()


def get_statistics() -> Dict[str, int]:
    conn = get_connection()
    try:
        total = conn.execute("SELECT COUNT(*) as count FROM signals").fetchone()["count"]
        bullish = conn.execute("SELECT COUNT(*) as count FROM signals WHERE signal_type = 'UP'").fetchone()["count"]
        bearish = conn.execute("SELECT COUNT(*) as count FROM signals WHERE signal_type = 'DOWN'").fetchone()["count"]
        users = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()["count"]
        return {"total_signals": total, "bullish_signals": bullish, "bearish_signals": bearish, "user_count": users}
    except Exception:
        logger.exception("Unable to compute statistics")
        return {"total_signals": 0, "bullish_signals": 0, "bearish_signals": 0, "user_count": 0}
    finally:
        conn.close()
