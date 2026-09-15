from __future__ import annotations

import pytest

from trading_bot.config import ConfigurationError, Settings
from trading_bot.tool_policy import ToolPolicyError, ensure_read_only_tool


def test_settings_default_to_demo() -> None:
    settings = Settings.from_env({})
    assert settings.environment == "demo"


def test_live_environment_is_rejected() -> None:
    with pytest.raises(ConfigurationError):
        Settings.from_env({"ENVIRONMENT": "live"})


def test_known_read_tool_is_allowed() -> None:
    ensure_read_only_tool("fetch_positions")


@pytest.mark.parametrize(
    "tool_name",
    ["place_market_order", "cancel_order", "create_pie", "request_csv_export"],
)
def test_mutation_capable_tools_are_rejected(tool_name: str) -> None:
    with pytest.raises(ToolPolicyError):
        ensure_read_only_tool(tool_name)


def test_unknown_tools_are_rejected() -> None:
    with pytest.raises(ToolPolicyError):
        ensure_read_only_tool("unknown_tool")
