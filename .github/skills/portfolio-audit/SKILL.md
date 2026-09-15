---
name: portfolio-audit
description: Audit the Trading 212 portfolio health, asset weights, cash buffer, concentration risk, and save a snapshot to local storage.
---

# Portfolio Audit Skill

Use this skill whenever the user asks for a portfolio review, health check, balance check, or allocation breakdown.

## Procedure

1. **Query Account & Positions**:
   - Call `fetch_account_summary` from Trading 212 MCP.
   - Call `fetch_positions` from Trading 212 MCP.
   - Note `totalValue`, `cash.availableToTrade`, account `currency`, and `investments.currentValue`.

2. **Compute Allocations & Concentrations**:
   - Compute `cash_weight = cash.availableToTrade / totalValue`.
   - For each open position:
     - `position_weight = (position.quantity * position.currentPrice) / totalValue`.
     - Calculate unrealized profit/loss percentage: `(currentPrice - averagePrice) / averagePrice * 100`.
   - Highlight any position exceeding 20% total allocation (concentration risk).

3. **Check Cash Cushion**:
   - Healthy target: typically 5%–15% available cash depending on strategy.
   - Warn if cash is under 2% (low flexibility for dips or fees) or over 50% (cash drag).

4. **Persist Snapshot to SQLite**:
   - Execute the CLI snapshot command or Python storage function to record this timestamped state into `./data/portfolio.db`.

5. **Format Report**:
   Present findings in a structured Markdown format:
   - Account overview (Total Value, Free Cash, Invested Capital, Unrealized P&L).
   - Holdings breakdown table (Ticker, Quantity, Avg Price, Current Price, Value, Weight %, P&L %).
   - Risk assessment (Concentration, Cash reserves, Largest winner/loser).
