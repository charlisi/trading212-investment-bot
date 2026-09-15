from __future__ import annotations

from trading_bot.rebalancer import (
    BASELINE_PORTFOLIO_GBP,
    BASELINE_QQQ_USD,
    BASELINE_SPY_USD,
    evaluate_portfolio_state,
)


def test_evaluate_portfolio_state_baseline() -> None:
    account = {
        "totalValue": 5000.0,
        "cash": {"availableToTrade": 500.0},
    }
    positions = [
        {
            "ticker": "NVDA_US_EQ",
            "quantity": 5.0,
            "currentPrice": 200.0,
            "currentValue": 900.0,
        },
        {
            "ticker": "MSFT_US_EQ",
            "quantity": 2.0,
            "currentPrice": 450.0,
            "currentValue": 900.0,
        },
    ]

    report = evaluate_portfolio_state(
        account_summary=account,
        positions=positions,
        current_spy_price=BASELINE_SPY_USD,
        current_qqq_price=BASELINE_QQQ_USD,
    )

    assert report.portfolio_value_gbp == 5000.0
    assert report.portfolio_return_pct == 0.0
    assert report.spy_return_pct == 0.0
    assert report.qqq_return_pct == 0.0
    assert report.alpha_vs_spy_pct == 0.0
    assert len(report.triggers) == 0


def test_evaluate_portfolio_triggers_trim_when_single_asset_exceeds_ceiling() -> None:
    account = {
        "totalValue": 5000.0,
        "cash": {"availableToTrade": 400.0},
    }
    # NVDA is £1,500 = 30% of portfolio (> 25% ceiling)
    positions = [
        {
            "ticker": "NVDA_US_EQ",
            "quantity": 10.0,
            "currentPrice": 200.0,
            "currentValue": 1500.0,
        }
    ]

    report = evaluate_portfolio_state(
        account_summary=account,
        positions=positions,
        current_spy_price=BASELINE_SPY_USD,
        current_qqq_price=BASELINE_QQQ_USD,
    )

    trim_triggers = [t for t in report.triggers if t.trigger_type == "TRIM"]
    assert len(trim_triggers) == 1
    assert "NVDA_US_EQ" in trim_triggers[0].message
    assert len(report.proposed_orders) == 1
    assert report.proposed_orders[0]["action"] == "SELL"


def test_evaluate_portfolio_triggers_cash_floor() -> None:
    # Only £100 cash = 2% (< 5% floor)
    account = {
        "totalValue": 5000.0,
        "cash": {"availableToTrade": 100.0},
    }
    positions = []

    report = evaluate_portfolio_state(
        account_summary=account,
        positions=positions,
        current_spy_price=BASELINE_SPY_USD,
        current_qqq_price=BASELINE_QQQ_USD,
    )

    floor_triggers = [t for t in report.triggers if t.trigger_type == "CASH_FLOOR"]
    assert len(floor_triggers) == 1
