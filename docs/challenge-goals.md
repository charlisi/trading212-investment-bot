# 12-Month Alpha Challenge: Portfolio Goals & Rules

## 1. Challenge Overview

- **Objective**: Outperform major market benchmarks by **+20.0% alpha** over a 12-month period.
- **Start Date**: September 15, 2026
- **Target Completion Date**: September 15, 2027
- **Starting Capital**: **£5,000.00 GBP** (~$6,738.50 USD at 1.3477 FX)
- **Account**: Trading 212 Practice (Demo) Account ID `51058370`
- **Initial Baseline Snapshots**:
  - Snapshot #1 (100% Cash): £5,000.00
  - Snapshot #2 (Funded Allocation): £4,991.62 invested across 6 growth pillars + £389.28 cash buffer.

---

## 2. Benchmark Tracking Baselines

To measure the **+20% alpha** requirement, performance is tracked against two primary benchmarks from the opening close on 2026-09-15:

| Benchmark | Ticker | Baseline Close | Target 12M Return Formula |
| :--- | :---: | :---: | :--- |
| **S&P 500 ETF** | `SPY` | **$756.69** | $R_{Target} \ge R_{SPY} + 20.0\%$ |
| **Nasdaq 100 ETF** | `QQQ` | **$703.81** | $R_{Target} \ge R_{QQQ} + 20.0\%$ |

$$\text{Alpha} = R_{\text{Portfolio}} - \max(R_{\text{SPY}}, R_{\text{QQQ}})$$
**Success Condition**: $\text{Alpha} \ge +20.0\%$ at the 12-month mark.

---

## 3. Approved Asset Universe & Target Allocations

The portfolio concentrates in 6 secular growth pillars with high Return on Invested Capital (ROIC) and structural tailwinds:

| Pillar | Symbol | Trading 212 Ticker | Initial Target % | Initial Shares | Rationale |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **AI Compute & GPUs** | `NVDA` | `NVDA_US_EQ` | 18.0% | 5.7208 | Dominant accelerated compute & CUDA ecosystem. |
| **Cloud & Enterprise AI** | `MSFT` | `MSFT_US_EQ` | 18.0% | 2.4430 | Azure hyperscaler scale and Copilot monetization. |
| **Foundry Monopoly** | `TSM` | `TSM_US_EQ` | 16.0% | 2.6022 | >90% global production of sub-5nm advanced silicon. |
| **Cloud Security & SASE** | `CRWD` | `CRWD_US_EQ` | 14.0% | 3.9163 | Falcon platform mission-critical enterprise security. |
| **Metabolic Healthcare** | `LLY` | `LLY_US_EQ` | 14.0% | 0.8334 | Multi-decade secular expansion in GLP-1 metabolic drugs. |
| **AI Baseload Energy** | `CEG` | `CEG_US_EQ` | 12.0% | 3.0887 | Clean nuclear power supplying hyperscale data centers. |
| **Tactical Cash Reserve** | `CASH` | — | 8.0% | — | Dip-buying and rebalancing liquidity buffer. |

---

## 4. Risk Limits & Allocation Constraints

To ensure true diversification and prevent catastrophic single-asset blowups:

1. **Maximum Position Ceiling (25%)**:
   - No single asset may exceed **25.0%** of total portfolio equity.
   - If an asset grows past 22%, it enters the trimming watchlist.
   - If it breaches 25%, the bot must automatically trim back to target weight and move proceeds to cash.
2. **Minimum Cash Floor (5%)**:
   - Free cash must never drop below **5.0%** (£250 equivalent).
   - Prevents total illiquidity, FX margin call risks, and allows buying pullbacks.
3. **Maximum Cash Drag Ceiling (15%)**:
   - Free cash exceeding **15.0%** triggers a redeployment cycle into underweight or highest-conviction pillars.
4. **Herfindahl-Hirschman Index (HHI)**:
   - Target portfolio HHI must remain below **0.180** (institutional threshold for a well-diversified portfolio). Initial baseline is **0.1446**.
5. **Trend Invalidation / Stop-Loss Rule**:
   - If an asset closes **> 8% below its 200-day Simple Moving Average (SMA)** or suffers a **> 20% drawdown from local peak**, a risk review is triggered to cut or replace the position with a higher-momentum candidate.

---

## 5. Review & Rebalance Cadence

- **Daily Market Close Review**: Automated tracking of prices, alpha spread vs SPY/QQQ, and risk boundaries.
- **Bi-weekly Rebalance Check**: Evaluate weight drift ($\pm 3\%$ from target).
- **Quarterly Earnings Evaluation**: Review EPS growth, forward revenue guidance, and thesis integrity.
