"""SQLite persistence for portfolio snapshots, positions, and market data."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def get_db_path(data_dir: Path | None = None) -> Path:
    base = data_dir if data_dir is not None else Path("./data")
    base.mkdir(parents=True, exist_ok=True)
    return base / "portfolio.db"


def init_db(db_target: Path | str | sqlite3.Connection) -> sqlite3.Connection:
    if isinstance(db_target, sqlite3.Connection):
        conn = db_target
    else:
        conn = sqlite3.connect(db_target)
    conn.row_factory = sqlite3.Row
    with conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_value REAL NOT NULL,
                cash_available REAL NOT NULL,
                investments_value REAL NOT NULL,
                unrealized_pl REAL NOT NULL,
                currency TEXT NOT NULL,
                raw_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id INTEGER NOT NULL,
                ticker TEXT NOT NULL,
                quantity REAL NOT NULL,
                average_price REAL NOT NULL,
                current_price REAL NOT NULL,
                current_value REAL NOT NULL,
                unrealized_pl REAL NOT NULL,
                raw_json TEXT NOT NULL,
                FOREIGN KEY (snapshot_id) REFERENCES snapshots(id)
            );

            CREATE TABLE IF NOT EXISTS historical_prices (
                ticker TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume INTEGER NOT NULL,
                PRIMARY KEY (ticker, date)
            );
            """
        )
    return conn


def save_snapshot(
    conn: sqlite3.Connection,
    account_summary: dict[str, Any],
    positions: list[dict[str, Any]],
    timestamp: str | None = None,
) -> int:
    ts = timestamp or datetime.now(timezone.utc).isoformat()
    total_val = float(account_summary.get("totalValue", 0.0))
    cash_val = float(account_summary.get("cash", {}).get("availableToTrade", 0.0))
    inv = account_summary.get("investments", {})
    inv_val = float(inv.get("currentValue", 0.0))
    unrealized = float(inv.get("unrealizedProfitLoss", 0.0))
    currency = str(account_summary.get("currency", "GBP"))

    with conn:
        cursor = conn.execute(
            """
            INSERT INTO snapshots (timestamp, total_value, cash_available, investments_value, unrealized_pl, currency, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (ts, total_val, cash_val, inv_val, unrealized, currency, json.dumps(account_summary)),
        )
        snapshot_id = cursor.lastrowid
        assert snapshot_id is not None

        for pos in positions:
            ticker = pos.get("ticker", "UNKNOWN")
            qty = float(pos.get("quantity", 0.0))
            avg_p = float(pos.get("averagePrice", 0.0))
            cur_p = float(pos.get("currentPrice", 0.0))
            cur_v = float(pos.get("currentValue", qty * cur_p))
            pos_unrealized = float(pos.get("unrealizedProfitLoss", (cur_p - avg_p) * qty))

            conn.execute(
                """
                INSERT INTO positions (snapshot_id, ticker, quantity, average_price, current_price, current_value, unrealized_pl, raw_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (snapshot_id, ticker, qty, avg_p, cur_p, cur_v, pos_unrealized, json.dumps(pos)),
            )

    return snapshot_id


def save_price_series(conn: sqlite3.Connection, ticker: str, candles: list[dict[str, Any]]) -> int:
    inserted = 0
    with conn:
        for c in candles:
            date = c.get("Date")
            if not date:
                continue
            conn.execute(
                """
                INSERT OR REPLACE INTO historical_prices (ticker, date, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    ticker,
                    str(date),
                    float(c.get("Open", 0.0)),
                    float(c.get("High", 0.0)),
                    float(c.get("Low", 0.0)),
                    float(c.get("Close", 0.0)),
                    int(c.get("Volume", 0)),
                ),
            )
            inserted += 1
    return inserted


def get_latest_snapshot(conn: sqlite3.Connection) -> dict[str, Any] | None:
    row = conn.execute("SELECT * FROM snapshots ORDER BY id DESC LIMIT 1").fetchone()
    if not row:
        return None

    snapshot_id = row["id"]
    positions_rows = conn.execute(
        "SELECT * FROM positions WHERE snapshot_id = ?", (snapshot_id,)
    ).fetchall()

    return {
        "id": row["id"],
        "timestamp": row["timestamp"],
        "total_value": row["total_value"],
        "cash_available": row["cash_available"],
        "investments_value": row["investments_value"],
        "unrealized_pl": row["unrealized_pl"],
        "currency": row["currency"],
        "positions": [dict(p) for p in positions_rows],
    }
