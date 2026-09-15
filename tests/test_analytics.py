from __future__ import annotations

import pytest
from trading_bot.analytics import (
    calculate_annualized_volatility,
    calculate_hhi,
    calculate_max_drawdown,
    calculate_sma,
    calculate_weights,
)


def test_calculate_weights() -> None:
    positions = [
        {"ticker": "AAPL", "current_value": 3000.0},
        {"ticker": "GOOGL", "current_value": 2000.0},
    ]
    weights = calculate_weights(positions, total_value=10000.0)
    assert weights["AAPL"] == 0.3
    assert weights["GOOGL"] == 0.2


def test_calculate_hhi() -> None:
    # 2 equal assets: 0.5^2 + 0.5^2 = 0.5
    assert calculate_hhi([0.5, 0.5]) == 0.5
    # 4 equal assets: 4 * 0.25^2 = 0.25
    assert calculate_hhi([0.25, 0.25, 0.25, 0.25]) == 0.25
    # Empty
    assert calculate_hhi([]) == 0.0


def test_calculate_sma() -> None:
    prices = [10.0, 20.0, 30.0, 40.0, 50.0]
    sma3 = calculate_sma(prices, window=3)
    assert sma3[:2] == [None, None]
    assert sma3[2] == 20.0  # (10+20+30)/3
    assert sma3[3] == 30.0  # (20+30+40)/3
    assert sma3[4] == 40.0  # (30+40+50)/3


def test_calculate_max_drawdown() -> None:
    prices = [100.0, 120.0, 90.0, 110.0, 80.0, 95.0]
    # Peak is 120.0, trough is 80.0 -> (80 - 120) / 120 = -40 / 120 = -0.3333
    dd = calculate_max_drawdown(prices)
    assert dd == pytest.approx(-0.3333, abs=1e-4)


def test_calculate_annualized_volatility() -> None:
    returns = [0.01, -0.01, 0.02, -0.005, 0.015]
    vol = calculate_annualized_volatility(returns)
    assert vol > 0.0
