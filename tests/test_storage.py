from __future__ import annotations

import sqlite3
from trading_bot.storage import init_db, save_snapshot, save_price_series, get_latest_snapshot


def test_init_db_creates_tables() -> None:
    conn = sqlite3.connect(":memory:")
    init_db(conn)
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    assert "snapshots" in tables
    assert "positions" in tables
    assert "historical_prices" in tables


def test_save_and_retrieve_snapshot() -> None:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)

    account = {
        "totalValue": 5500.0,
        "currency": "GBP",
        "cash": {"availableToTrade": 1500.0},
        "investments": {"currentValue": 4000.0, "unrealizedProfitLoss": 250.0},
    }
    positions = [
        {
            "ticker": "AAPL",
            "quantity": 10.0,
            "averagePrice": 180.0,
            "currentPrice": 200.0,
            "currentValue": 2000.0,
            "unrealizedProfitLoss": 200.0,
        },
        {
            "ticker": "MSFT",
            "quantity": 5.0,
            "averagePrice": 390.0,
            "currentPrice": 400.0,
            "currentValue": 2000.0,
            "unrealizedProfitLoss": 50.0,
        },
    ]

    snapshot_id = save_snapshot(conn, account, positions, timestamp="2026-09-15T12:00:00Z")
    assert snapshot_id == 1

    latest = get_latest_snapshot(conn)
    assert latest is not None
    assert latest["total_value"] == 5500.0
    assert latest["cash_available"] == 1500.0
    assert latest["currency"] == "GBP"
    assert len(latest["positions"]) == 2
    assert latest["positions"][0]["ticker"] == "AAPL"


def test_save_price_series() -> None:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    init_db(conn)

    candles = [
        {
            "Date": "2026-09-10",
            "Open": 220.0,
            "High": 225.0,
            "Low": 219.0,
            "Close": 224.5,
            "Volume": 1000000,
        },
        {
            "Date": "2026-09-11",
            "Open": 224.5,
            "High": 228.0,
            "Low": 223.0,
            "Close": 227.0,
            "Volume": 1200000,
        },
    ]
    inserted = save_price_series(conn, "AAPL", candles)
    assert inserted == 2

    row = conn.execute("SELECT * FROM historical_prices WHERE ticker = 'AAPL'").fetchone()
    assert row["close"] == 224.5
