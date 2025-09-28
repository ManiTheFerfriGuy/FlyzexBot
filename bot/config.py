"""Configuration for the Flyzex guild application bot.

Edit this file to configure admin accounts, onboarding questions, and the
invite code that should be sent to approved applicants. Only the bot token is
expected to come from the environment for security reasons.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from typing import List


@dataclass(slots=True)
class BotConfig:
    """Settings that control bot behaviour.

    Attributes
    ----------
    bot_token:
        The Telegram bot token. Read from the ``BOT_TOKEN`` environment
        variable.
    admin_ids:
        Telegram user IDs that are allowed to review guild applications.
    questions:
        The questions shown to applicants when they start the bot.
    invite_code:
        Code or link returned to applicants that have been approved.
    storage_path:
        File system location used to persist pending applications.
    """

    bot_token: str
    admin_ids: List[int]
    questions: List[str]
    invite_code: str
    storage_path: str = field(default="data/applications.json")


def load_config() -> BotConfig:
    """Create a :class:`BotConfig` instance from local settings."""

    bot_token = os.environ.get("BOT_TOKEN", "")
    if not bot_token:
        raise RuntimeError(
            "BOT_TOKEN environment variable is required. Obtain it from BotFather and set it before starting the bot."
        )

    # ------------------------------------------------------------------
    # Customise the following values to match your guild's workflow.
    # ------------------------------------------------------------------
    admin_ids: List[int] = [123456789]  # Replace with your Telegram user IDs

    questions: List[str] = [
        "Why do you want to join the guild?",
        "What experience do you have that can benefit the guild?",
        "Provide a brief introduction about yourself.",
    ]

    invite_code = "YOUR-GUILD-INVITE-CODE"

    return BotConfig(
        bot_token=bot_token,
        admin_ids=admin_ids,
        questions=questions,
        invite_code=invite_code,
    )


__all__ = ["BotConfig", "load_config"]
