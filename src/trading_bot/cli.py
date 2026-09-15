"""Command-line entry point."""

from __future__ import annotations

import argparse

from .config import Settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Trading 212 portfolio research bot")
    parser.add_argument(
        "command",
        choices=("check-config",),
        help="Run a local safety/configuration check.",
    )
    args = parser.parse_args()
    if args.command == "check-config":
        settings = Settings.from_env()
        print(f"Read-only configuration valid for environment={settings.environment}")


if __name__ == "__main__":
    main()
