# Implementation Plan

## Goal

Build a private, research-oriented AI bot that can learn from Trading 212 portfolio history without creating a direct path to unreviewed live trading.

## First milestone: read-only data foundation

The first usable release will collect and report on demo-account data. It will not train a predictive model, provide investment recommendations, simulate execution, or call Trading 212 mutation endpoints.

### Data flow

```text
Trading 212 demo account
          |
          v
Trading 212 MCP server (local stdio)
          |
          v
Read-only MCP adapter and tool allowlist
          |
          v
Raw payload archive + normalized SQLite tables
          |
          v
Offline portfolio-history analytics and reports
```

## Components

### MCP adapter

- Start or connect to the separately checked-out Trading 212 MCP server.
- Use stdio transport.
- Allow account, position, order-history, transaction, dividend, and metadata reads.
- Reject order placement, order cancellation, pie mutations, and CSV export requests.
- Handle `nextPagePath` cursors explicitly.
- Record retrieval timestamps and cache metadata.

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
