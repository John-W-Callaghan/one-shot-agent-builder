"""Model selection strategy and configuration."""
import os
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """Maps agent roles to appropriate models."""

    # Judgment/reasoning — needs the strongest model
    STRATEGIST_MODEL: str = "claude-sonnet-5-5"
    ARCHITECT_MODEL: str = "claude-sonnet-5-5"
    SENTINEL_MODEL: str = "claude-sonnet-5-5"

    # Code generation — fast and capable
    FRONTEND_MODEL: str = "claude-sonnet-5-5"
    BACKEND_MODEL: str = "claude-sonnet-5-5"
    DESIGNER_MODEL: str = "claude-sonnet-5-5"

    # Mechanical/templated tasks — fast and cheap
    SHIPPER_MODEL: str = "claude-haiku-5-5"

    # Server-side refusal fallback (Claude API beta). If a request is declined by a
    # safety classifier, the API reruns it on a fallback model within the same call.
    # Not available for Haiku models. Set to False if your account lacks the beta.
    USE_REFUSAL_FALLBACK: bool = True
    REFUSAL_FALLBACK_BETA: str = "server-side-fallback-2026-07-01"

    @staticmethod
    def get_api_key() -> str:
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            raise ValueError(
                "ANTHROPIC_API_KEY not set. Copy .env.example to .env and add your key."
            )
        return key


# NOTE: In a production version with higher API budgets, you would use:
# - claude-opus-5-5 for STRATEGIST, ARCHITECT, SENTINEL (judgment roles)
# - claude-sonnet-5-5 for coding and design roles
# - claude-haiku-5-5 for SHIPPER (mechanical tasks)
#
# The current config uses Sonnet for everything except Shipper to keep
# API costs reasonable for a portfolio project. The architecture supports
# swapping models per-agent — that's the whole point of the config layer.
