# Trading 212 AI Bot

A research-oriented investment bot built around the Trading 212 MCP server.

## Current scope

The first milestone is deliberately read-only:

- Connect to a local Trading 212 MCP server over stdio.
- Use a demo Trading 212 account only.
- Collect account, cash, positions, orders, transactions, dividends, and instrument metadata.
- Store raw responses and normalized history locally.
- Produce portfolio-history reports from the local database.

This milestone does not place orders, cancel orders, mutate pies, request exports, recommend investments, or run autonomous live trading.

## Architecture direction

The application will be implemented in Python with `uv`. The MCP server remains a separate local checkout and is configured through an absolute path. The bot will enforce its own read-only tool allowlist because MCP tool annotations describe effects but do not provide authorization.

Trading 212 account history is not an independent market-data feed. Forecasting or strategy backtesting will require additional historical price, corporate-action, and benchmark data and is outside the first milestone.

## Planned milestones

1. Document the architecture and safety boundary.
2. Build the Python project and configuration layer.
3. Add a read-only MCP stdio adapter with pagination support.
4. Persist raw and normalized data in private SQLite storage.
5. Add idempotent collection and data-quality checks.
6. Generate offline portfolio-history reports.
7. Add fixture-based tests and a demo-account integration smoke test.
8. Design later research, simulation, and paper-trading workflows.

## Repository setup

The MCP server is independently maintained and is not affiliated with Trading 212. Review its current documentation and pin a known commit before relying on it.

The local MCP server expects variables such as:

- `TRADING212_API_KEY`
- Optional `TRADING212_API_SECRET`
- `ENVIRONMENT=demo`

Never commit credentials, MCP caches, raw account data, SQLite databases, or generated reports.

## Status

Documentation-first implementation in progress. Live trading is intentionally disabled.
