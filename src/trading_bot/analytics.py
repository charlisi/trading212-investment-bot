"""Quantitative analytics and risk metrics for portfolio and market feeds."""

from __future__ import annotations

import math
from typing import Sequence


def calculate_weights(
    positions: Sequence[dict[str, float]], total_value: float
) -> dict[str, float]:
    """Calculate percentage allocation weights for each position."""
    if total_value <= 0:
        return {}
    weights: dict[str, float] = {}
    for pos in positions:
        ticker = str(pos.get("ticker", "UNKNOWN"))
        val = float(pos.get("current_value", 0.0))
        weights[ticker] = round(val / total_value, 4)
    return weights


def calculate_hhi(weights: Sequence[float]) -> float:
    """
    Calculate Herfindahl-Hirschman Index (HHI) for portfolio concentration.
    Returns value between 0 (fully diversified) and 1.0 (single asset).
    """
    if not weights:
        return 0.0
    return round(sum(w**2 for w in weights), 4)


def calculate_sma(prices: Sequence[float], window: int) -> list[float | None]:
    """Calculate Simple Moving Average (SMA)."""
    if window <= 0:
        raise ValueError("Window must be positive")
    result: list[float | None] = []
    for i in range(len(prices)):
        if i + 1 < window:
            result.append(None)
        else:
            window_slice = prices[i + 1 - window : i + 1]
            result.append(round(sum(window_slice) / window, 4))
    return result


def calculate_max_drawdown(prices: Sequence[float]) -> float:
    """Calculate maximum peak-to-trough decline as a decimal (e.g. -0.20 for 20% drawdown)."""
    if not prices:
        return 0.0
    peak = prices[0]
    max_dd = 0.0
    for price in prices:
        if price > peak:
            peak = price
        elif peak > 0:
            dd = (price - peak) / peak
            if dd < max_dd:
                max_dd = dd
    return round(max_dd, 4)


def calculate_annualized_volatility(daily_returns: Sequence[float]) -> float:
    """Calculate annualized volatility assuming 252 trading days."""
    if len(daily_returns) < 2:
        return 0.0
    mean_ret = sum(daily_returns) / len(daily_returns)
    variance = sum((r - mean_ret) ** 2 for r in daily_returns) / (len(daily_returns) - 1)
    daily_std = math.sqrt(variance)
    return round(daily_std * math.sqrt(252), 4)
