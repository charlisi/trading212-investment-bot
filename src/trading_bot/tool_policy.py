"""MCP tool authorization policy for the read-only milestone."""

from __future__ import annotations

READ_ONLY_TOOLS = frozenset(
    {
        "fetch_account_summary",
        "fetch_account_cash",
        "fetch_account_info",
        "fetch_positions",
        "fetch_position_by_ticker",
        "fetch_all_open_positions",
        "fetch_open_position_by_ticker",
        "search_specific_position_by_ticker",
        "fetch_all_orders",
        "fetch_order",
        "search_instrument",
        "search_exchange",
        "fetch_historical_order_data",
        "fetch_paid_out_dividends",
        "fetch_transaction_list",
        "fetch_exports_list",
    }
)

BLOCKED_TOOLS = frozenset(
    {
        "place_market_order",
        "place_limit_order",
        "place_stop_order",
        "place_stop_limit_order",
        "cancel_order",
        "fetch_pies",
        "fetch_a_pie",
        "create_pie",
        "update_pie",
        "duplicate_pie",
        "delete_pie",
        "request_csv_export",
    }
)


class ToolPolicyError(PermissionError):
    """Raised when a tool is outside the first-milestone policy."""


def ensure_read_only_tool(tool_name: str) -> None:
    """Allow only explicitly listed read tools."""
    if tool_name not in READ_ONLY_TOOLS:
        raise ToolPolicyError(f"MCP tool is not allowed in read-only mode: {tool_name}")
