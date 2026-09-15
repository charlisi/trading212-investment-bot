"""Command-line entry point."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

from .analytics import calculate_hhi, calculate_weights
from .config import Settings
from .storage import get_db_path, get_latest_snapshot, init_db, save_price_series


def fetch_yahoo_history(ticker: str, period: str = "1mo", interval: str = "1d") -> list[dict]:
    """Fetch historical OHLCV candles via yfinance MCP server over stdio."""
    proc = subprocess.Popen(
        ["uvx", "mcp-server-yfinance"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    def send_recv(req: dict) -> dict:
        proc.stdin.write(json.dumps(req) + "\n")
        proc.stdin.flush()
        line = proc.stdout.readline()
        if not line:
            err = proc.stderr.read()
            raise RuntimeError(f"yfinance MCP server failed: {err}")
        return json.loads(line)

    try:
        # Initialize
        send_recv(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "trading-bot", "version": "0.1.0"},
                },
            }
        )
        proc.stdin.write(
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
            + "\n"
        )
        proc.stdin.flush()

        # Call get_history
        res = send_recv(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "get_history",
                    "arguments": {"ticker": ticker, "period": period, "interval": interval},
                },
            }
        )
        content = res.get("result", {}).get("content", [])
        candles = [json.loads(c["text"]) for c in content if c.get("type") == "text"]
        return candles
    finally:
        proc.terminate()


def main() -> None:
    parser = argparse.ArgumentParser(description="Trading 212 portfolio research bot")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("check-config", help="Verify configuration and data directory.")
    subparsers.add_parser("summary", help="Display latest portfolio snapshot and holdings.")

    fetch_parser = subparsers.add_parser("fetch-history", help="Fetch and save historical stock data.")
    fetch_parser.add_argument("ticker", help="Stock ticker symbol (e.g. AAPL, NVDA, SPY)")
    fetch_parser.add_argument("--period", default="1mo", help="Lookback period (e.g. 5d, 1mo, 6mo, 1y, 5y)")
    fetch_parser.add_argument("--interval", default="1d", help="Candle interval (e.g. 1d, 1wk, 1h)")

    args = parser.parse_args()
    settings = Settings.from_env()

    if args.command == "check-config":
        print(f"Read-only configuration valid for environment={settings.environment}")
        print(f"Data directory: {settings.data_dir}")

    elif args.command == "fetch-history":
        print(f"Fetching {args.ticker} history (period={args.period}, interval={args.interval}) from Yahoo Finance...")
        candles = fetch_yahoo_history(args.ticker, period=args.period, interval=args.interval)
        print(f"Retrieved {len(candles)} candles.")
        if candles:
            latest = candles[-1]
            print(f"Latest Bar ({latest.get('Date')}): Open={latest.get('Open'):.2f}, Close={latest.get('Close'):.2f}, Vol={latest.get('Volume'):,}")
            db_path = get_db_path(settings.data_dir)
            conn = init_db(db_path)
            inserted = save_price_series(conn, args.ticker, candles)
            print(f"Saved {inserted} bars into {db_path} table 'historical_prices'.")

    elif args.command == "summary":
        db_path = get_db_path(settings.data_dir)
        if not db_path.exists():
            print("No database found yet. Run an audit or save a snapshot first.")
            sys.exit(0)

        conn = init_db(db_path)
        snapshot = get_latest_snapshot(conn)
        if not snapshot:
            print("Database initialized, but no snapshots recorded yet.")
            sys.exit(0)

        print("=== Latest Portfolio Snapshot ===")
        print(f"Timestamp: {snapshot['timestamp']}")
        print(f"Total Value: {snapshot['total_value']:,.2f} {snapshot['currency']}")
        print(f"Cash Available: {snapshot['cash_available']:,.2f} {snapshot['currency']}")
        print(f"Investments: {snapshot['investments_value']:,.2f} {snapshot['currency']}")
        print(f"Unrealized P&L: {snapshot['unrealized_pl']:,.2f} {snapshot['currency']}")

        positions = snapshot.get("positions", [])
        print(f"\nOpen Positions ({len(positions)}):")
        if not positions:
            print("  (None)")
        else:
            weights = calculate_weights(positions, snapshot["total_value"])
            hhi = calculate_hhi(list(weights.values()))
            print(f"Portfolio Concentration (HHI): {hhi:.4f}")
            for pos in positions:
                ticker = pos["ticker"]
                w = weights.get(ticker, 0.0) * 100
                print(
                    f"  - {ticker}: {pos['quantity']} shares @ {pos['current_price']} {snapshot['currency']} (Value: {pos['current_value']:,.2f}, Weight: {w:.1f}%)"
                )


if __name__ == "__main__":
    main()
