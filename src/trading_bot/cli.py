"""Command-line entry point."""

from __future__ import annotations

import argparse
import sys

from .analytics import calculate_hhi, calculate_weights
from .config import Settings
from .storage import get_db_path, get_latest_snapshot, init_db


def main() -> None:
    parser = argparse.ArgumentParser(description="Trading 212 portfolio research bot")
    parser.add_argument(
        "command",
        choices=("check-config", "summary"),
        help="Command to run.",
    )
    args = parser.parse_args()

    settings = Settings.from_env()

    if args.command == "check-config":
        print(f"Read-only configuration valid for environment={settings.environment}")
        print(f"Data directory: {settings.data_dir}")

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
