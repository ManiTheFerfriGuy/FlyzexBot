from __future__ import annotations

from html import escape
import logging
from typing import List, Sequence, Tuple

from telegram import ChatMember, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (CallbackQueryHandler, CommandHandler, ContextTypes,
                          MessageHandler, filters)

from ..localization import PERSIAN_TEXTS
from ..services.analytics import AnalyticsTracker, NullAnalytics
from ..services.storage import Storage
from ..ui.keyboards import leaderboard_refresh_keyboard

LOGGER = logging.getLogger(__name__)


class GroupHandlers:
    def __init__(
        self,
        storage: Storage,
        xp_reward: int,
        xp_limit: int,
        cups_limit: int,
        analytics: AnalyticsTracker | NullAnalytics | None = None,
    ) -> None:
        self.storage = storage
        self.xp_reward = xp_reward
        self.xp_limit = xp_limit
        self.cups_limit = cups_limit
        self.analytics = analytics or NullAnalytics()

    def build_handlers(self) -> list:
        return [
            MessageHandler(filters.TEXT & filters.ChatType.GROUPS, self.track_activity),
            CommandHandler("xp", self.show_xp_leaderboard, filters=filters.ChatType.GROUPS),
            CommandHandler("cups", self.show_cup_leaderboard, filters=filters.ChatType.GROUPS),
            CommandHandler("add_cup", self.add_cup, filters=filters.ChatType.GROUPS),
            CallbackQueryHandler(self.handle_leaderboard_refresh, pattern=r"^leaderboard:"),
        ]

    async def track_activity(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message = update.effective_message
        if message is None or update.effective_chat is None or update.effective_user is None:
            return
        if message.text and message.text.startswith("/"):
            return
        try:
            async with self.analytics.track_time("group.track_activity"):
                new_score = await self.storage.add_xp(
                    chat_id=update.effective_chat.id,
                    user_id=update.effective_user.id,
                    amount=self.xp_reward,
                )
        except Exception as exc:
            LOGGER.error("Failed to update XP for %s: %s", update.effective_user.id, exc)
            await self.analytics.record("group.activity_error")
            return
        if new_score % (self.xp_reward * 5) == 0:
            await message.reply_text(
                PERSIAN_TEXTS.group_xp_updated.format(
                    full_name=update.effective_user.full_name
                    or update.effective_user.username
                    or str(update.effective_user.id),
                    xp=new_score,
                )
            )
        await self.analytics.record("group.activity_tracked")

    async def show_xp_leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        if chat is None:
            return
        await self.analytics.record("group.xp_leaderboard_requested")
        text, mode, markup = await self._compose_xp_leaderboard(context, chat.id)
        await chat.send_message(text, parse_mode=mode, reply_markup=markup)

    async def add_cup(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        user = update.effective_user
        if chat is None or user is None:
            return
        if not await self._is_admin(context, chat.id, user.id):
            await chat.send_message(PERSIAN_TEXTS.dm_admin_only)
            return
        if len(context.args) < 2:
            await chat.send_message("استفاده: /add_cup عنوان | توضیح | قهرمان,نایب‌قهرمان,سوم")
            return

        raw = " ".join(context.args)
        try:
            title, description, podium_raw = [part.strip() for part in raw.split("|")]
            podium = [slot.strip() for slot in podium_raw.split(",") if slot.strip()]
        except ValueError:
            await chat.send_message("ساختار ورودی صحیح نیست. از جداکننده | استفاده کنید.")
            return

        try:
            await self.storage.add_cup(chat.id, title, description, podium)
        except Exception as exc:
            LOGGER.error("Failed to add cup in chat %s: %s", chat.id, exc)
            await chat.send_message(PERSIAN_TEXTS.group_no_data)
            await self.analytics.record("group.cup_add_error")
            return
        await chat.send_message(PERSIAN_TEXTS.group_cup_added.format(title=title))
        await self.analytics.record("group.cup_added")

    async def show_cup_leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        if chat is None:
            return
        await self.analytics.record("group.cup_leaderboard_requested")
        text, mode, markup = self._compose_cup_leaderboard(chat.id)
        await chat.send_message(text, parse_mode=mode, reply_markup=markup)

    async def handle_leaderboard_refresh(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if not query or not query.data:
            return
        await query.answer()
        parts = query.data.split(":", 2)
        if len(parts) != 3:
            return
        _, board_type, chat_id_raw = parts
        message = query.message
        if message is None:
            return
        try:
            chat_id = int(chat_id_raw)
        except ValueError:
            return
        if board_type == "xp":
            text, mode, markup = await self._compose_xp_leaderboard(context, chat_id)
            await self.analytics.record("group.xp_leaderboard_refreshed")
        else:
            text, mode, markup = self._compose_cup_leaderboard(chat_id)
            await self.analytics.record("group.cup_leaderboard_refreshed")
        await message.edit_text(text, parse_mode=mode, reply_markup=markup)

    async def _is_admin(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int) -> bool:
        try:
            member: ChatMember = await context.bot.get_chat_member(chat_id, user_id)
        except Exception as exc:
            LOGGER.error("Failed to fetch chat member: %s", exc)
            return False
        return member.status in {"administrator", "creator"} or self.storage.is_admin(user_id)

    async def _resolve_leaderboard_names(
        self,
        context: ContextTypes.DEFAULT_TYPE,
        chat_id: int,
        leaderboard: Sequence[Tuple[str, int]],
    ) -> List[Tuple[str, int]]:
        resolved: List[Tuple[str, int]] = []
        for user_id, xp in leaderboard:
            try:
                member = await context.bot.get_chat_member(chat_id, int(user_id))
                display = member.user.full_name or member.user.username or f"کاربر {user_id}"
            except Exception:
                display = f"کاربر {user_id}"
            resolved.append((display, xp))
        return resolved

    async def _compose_xp_leaderboard(
        self,
        context: ContextTypes.DEFAULT_TYPE,
        chat_id: int,
    ) -> Tuple[str, ParseMode | None, InlineKeyboardMarkup | None]:
        leaderboard = self.storage.get_xp_leaderboard(chat_id, self.xp_limit)
        if not leaderboard:
            return (PERSIAN_TEXTS.group_no_data, None, None)
        resolved = await self._resolve_leaderboard_names(context, chat_id, leaderboard)
        lines: List[str] = [PERSIAN_TEXTS.group_xp_leaderboard_title]
        for index, (display_name, xp) in enumerate(resolved, start=1):
            safe_name = escape(str(display_name))
            lines.append(f"{index}. <b>{safe_name}</b> — <code>{xp}</code>")
        text = "\n".join(lines)
        markup = leaderboard_refresh_keyboard("xp", chat_id, PERSIAN_TEXTS)
        return (text, ParseMode.HTML, markup)

    def _compose_cup_leaderboard(
        self,
        chat_id: int,
    ) -> Tuple[str, ParseMode | None, InlineKeyboardMarkup | None]:
        cups = self.storage.get_cups(chat_id, self.cups_limit)
        if not cups:
            return (PERSIAN_TEXTS.group_no_data, None, None)
        lines: List[str] = [PERSIAN_TEXTS.group_cup_leaderboard_title]
        for cup in cups:
            title = escape(str(cup.get("title", "")))
            description = escape(str(cup.get("description", "")))
            podium_entries = [escape(str(slot)) for slot in cup.get("podium", []) if slot]
            podium = "، ".join(podium_entries) if podium_entries else "—"
            lines.append(f"<b>{title}</b> — {description}\n🥇 {podium}")
        text = "\n\n".join(lines)
        markup = leaderboard_refresh_keyboard("cups", chat_id, PERSIAN_TEXTS)
        return (text, ParseMode.HTML, markup)

