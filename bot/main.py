"""Telegram bot entrypoint for managing Flyzex guild applications."""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .config import BotConfig, load_config
from .storage import Application, ApplicationStore

logger = logging.getLogger(__name__)


class ApplicationStates(StatesGroup):
    collecting = State()


router = Router()


def build_admin_keyboard(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Accept", callback_data=f"accept:{user_id}")
    builder.button(text="❌ Reject", callback_data=f"reject:{user_id}")
    builder.adjust(2)
    return builder.as_markup()


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext, config: BotConfig, store: ApplicationStore) -> None:
    user_id = message.from_user.id
    if user_id in config.admin_ids:
        await message.answer(
            "👋 Admin mode activated. Use /pending to see outstanding guild applications."
        )
        await state.clear()
        return

    if store.get_pending(user_id):
        await message.answer(
            "We have already received your application and it is waiting for admin review."
        )
        return

    if store.get_history(user_id):
        await message.answer(
            "Our records show that you have already applied. If you believe this is a mistake, please contact an admin."
        )
        return

    await state.set_state(ApplicationStates.collecting)
    await state.update_data(answers=[], question_index=0)
    await message.answer(
        "Welcome to the Flyzex guild intake bot! Please answer the following questions to apply for membership."
    )
    await ask_next_question(message, state, config.questions)


async def ask_next_question(message: Message, state: FSMContext, questions: List[str]) -> None:
    data = await state.get_data()
    index = data.get("question_index", 0)
    if index >= len(questions):
        await message.answer("Thank you! Your application has been submitted for review.")
        await state.clear()
        return

    await message.answer(questions[index])


@router.message(ApplicationStates.collecting)
async def collect_answer(message: Message, state: FSMContext, config: BotConfig, store: ApplicationStore, bot: Bot) -> None:
    data = await state.get_data()
    answers: List[Dict[str, str]] = data.get("answers", [])
    question_index = data.get("question_index", 0)

    if question_index >= len(config.questions):
        await message.answer("All questions have already been answered.")
        return

    answers.append({"question": config.questions[question_index], "answer": message.text or ""})
    await state.update_data(answers=answers, question_index=question_index + 1)

    if question_index + 1 == len(config.questions):
        application = Application(
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            answers=answers,
        )
        store.add_pending(application)
        await notify_admins(bot, config, application)
        await message.answer(
            "Your answers have been sent to the guild admins. You will receive a response soon."
        )
        await state.clear()
        return

    await ask_next_question(message, state, config.questions)


async def notify_admins(bot: Bot, config: BotConfig, application: Application) -> None:
    keyboard = build_admin_keyboard(application.user_id)
    for admin_id in config.admin_ids:
        try:
            await bot.send_message(
                admin_id,
                text=application.format_for_admin(),
                reply_markup=keyboard,
            )
        except TelegramBadRequest as exc:  # pragma: no cover - network errors
            logger.warning("Failed to notify admin %s: %s", admin_id, exc)


@router.callback_query(F.data.startswith("accept"))
async def accept_application(callback: CallbackQuery, config: BotConfig, store: ApplicationStore, bot: Bot) -> None:
    if not await validate_admin(callback, config):
        return

    user_id = int(callback.data.split(":", 1)[1])
    application = store.pop_pending(user_id)
    if not application:
        await callback.answer("This application has already been processed.", show_alert=True)
        return

    await callback.message.edit_reply_markup()
    await callback.message.answer("Application approved. Invitation sent to the applicant.")
    await bot.send_message(
        user_id,
        "🎉 Congratulations! Your application has been approved. Here is your invite code:\n"
        f"<code>{config.invite_code}</code>",
        parse_mode=ParseMode.HTML,
    )
    await callback.answer("Applicant accepted.")


@router.callback_query(F.data.startswith("reject"))
async def reject_application(callback: CallbackQuery, config: BotConfig, store: ApplicationStore, bot: Bot) -> None:
    if not await validate_admin(callback, config):
        return

    user_id = int(callback.data.split(":", 1)[1])
    application = store.pop_pending(user_id)
    if not application:
        await callback.answer("This application has already been processed.", show_alert=True)
        return

    await callback.message.edit_reply_markup()
    await callback.message.answer("Application rejected. The applicant has been notified.")
    await bot.send_message(
        user_id,
        "Thank you for your interest, but your application was not approved at this time.",
    )
    await callback.answer("Applicant rejected.")


async def validate_admin(callback: CallbackQuery, config: BotConfig) -> bool:
    if callback.from_user.id not in config.admin_ids:
        await callback.answer("Only admins can take this action.", show_alert=True)
        return False
    return True


@router.message(Command("pending"))
async def list_pending(message: Message, config: BotConfig, store: ApplicationStore) -> None:
    if message.from_user.id not in config.admin_ids:
        await message.answer("You are not authorised to use this command.")
        return

    pending = list(store.list_pending())
    if not pending:
        await message.answer("There are no pending applications.")
        return

    lines = ["Pending applications:"]
    for application in pending:
        lines.append(f"• {application.full_name} (ID: {application.user_id})")
    await message.answer("\n".join(lines))


@router.message(Command("history"))
async def show_history(message: Message, config: BotConfig, store: ApplicationStore) -> None:
    if message.from_user.id not in config.admin_ids:
        await message.answer("You are not authorised to use this command.")
        return

    text = message.text or ""
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /history <user_id>")
        return

    try:
        target_id = int(parts[1])
    except ValueError:
        await message.answer("Usage: /history <user_id>")
        return

    application = store.get_history(target_id)
    if application is None:
        await message.answer("No application history found for that user.")
        return

    await message.answer(application.format_for_admin())


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    config = load_config()
    store = ApplicationStore(config.storage_path)
    bot = Bot(token=config.bot_token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    dp[BotConfig] = config
    dp[ApplicationStore] = store

    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
