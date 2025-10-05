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
    milestone_interval: int = 5


@dataclass
class CupConfig:
    leaderboard_size: int


@dataclass
class StorageConfig:
    path: Path
    backup_path: Optional[Path] = None


@dataclass
class LoggingConfig:
    level: str
    file: Optional[Path]


@dataclass
class WebAppConfig:
    host: str
    port: int
    url: Optional[str] = None

    def get_url(self) -> Optional[str]:
        """Return a fully-qualified URL for the configured WebApp."""

        if self.url:
            return self.url

        if not self.host:
            return None

        scheme = "https" if self.port == 443 else "http"
        if self.port in (80, 443):
            return f"{scheme}://{self.host}"

        return f"{scheme}://{self.host}:{self.port}"


@dataclass
class SecurityConfig:
    rate_limit_interval: float
    rate_limit_burst: int


@dataclass
class AnalyticsConfig:
    flush_interval: float


@dataclass
class Settings:
    telegram: TelegramConfig
    xp: XPConfig
    cups: CupConfig
    storage: StorageConfig
    logging: LoggingConfig
    webapp: WebAppConfig
    security: SecurityConfig
    analytics: AnalyticsConfig

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
            milestone_interval=int(data["xp"].get("milestone_interval", 5)),
        )

        cups = CupConfig(
            leaderboard_size=int(data["cups"]["leaderboard_size"]),
        )

        storage = StorageConfig(
            path=Path(data["storage"]["path"]),
            backup_path=Path(data["storage"]["backup_path"]) if data["storage"].get("backup_path") else None,
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
            url=webapp_cfg.get("url"),
        )

        security_cfg = data.get("security", {})
        security = SecurityConfig(
            rate_limit_interval=float(security_cfg.get("rate_limit_interval", 10.0)),
            rate_limit_burst=int(security_cfg.get("rate_limit_burst", 5)),
        )

        analytics_cfg = data.get("analytics", {})
        analytics = AnalyticsConfig(
            flush_interval=float(analytics_cfg.get("flush_interval", 60.0)),
        )

        return cls(
            telegram=telegram,
            xp=xp,
            cups=cups,
            storage=storage,
            logging=logging_config,
            webapp=webapp,
            security=security,
            analytics=analytics,
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

