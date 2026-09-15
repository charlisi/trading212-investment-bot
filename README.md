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

The application is implemented in Python with `uv`. It uses two MCP servers over local `stdio`:

1. **Trading 212 MCP Server** (`trading212-mcp-server`): Connects to your Trading 212 demo account for account state, positions, transactions, orders, and dividends. The bot strictly enforces an internal read-only allowlist to block all order and mutation tools.
2. **Yahoo Finance MCP Server** (`mcp-server-yfinance` via `uvx`): Provides market price feeds, historical OHLCV candles, benchmarks, and indicators for stocks without requiring any API key.

By combining account state from Trading 212 with public market data from Yahoo Finance, the bot can construct feature sets, benchmark portfolio performance, and train investment models safely offline.

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
