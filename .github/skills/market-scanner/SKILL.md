---
name: market-scanner
description: Analyze market trends, historical price action, volatility, and benchmark comparison for stocks using Yahoo Finance MCP.
---

# Market Scanner Skill

Use this skill to research a stock, assess market conditions, inspect price history, or compare a ticker against a benchmark.

## Procedure

1. **Retrieve Price Series**:
   - Call `get_history` from `yfinance` MCP with:
     - `ticker`: symbol (e.g. `AAPL`, `MSFT`, `SPY`)
     - `period`: `1y` (or `6mo` for shorter-term trend)
     - `interval`: `1d`
   
2. **Calculate Technical & Trend Metrics**:
   - **Current Price & 52-Week Range**: Highest high and lowest low over the period.
   - **Moving Averages**:
     - 50-day Simple Moving Average (SMA)
     - 200-day Simple Moving Average (SMA)
     - Trend status: Bullish (Price > 50 > 200), Bearish (Price < 50 < 200), or Neutral/Consolidating.
   - **Historical Volatility**: Standard deviation of daily returns annualized ($\sigma \times \sqrt{252}$).
   - **Recent Drawdown**: Drop from the highest peak in the lookback window.

3. **Fundamentals & Target Context**:
   - Optionally call `get_price_targets` and `get_analyst_recommendations` to see consensus target price and upside/downside ratio.

4. **Synthesize Insight**:
   - Summarize the trend, current valuation context, key support/resistance levels, and risk/reward ratio.
