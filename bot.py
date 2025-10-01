from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from telegram.ext import AIORateLimiter, ApplicationBuilder

from flyzexbot.config import Settings
from flyzexbot.handlers.dm import DMHandlers
from flyzexbot.handlers.group import GroupHandlers
from flyzexbot.localization import PERSIAN_TEXTS
from flyzexbot.services.security import EncryptionManager
from flyzexbot.services.storage import Storage

CONFIG_PATH = Path("config/settings.yaml")


async def setup_logging(settings: Settings) -> None:
    logging.basicConfig(
        level=getattr(logging, settings.logging.level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    if settings.logging.file:
        settings.logging.file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(settings.logging.file, encoding="utf-8")
        file_handler.setLevel(getattr(logging, settings.logging.level.upper(), logging.INFO))
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        logging.getLogger().addHandler(file_handler)


async def build_application(settings: Settings) -> None:
    await setup_logging(settings)

    encryption = EncryptionManager(settings.get_secret_key())
    storage = Storage(settings.storage.path, encryption)
    await storage.load()

    if settings.telegram.owner_id not in storage.list_admins():
        await storage.add_admin(settings.telegram.owner_id)

    dm_handlers = DMHandlers(storage=storage, owner_id=settings.telegram.owner_id)
    group_handlers = GroupHandlers(
        storage=storage,
        xp_reward=settings.xp.message_reward,
        xp_limit=settings.xp.leaderboard_size,
        cups_limit=settings.cups.leaderboard_size,
    )

    application = (
        ApplicationBuilder()
        .token(settings.get_bot_token())
        .rate_limiter(AIORateLimiter())
        .concurrent_updates(True)
        .arbitrary_callback_data(True)
        .build()
    )

    application.bot_data["review_chat_id"] = settings.telegram.application_review_chat

    for handler in dm_handlers.build_handlers():
        application.add_handler(handler)

    for handler in group_handlers.build_handlers():
        application.add_handler(handler)

    async def post_init(app) -> None:
        await app.bot.set_my_commands(
            [
                ("start", "شروع"),
                ("pending", "درخواست‌های در صف (ادمین)"),
                ("admins", "لیست ادمین‌ها"),
                ("xp", "نمایش لیدربورد تجربه"),
                ("cups", "نمایش جام‌ها"),
            ]
        )

    application.post_init = post_init

    async def error_handler(update, context) -> None:  # noqa: ANN001, ANN201
        logging.getLogger(__name__).error("Exception while handling update", exc_info=context.error)
        if update and context.application:
            try:
                await context.application.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=PERSIAN_TEXTS.error_generic,
                )
            except Exception:  # noqa: BLE001 - best effort
                logging.getLogger(__name__).debug("Failed to notify user about error")

    application.add_error_handler(error_handler)

    await application.initialize()
    await application.start()
    await application.updater.start_polling(drop_pending_updates=True)

    logging.info("FlyzexBot is running with glass-panel UI.")

    try:
        await asyncio.Event().wait()
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


async def main() -> None:
    config_path = CONFIG_PATH if CONFIG_PATH.exists() else Path("config/settings.example.yaml")
    settings = Settings.load(config_path)
    await build_application(settings)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
