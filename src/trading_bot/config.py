"""Application configuration and safety guards."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


class ConfigurationError(ValueError):
    """Raised when configuration would violate the first-milestone safety boundary."""


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the read-only collector."""

    environment: str
    mcp_server_dir: Path | None
    data_dir: Path

    @classmethod
    def from_env(cls, environ: dict[str, str] | None = None) -> "Settings":
        values = os.environ if environ is None else environ
        environment = values.get("ENVIRONMENT", "demo").strip().lower()
        if environment != "demo":
            raise ConfigurationError(
                "Only ENVIRONMENT=demo is supported while the read-only milestone is implemented."
            )

        server_dir_value = values.get("TRADING212_MCP_SERVER_DIR", "").strip()
        data_dir = Path(values.get("TRADING_BOT_DATA_DIR", "./data")).expanduser()
        return cls(
            environment=environment,
            mcp_server_dir=Path(server_dir_value).expanduser() if server_dir_value else None,
            data_dir=data_dir,
        )
