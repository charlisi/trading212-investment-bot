"""Automated drift evaluation, benchmark alpha tracking, and rebalancing logic."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

# Baseline numbers recorded at challenge inception (2026-09-15)
BASELINE_DATE = "2026-09-15"
BASELINE_PORTFOLIO_GBP = 5000.0
BASELINE_SPY_USD = 756.69
BASELINE_QQQ_USD = 703.81

# Hard Risk Constraints
MAX_SINGLE_WEIGHT = 0.25  # 25% single-asset cap
MIN_CASH_WEIGHT = 0.05    # 5% cash floor
MAX_CASH_WEIGHT = 0.15    # 15% cash drag ceiling
MAX_DAILY_TURNOVER_GBP = 500.0


@dataclass
class RebalanceTrigger:
    ticker: str
    trigger_type: str  # "TRIM", "CASH_FLOOR", "CASH_DRAG", "STOP_LOSS"
    message: str
    current_value: float
    target_value: float


@dataclass
class EvaluationReport:
    timestamp: str
    portfolio_value_gbp: float
    cash_available_gbp: float
    cash_weight_pct: float
    portfolio_return_pct: float
    spy_return_pct: float
    qqq_return_pct: float
    alpha_vs_spy_pct: float
    alpha_vs_qqq_pct: float
    max_benchmark_alpha_pct: float
    hhi: float
    positions: list[dict[str, Any]]
    triggers: list[RebalanceTrigger] = field(default_factory=list)
    proposed_orders: list[dict[str, Any]] = field(default_factory=list)


def evaluate_portfolio_state(
    account_summary: dict[str, Any],
    positions: list[dict[str, Any]],
    current_spy_price: float,
    current_qqq_price: float,
    fx_gbp_usd: float = 1.3477,
) -> EvaluationReport:
    """Evaluate current portfolio against the 12-month alpha challenge rules."""
    ts = datetime.now(timezone.utc).isoformat()
    total_val = float(account_summary.get("totalValue", BASELINE_PORTFOLIO_GBP))
    cash_val = float(account_summary.get("cash", {}).get("availableToTrade", 0.0))
    cash_weight = cash_val / total_val if total_val > 0 else 0.0

    # Returns calculation
    port_ret = ((total_val - BASELINE_PORTFOLIO_GBP) / BASELINE_PORTFOLIO_GBP) * 100.0
    spy_ret = ((current_spy_price - BASELINE_SPY_USD) / BASELINE_SPY_USD) * 100.0
    qqq_ret = ((current_qqq_price - BASELINE_QQQ_USD) / BASELINE_QQQ_USD) * 100.0

    alpha_spy = port_ret - spy_ret
    alpha_qqq = port_ret - qqq_ret
    alpha_max = port_ret - max(spy_ret, qqq_ret)

    # Weights and HHI
    triggers: list[RebalanceTrigger] = []
    proposed_orders: list[dict[str, Any]] = []
    hhi_sum = cash_weight**2

    normalized_positions = []
    for pos in positions:
        ticker = pos.get("instrument", {}).get("ticker") or pos.get("ticker", "UNKNOWN")
        qty = float(pos.get("quantity", 0.0))
        cur_p = float(pos.get("currentPrice", 0.0))
        wallet = pos.get("walletImpact", {})
        val_gbp = float(wallet.get("currentValue", pos.get("currentValue", 0.0)))

        weight = val_gbp / total_val if total_val > 0 else 0.0
        hhi_sum += weight**2

        pos_info = {
            "ticker": ticker,
            "quantity": qty,
            "current_price": cur_p,
            "value_gbp": val_gbp,
            "weight_pct": round(weight * 100, 2),
        }
        normalized_positions.append(pos_info)

        # Check single-asset ceiling
        if weight > MAX_SINGLE_WEIGHT:
            target_val = total_val * 0.18  # Trim back to 18%
            excess_gbp = val_gbp - target_val
            excess_usd = excess_gbp * fx_gbp_usd
            shares_to_sell = excess_usd / cur_p if cur_p > 0 else 0.0

            triggers.append(
                RebalanceTrigger(
                    ticker=ticker,
                    trigger_type="TRIM",
                    message=f"{ticker} weight is {weight*100:.1f}% (exceeds {MAX_SINGLE_WEIGHT*100:.0f}% ceiling)",
                    current_value=val_gbp,
                    target_value=target_val,
                )
            )
            proposed_orders.append(
                {
                    "action": "SELL",
                    "ticker": ticker,
                    "quantity": round(shares_to_sell, 4),
                    "estimated_value_gbp": round(excess_gbp, 2),
                    "reason": f"Trim excess weight down to 18%",
                }
            )

    # Check cash floor & drag
    if cash_weight < MIN_CASH_WEIGHT:
        triggers.append(
            RebalanceTrigger(
                ticker="CASH",
                trigger_type="CASH_FLOOR",
                message=f"Cash buffer is {cash_weight*100:.1f}% (below {MIN_CASH_WEIGHT*100:.0f}% floor)",
                current_value=cash_val,
                target_value=total_val * MIN_CASH_WEIGHT,
            )
        )
    elif cash_weight > MAX_CASH_WEIGHT:
        triggers.append(
            RebalanceTrigger(
                ticker="CASH",
                trigger_type="CASH_DRAG",
                message=f"Cash buffer is {cash_weight*100:.1f}% (above {MAX_CASH_WEIGHT*100:.0f}% ceiling - cash drag)",
                current_value=cash_val,
                target_value=total_val * 0.08,
            )
        )

    return EvaluationReport(
        timestamp=ts,
        portfolio_value_gbp=round(total_val, 2),
        cash_available_gbp=round(cash_val, 2),
        cash_weight_pct=round(cash_weight * 100, 2),
        portfolio_return_pct=round(port_ret, 2),
        spy_return_pct=round(spy_ret, 2),
        qqq_return_pct=round(qqq_ret, 2),
        alpha_vs_spy_pct=round(alpha_spy, 2),
        alpha_vs_qqq_pct=round(alpha_qqq, 2),
        max_benchmark_alpha_pct=round(alpha_max, 2),
        hhi=round(hhi_sum, 4),
        positions=normalized_positions,
        triggers=triggers,
        proposed_orders=proposed_orders,
    )
