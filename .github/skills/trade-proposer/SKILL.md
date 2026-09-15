---
name: trade-proposer
description: Synthesize portfolio state and market data to propose risk-managed trades or rebalancing actions with strict human-in-the-loop signoff.
---

# Trade Proposer Skill

Use this skill when proposing new positions, adjusting allocations, taking profits, or rebalancing existing holdings.

## Critical Guardrails

- **Zero Autonomous Execution**: NEVER call `place_market_order` or `place_limit_order` autonomously.
- **Explicit Human Approval Required**: Formulate the trade proposal as a draft. The user must review and confirm before any order is submitted.

## Procedure

1. **Assess Context**:
   - Current free cash from `fetch_account_cash`.
   - Current position size in the target ticker (if already owned) from `fetch_positions`.
   - Volatility and recent price action from `get_history` (via `yfinance`).

2. **Position Sizing & Risk Management**:
   - **Max Position Size Rule**: Single position should not exceed 10%–15% of total portfolio value.
   - **Risk Budget**: Total capital at risk per idea should not exceed 1%–2% of total account value.
   - **Stop-Loss / Invalidation Level**: Clearly define the exit price if the trade goes against the thesis.
   - **Order Type**: Prefer limit orders with explicit limit price when possible to avoid slippage.

3. **Draft the Trade Proposal**:
   Present the proposal with this structured template:

   ```markdown
   ### Proposed Action: [BUY / SELL / REBALANCE]
   - **Instrument**: {Ticker} ({Company Name})
   - **Action**: {BUY | SELL}
   - **Quantity**: {N shares}
   - **Order Type**: {MARKET | LIMIT @ price}
   - **Estimated Total Value**: {Amount} {Currency} ({X}% of Portfolio)
   - **Cash Remaining After Order**: {Amount} {Currency}
   - **Thesis**: {1-2 concise sentences explaining why}
   - **Stop-Loss / Exit Strategy**: Invalidation below {Price} (-{X}%)
   - **Upside Target**: Target {Price} (+{Y}%)

   > **Confirmation Required**: Would you like me to submit this order to Trading 212 Demo? (Reply "Confirm" to execute or "Cancel" to abort).
   ```

4. **Execution on Confirmation Only**:
   - Only if the user explicitly confirms, invoke the appropriate order tool (`place_market_order` or `place_limit_order`).
   - Immediately report the returned order confirmation / order ID.
