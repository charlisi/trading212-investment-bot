"""Command-line entry point."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

from .analytics import calculate_hhi, calculate_weights
from .config import Settings
from .rebalancer import evaluate_portfolio_state
from .storage import get_db_path, get_latest_snapshot, init_db, save_price_series, save_snapshot


def call_trading212_mcp(tool_name: str, arguments: dict | None = None) -> dict:
    """Call a tool on the local trading212-mcp-server over stdio."""
    import os
    from pathlib import Path
    env = os.environ.copy()
    
    server_bin = os.getenv("TRADING212_MCP_BIN")
    if not server_bin:
        # Default relative to project root or fallback to common local directory
        project_root = Path(__file__).resolve().parent.parent.parent
        candidate = project_root.parent / "trading212-mcp-server" / ".venv" / "bin" / "trading212-mcp-server"
        server_bin = str(candidate) if candidate.exists() else "trading212-mcp-server"

    proc = subprocess.Popen(
        [server_bin],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )

    def send_recv(req: dict) -> dict:
        proc.stdin.write(json.dumps(req) + "\n")
        proc.stdin.flush()
        line = proc.stdout.readline()
        if not line:
            err = proc.stderr.read()
            raise RuntimeError(f"Trading 212 MCP server failed: {err}")
        return json.loads(line)

    try:
        send_recv(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "trading-bot-cli", "version": "0.1.0"},
                },
            }
        )
        proc.stdin.write(
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})
            + "\n"
        )
        proc.stdin.flush()

        res = send_recv(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments or {}},
            }
        )
        return res.get("result", {}).get("structuredContent", {})
    finally:
        proc.terminate()


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

    cycle_parser = subparsers.add_parser(
        "run-cycle", help="Periodic monitoring cycle: audits portfolio, computes alpha vs SPY/QQQ, checks rebalance triggers."
    )
    cycle_parser.add_argument(
        "--execute",
        action="store_true",
        help="Automatically execute proposed rebalance orders (Trading 212 Demo only).",
    )

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

    elif args.command == "run-cycle":
        print("=== Running Periodic Monitoring & Evaluation Cycle ===")
        # 1. Fetch Trading 212 state
        summary = call_trading212_mcp("fetch_account_summary")
        positions_res = call_trading212_mcp("fetch_positions")
        raw_positions = positions_res.get("result", [])

        # 2. Fetch current Benchmark prices
        spy_candles = fetch_yahoo_history("SPY", period="5d", interval="1d")
        qqq_candles = fetch_yahoo_history("QQQ", period="5d", interval="1d")
        spy_price = float(spy_candles[-1]["Close"]) if spy_candles else 756.69
        qqq_price = float(qqq_candles[-1]["Close"]) if qqq_candles else 703.81

        # 3. Save snapshot to SQLite
        normalized_positions = []
        for p in raw_positions:
            ticker = p.get("instrument", {}).get("ticker", "UNKNOWN")
            qty = p.get("quantity", 0.0)
            avg_p = p.get("averagePricePaid", 0.0)
            cur_p = p.get("currentPrice", 0.0)
            wallet = p.get("walletImpact", {})
            cur_val = wallet.get("currentValue", 0.0)
            unrealized = wallet.get("unrealizedProfitLoss", 0.0)
            normalized_positions.append(
                {
                    "ticker": ticker,
                    "quantity": qty,
                    "averagePrice": avg_p,
                    "currentPrice": cur_p,
                    "currentValue": cur_val,
                    "unrealizedProfitLoss": unrealized,
                }
            )

        db_path = get_db_path(settings.data_dir)
        conn = init_db(db_path)
        snap_id = save_snapshot(conn, summary, normalized_positions)

        # 4. Run evaluation rules
        report = evaluate_portfolio_state(
            account_summary=summary,
            positions=raw_positions,
            current_spy_price=spy_price,
            current_qqq_price=qqq_price,
        )

        print(f"Timestamp: {report.timestamp}")
        print(f"Total Portfolio Value: £{report.portfolio_value_gbp:,.2f} ({report.portfolio_return_pct:+.2f}%)")
        print(f"Free Cash Reserve: £{report.cash_available_gbp:,.2f} ({report.cash_weight_pct:.1f}%)")
        print(f"S&P 500 (SPY): ${spy_price:.2f} ({report.spy_return_pct:+.2f}%)")
        print(f"Nasdaq 100 (QQQ): ${qqq_price:.2f} ({report.qqq_return_pct:+.2f}%)")
        print(f"Alpha vs SPY: {report.alpha_vs_spy_pct:+.2f}%")
        print(f"Alpha vs QQQ: {report.alpha_vs_qqq_pct:+.2f}%")
        print(f"Max Benchmark Alpha Spread: {report.max_benchmark_alpha_pct:+.2f}% (Goal: +20.0%)")
        print(f"Concentration (HHI): {report.hhi:.4f}")

        # 5. Output triggers
        if not report.triggers:
            print("\nStatus: All risk limits & allocations within bounds. No rebalance needed.")
        else:
            print(f"\n⚠️ Rebalance Triggers Fired ({len(report.triggers)}):")
            for t in report.triggers:
                print(f"  - [{t.trigger_type}] {t.message}")

            if report.proposed_orders:
                print("\nProposed Actions:")
                for o in report.proposed_orders:
                    print(f"  - {o['action']} {o['quantity']} {o['ticker']} (~£{o['estimated_value_gbp']}) [{o['reason']}]")

                if args.execute:
                    if settings.environment != "demo":
                        print("Autonomous execution is strictly restricted to ENVIRONMENT=demo. Aborting.")
                        sys.exit(1)
                    print("\nExecuting proposed orders on Trading 212 Demo...")
                    for o in report.proposed_orders:
                        res = call_trading212_mcp("place_market_order", {"ticker": o["ticker"], "quantity": -o["quantity"] if o["action"] == "SELL" else o["quantity"]})
                        print(f"Executed {o['action']} {o['ticker']}: {res.get('status')}")

        # Save evaluation report to JSON file
        report_file = settings.data_dir / "latest_evaluation.json"
        with open(report_file, "w") as f:
            json.dump(
                {
                    "timestamp": report.timestamp,
                    "portfolio_value_gbp": report.portfolio_value_gbp,
                    "cash_available_gbp": report.cash_available_gbp,
                    "portfolio_return_pct": report.portfolio_return_pct,
                    "alpha_spread_pct": report.max_benchmark_alpha_pct,
                    "hhi": report.hhi,
                    "triggers": [t.message for t in report.triggers],
                    "proposed_orders": report.proposed_orders,
                },
                f,
                indent=2,
            )
        print(f"\nSaved evaluation report to {report_file}")


if __name__ == "__main__":
    main()
