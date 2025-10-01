"""Group handlers for FlyzexBot."""
from __future__ import annotations

from html import escape
import logging
from typing import List, Sequence, Tuple

from telegram import ChatMember, Update
from telegram.constants import ParseMode
from telegram.ext import (CommandHandler, ContextTypes, MessageHandler,
                          filters)

from ..localization import PERSIAN_TEXTS
from ..services.storage import Storage

LOGGER = logging.getLogger(__name__)


class GroupHandlers:
    def __init__(self, storage: Storage, xp_reward: int, xp_limit: int, cups_limit: int) -> None:
        self.storage = storage
        self.xp_reward = xp_reward
        self.xp_limit = xp_limit
        self.cups_limit = cups_limit

    def build_handlers(self) -> list:
        return [
            MessageHandler(filters.TEXT & filters.ChatType.GROUPS, self.track_activity),
            CommandHandler("xp", self.show_xp_leaderboard, filters=filters.ChatType.GROUPS),
            CommandHandler("cups", self.show_cup_leaderboard, filters=filters.ChatType.GROUPS),
            CommandHandler("add_cup", self.add_cup, filters=filters.ChatType.GROUPS),
        ]

    async def track_activity(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message = update.effective_message
        if message is None or update.effective_chat is None or update.effective_user is None:
            return
        if message.text and message.text.startswith("/"):
            return  # ignore commands

        new_score = await self.storage.add_xp(
            chat_id=update.effective_chat.id,
            user_id=update.effective_user.id,
            amount=self.xp_reward,
        )
        if new_score % (self.xp_reward * 5) == 0:
            await message.reply_text(
                PERSIAN_TEXTS.group_xp_updated.format(
                    full_name=update.effective_user.full_name
                    or update.effective_user.username
                    or str(update.effective_user.id),
                    xp=new_score,
                )
            )

    async def show_xp_leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        if chat is None:
            return
        leaderboard = self.storage.get_xp_leaderboard(chat.id, self.xp_limit)
        if not leaderboard:
            await chat.send_message(PERSIAN_TEXTS.group_no_data)
            return

        resolved = await self._resolve_leaderboard_names(context, chat.id, leaderboard)

        lines: List[str] = [PERSIAN_TEXTS.group_xp_leaderboard_title]
        for index, (display_name, xp) in enumerate(resolved, start=1):
            safe_name = escape(str(display_name))
            lines.append(f"{index}. <b>{safe_name}</b> — <code>{xp}</code>")
        await chat.send_message("\n".join(lines), parse_mode=ParseMode.HTML)

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

        await self.storage.add_cup(chat.id, title, description, podium)
        await chat.send_message(PERSIAN_TEXTS.group_cup_added.format(title=title))

    async def show_cup_leaderboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        if chat is None:
            return
        cups = self.storage.get_cups(chat.id, self.cups_limit)
        if not cups:
            await chat.send_message(PERSIAN_TEXTS.group_no_data)
            return

        lines: List[str] = [PERSIAN_TEXTS.group_cup_leaderboard_title]
        for cup in cups:
            title = escape(str(cup.get("title", "")))
            description = escape(str(cup.get("description", "")))
            podium_entries = [escape(str(slot)) for slot in cup.get("podium", []) if slot]
            podium = "، ".join(podium_entries) if podium_entries else "—"
            lines.append(
                f"<b>{title}</b> — {description}\n🥇 {podium}"
            )
        await chat.send_message("\n\n".join(lines), parse_mode=ParseMode.HTML)

    async def _is_admin(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int) -> bool:
        try:
            member: ChatMember = await context.bot.get_chat_member(chat_id, user_id)
        except Exception as exc:  # noqa: BLE001
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

