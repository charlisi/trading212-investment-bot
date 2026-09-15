# Implementation Plan

## Goal

Build a private, research-oriented AI bot that can learn from Trading 212 portfolio history without creating a direct path to unreviewed live trading.

## First milestone: read-only data foundation

The first usable release will collect and report on demo-account data. It will not train a predictive model, provide investment recommendations, simulate execution, or call Trading 212 mutation endpoints.

## Hybrid Architecture

The bot is implemented as a **hybrid AI agent system**:

1. **Agent Layer (Instructions & Skills)**:
   - Persona and guardrails defined in [`.github/copilot-instructions.md`](../.github/copilot-instructions.md).
   - Domain skills in [`.github/skills/`](../.github/skills/):
     - `portfolio-audit`: Audits balances, positions, cash reserves, and saves snapshots to local SQLite.
     - `market-scanner`: Analyzes historical price series, moving averages, and volatility via Yahoo Finance MCP.
     - `trade-proposer`: Formulates proposed risk-managed rebalancing or trade actions with strict human confirmation required before any order execution.

2. **Tooling Layer (MCP Servers)**:
   - Configured in [`.vscode/mcp.json`](../.vscode/mcp.json).
   - `trading212-demo`: Local stdio connection to Trading 212 Practice account.
   - `yfinance`: Local stdio connection to Yahoo Finance via `uvx` (no API key required).

3. **Core Engine (Python)**:
   - `storage.py`: SQLite schema (`./data/portfolio.db`) for snapshots, holdings, and price series.
   - `analytics.py`: Pure math functions for weights, concentration (HHI), moving averages, drawdowns, and volatility.
   - `cli.py`: Command-line interface for offline summaries and verification.

### Data flow

```text
Trading 212 Demo Account              Yahoo Finance Market Feed
         |                                     |
         v                                     v
Trading 212 MCP Server (stdio)        mcp-server-yfinance (stdio, no key)
         |                                     |
         +------------------+------------------+
                            |
                            v
            Dual MCP Adapter & Tool Allowlist
                            |
                            v
       Raw Payload Archive + Normalized SQLite Tables
                            |
                            v
   Offline Portfolio Analytics, Market Context & Feature Store
```

## Components

### MCP Adapters

1. **Trading 212 Adapter** (`trading212-mcp-server` over stdio):
   - Allow account, position, order history, transactions, dividends, and instrument metadata.
   - Reject order placement, order cancellation, pie mutations, and CSV export requests.
   - Handle pagination (`nextPagePath`) and record retrieval metadata.

2. **Market Data Adapter** (`mcp-server-yfinance` over stdio via `uvx`):
   - Requires **no API key**.
   - Pull historical OHLCV price series (`get_history`), key financials, and market benchmarks for stocks held or watched in Trading 212.
   - Provide historical bars for feature calculation, volatility analysis, and price normalization.

### Storage

Use a private local SQLite database with:

- Immutable raw JSON responses.
- Collection-run records and endpoint status.
- Account snapshots.
- Positions, orders, transactions, dividends, and instruments.
- Stable external IDs for idempotent upserts.
- Source timestamps, retrieval timestamps, currency, and units.

### Analytics

The initial report should cover only metrics supported by the collected data:

- Account currency and cash.
- Current positions and concentration.
- Transaction and dividend totals.
- Portfolio and account snapshots over time.
- Turnover and realized/unrealized information where the source data supports it.

Unavailable metrics must be labeled as unavailable rather than inferred silently. GBX/GBP units and account currency must remain explicit.

## Safety boundaries

- Default and integration-test environment: `demo`.
- Refuse `live` configuration in the first milestone.
- No credentials in source control.
- Keep the MCP cache and SQLite database on a private local filesystem.
- Do not rely on MCP effect annotations as an authorization mechanism.
- Do not automatically retry mutations; mutations are disabled entirely here.
- Require explicit future approval before adding paper-trading or live-execution code.

## Testing strategy

Offline tests will use fixtures and cover:

- Tool allowlisting and mutation rejection.
- Multi-page history collection.
- Duplicate-record handling and idempotent reruns.
- Currency and unit normalization.
- Partial responses, stale data, and failed collection runs.
- Demo-only configuration guards.

A separate, explicitly gated smoke test may contact a user-provided demo account. Normal tests must not require credentials or network access.

## Later research direction

Account history alone cannot support robust market forecasting. A later research phase may add an external market-data adapter, time-based train/validation/test splits, benchmark strategies, transaction-cost assumptions, and a paper-trading simulator. Any model must be evaluated against simple baselines and checked for leakage, selection bias, survivorship bias, and overfitting.
