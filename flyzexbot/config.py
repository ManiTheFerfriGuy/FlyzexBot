"""Configuration loader for FlyzexBot."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


@dataclass
class TelegramConfig:
    bot_token_env: str
    secret_key_env: str
    owner_id: int
    application_review_chat: Optional[int]


@dataclass
class XPConfig:
    message_reward: int
    leaderboard_size: int


@dataclass
class CupConfig:
    leaderboard_size: int


@dataclass
class StorageConfig:
    path: Path


@dataclass
class LoggingConfig:
    level: str
    file: Optional[Path]


@dataclass
class WebAppConfig:
    host: str
    port: int


@dataclass
class Settings:
    telegram: TelegramConfig
    xp: XPConfig
    cups: CupConfig
    storage: StorageConfig
    logging: LoggingConfig
    webapp: WebAppConfig

    @classmethod
    def load(cls, path: Path) -> "Settings":
        with path.open("r", encoding="utf-8") as config_file:
            data: Dict[str, Any] = yaml.safe_load(config_file)

        telegram = TelegramConfig(
            bot_token_env=data["telegram"]["bot_token_env"],
            secret_key_env=data["telegram"].get("secret_key_env", "BOT_SECRET_KEY"),
            owner_id=int(data["telegram"]["owner_id"]),
            application_review_chat=data["telegram"].get("application_review_chat"),
        )

        xp = XPConfig(
            message_reward=int(data["xp"]["message_reward"]),
            leaderboard_size=int(data["xp"]["leaderboard_size"]),
        )

        cups = CupConfig(
            leaderboard_size=int(data["cups"]["leaderboard_size"]),
        )

        storage = StorageConfig(
            path=Path(data["storage"]["path"]),
        )

        logging_cfg = data.get("logging", {})
        logging_config = LoggingConfig(
            level=logging_cfg.get("level", "INFO"),
            file=Path(logging_cfg["file"]) if logging_cfg.get("file") else None,
        )

        webapp_cfg = data.get("webapp", {})
        webapp = WebAppConfig(
            host=webapp_cfg.get("host", "0.0.0.0"),
            port=int(webapp_cfg.get("port", 8080)),
        )

        return cls(
            telegram=telegram,
            xp=xp,
            cups=cups,
            storage=storage,
            logging=logging_config,
            webapp=webapp,
        )

    def get_bot_token(self) -> str:
        token = os.getenv(self.telegram.bot_token_env)
        if not token:
            raise RuntimeError(
                f"Bot token not found in environment variable '{self.telegram.bot_token_env}'."
            )
        return token

    def get_secret_key(self) -> bytes:
        key = os.getenv(self.telegram.secret_key_env)
        if not key:
            raise RuntimeError(
                "Secret key for encrypting storage is missing."
            )
        return key.encode("utf-8")

