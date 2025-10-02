from __future__ import annotations

from html import escape
import logging
from telegram import InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (CallbackQueryHandler, CommandHandler, ContextTypes,
                          MessageHandler, filters)

from ..localization import (PERSIAN_TEXTS, TextPack, get_text_pack,
                            normalize_language_code)
from ..services.analytics import AnalyticsTracker, NullAnalytics
from ..services.security import RateLimitGuard
from ..services.storage import ApplicationHistoryEntry, Storage
from ..ui.keyboards import (application_review_keyboard,
                            glass_dm_welcome_keyboard,
                            language_options_keyboard)

LOGGER = logging.getLogger(__name__)

class DMHandlers:
    def __init__(
        self,
        storage: Storage,
        owner_id: int,
        analytics: AnalyticsTracker | NullAnalytics | None = None,
        rate_limiter: RateLimitGuard | None = None,
    ) -> None:
        self.storage = storage
        self.owner_id = owner_id
        self.analytics = analytics or NullAnalytics()
        self.rate_limiter = rate_limiter or RateLimitGuard(10.0, 5)

    def build_handlers(self) -> list:
        private_filter = filters.ChatType.PRIVATE
        return [
            CommandHandler("start", self.start, filters=private_filter),
            CommandHandler("cancel", self.cancel, filters=private_filter),
            MessageHandler(private_filter & filters.TEXT & ~filters.COMMAND, self.receive_application),
            CallbackQueryHandler(self.handle_apply_callback, pattern="^apply_for_guild$"),
            CallbackQueryHandler(self.show_status_callback, pattern="^application_status$"),
            CallbackQueryHandler(self.handle_withdraw_callback, pattern="^application_withdraw$"),
            CallbackQueryHandler(self.show_language_menu, pattern="^language_menu$"),
            CallbackQueryHandler(self.close_language_menu, pattern="^close_language_menu$"),
            CallbackQueryHandler(self.set_language_callback, pattern=r"^set_language:"),
            CallbackQueryHandler(self.handle_application_action, pattern=r"^application:"),
            CommandHandler("pending", self.list_applications),
            CommandHandler("admins", self.list_admins),
            CommandHandler("promote", self.promote_admin),
            CommandHandler("demote", self.demote_admin),
            CommandHandler("status", self.status),
            CommandHandler("withdraw", self.withdraw),
        ]

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        user = update.effective_user
        if chat is None:
            return
        language_code = getattr(user, "language_code", None) if user else None
        texts = self._get_texts(context, language_code)
        await self.analytics.record("dm.start")
        try:
            await chat.send_message(
                text=self._build_welcome_text(texts),
                reply_markup=glass_dm_welcome_keyboard(texts),
                parse_mode=ParseMode.HTML,
            )
        except Exception as exc:
            LOGGER.error("Failed to send welcome message: %s", exc)

    async def handle_apply_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if not query:
            return

        await query.answer()
        user = query.from_user
        if user is None:
            return

        texts = self._get_texts(context, getattr(user, "language_code", None))
        await self.analytics.record("dm.apply_requested")
        if self.storage.is_admin(user.id):
            await query.edit_message_text(
                text=texts.dm_admin_only,
            )
            return

        if self.storage.has_application(user.id):
            await query.edit_message_text(texts.dm_application_duplicate)
            return

        context.user_data["is_filling_application"] = True
        await query.edit_message_text(
            text=texts.dm_application_started,
        )
        await query.message.chat.send_message(texts.dm_application_question)
        return

    async def receive_application(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not context.user_data.get("is_filling_application"):
            return

        user = update.effective_user
        if user is None or update.message is None:
            return

        texts = self._get_texts(context, getattr(user, "language_code", None))
        if not await self.rate_limiter.is_allowed(user.id):
            await self.analytics.record("dm.rate_limited")
            await update.message.reply_text(texts.dm_rate_limited)
            return
        answer = update.message.text.strip()
        try:
            async with self.analytics.track_time("dm.application_store"):
                success = await self.storage.add_application(
                    user_id=user.id,
                    full_name=user.full_name or user.username or str(user.id),
                    answer=answer,
                    language_code=context.user_data.get("preferred_language"),
                )
        except Exception as exc:
            LOGGER.error("Failed to persist application for %s: %s", user.id, exc)
            await self.analytics.record("dm.application_error")
            await update.message.reply_text(texts.error_generic)
            context.user_data.pop("is_filling_application", None)
            return
        if not success:
            LOGGER.warning("Duplicate application prevented for user %s", user.id)
            await update.message.reply_text(texts.dm_application_duplicate)
            context.user_data.pop("is_filling_application", None)
            return

        await update.message.reply_text(texts.dm_application_received)
        await self.analytics.record("dm.application_submitted")
        review_chat_id = context.bot_data.get("review_chat_id")
        if review_chat_id and context.application:
            context.application.create_task(
                context.bot.send_message(
                    chat_id=review_chat_id,
                    text=self._render_application_text(user.id),
                    parse_mode=ParseMode.HTML,
                    reply_markup=application_review_keyboard(user.id, PERSIAN_TEXTS),
                )
            )
        context.user_data.pop("is_filling_application", None)
        return

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        context.user_data.pop("is_filling_application", None)
        language_code = getattr(update.effective_user, "language_code", None)
        texts = self._get_texts(context, language_code)
        if update.message:
            await update.message.reply_text(texts.dm_cancelled)
        await self.analytics.record("dm.cancelled")

    async def list_applications(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        chat = update.effective_chat
        if user is None or chat is None:
            return
        texts = self._get_texts(context, getattr(user, "language_code", None))
        if not self.storage.is_admin(user.id):
            await chat.send_message(texts.dm_admin_only)
            return

        pending = self.storage.get_pending_applications()
        if not pending:
            await chat.send_message(texts.dm_no_pending)
            return

        await self.analytics.record("dm.admin_pending_list")

        for application in pending[:5]:
            await chat.send_message(
                text=self._render_application_text(application.user_id, texts),
                parse_mode=ParseMode.HTML,
                reply_markup=application_review_keyboard(application.user_id, texts),
            )

    async def handle_application_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if not query:
            return
        await query.answer()

        user = query.from_user
        language_code = getattr(user, "language_code", None) if user else None
        admin_texts = self._get_texts(context, language_code)
        if user is None:
            return
        if not self.storage.is_admin(user.id):
            await query.edit_message_text(admin_texts.dm_admin_only)
            return

        data = query.data
        if data == "application:skip":
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([]))
            await self.analytics.record("dm.admin_skip_application")
            return

        _, user_id_str, action = data.split(":")
        target_id = int(user_id_str)
        application = await self.storage.pop_application(target_id)
        if not application:
            await query.edit_message_text(admin_texts.dm_no_pending)
            return

        applicant_texts = get_text_pack(application.language_code)
        if action == "approve":
            await query.edit_message_text(admin_texts.dm_application_approved_admin)
            await self._notify_user(context, target_id, applicant_texts.dm_application_approved_user)
            await self.storage.mark_application_status(target_id, "approved")
            await self.analytics.record("dm.admin_application_approved")
        else:
            await query.edit_message_text(admin_texts.dm_application_denied_admin)
            await self._notify_user(context, target_id, applicant_texts.dm_application_denied_user)
            await self.storage.mark_application_status(target_id, "denied")
            await self.analytics.record("dm.admin_application_denied")

    async def _notify_user(self, context: ContextTypes.DEFAULT_TYPE, user_id: int, text: str) -> None:
        try:
            await context.bot.send_message(chat_id=user_id, text=text)
        except Exception as exc:
            LOGGER.error("Failed to notify user %s: %s", user_id, exc)

    async def list_admins(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        if chat is None:
            return
        language_code = getattr(update.effective_user, "language_code", None)
        texts = self._get_texts(context, language_code)
        admins = self.storage.list_admins()
        if not admins:
            await chat.send_message(texts.dm_no_admins)
            return
        formatted = "\n".join(str(admin) for admin in admins)
        await chat.send_message(texts.admin_list_header.format(admins=formatted))

    async def promote_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self._check_owner(update):
            return
        chat = update.effective_chat
        if chat is None:
            return
        language_code = getattr(update.effective_user, "language_code", None)
        texts = self._get_texts(context, language_code)
        if not context.args:
            await chat.send_message(texts.dm_admin_enter_user_id)
            return
        try:
            user_id = int(context.args[0])
        except ValueError:
            await chat.send_message(texts.dm_admin_invalid_user_id)
            return
        added = await self.storage.add_admin(user_id)
        if added:
            await chat.send_message(texts.dm_admin_added.format(user_id=user_id))
        else:
            await chat.send_message(texts.dm_already_admin.format(user_id=user_id))

    async def demote_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self._check_owner(update):
            return
        chat = update.effective_chat
        if chat is None:
            return
        language_code = getattr(update.effective_user, "language_code", None)
        texts = self._get_texts(context, language_code)
        if not context.args:
            await chat.send_message(texts.dm_admin_enter_user_id)
            return
        try:
            user_id = int(context.args[0])
        except ValueError:
            await chat.send_message(texts.dm_admin_invalid_user_id)
            return
        removed = await self.storage.remove_admin(user_id)
        if removed:
            await chat.send_message(texts.dm_admin_removed.format(user_id=user_id))
        else:
            await chat.send_message(texts.dm_not_admin.format(user_id=user_id))

    async def _check_owner(self, update: Update) -> bool:
        user = update.effective_user
        chat = update.effective_chat
        if user is None or chat is None:
            return False
        if user.id != self.owner_id:
            texts = get_text_pack(getattr(user, "language_code", None))
            await chat.send_message(texts.dm_not_owner)
            return False
        return True

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        chat = update.effective_chat
        if user is None or chat is None:
            return
        texts = self._get_texts(context, getattr(user, "language_code", None))
        text = self._render_status_text(self.storage.get_application_status(user.id), texts)
        await chat.send_message(text, parse_mode=ParseMode.HTML)
        await self.analytics.record("dm.status_requested")

    async def show_status_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if not query:
            return
        await query.answer()
        user = query.from_user
        if user is None:
            return
        message = query.message
        if message is None:
            return
        texts = self._get_texts(context, getattr(user, "language_code", None))
        text = self._render_status_text(self.storage.get_application_status(user.id), texts)
        await message.chat.send_message(text, parse_mode=ParseMode.HTML)
        await self.analytics.record("dm.status_requested")

    async def withdraw(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        chat = update.effective_chat
        if user is None or chat is None:
            return
        texts = self._get_texts(context, getattr(user, "language_code", None))
        success = await self.storage.withdraw_application(user.id)
        context.user_data.pop("is_filling_application", None)
        if success:
            await chat.send_message(texts.dm_withdraw_success)
            await self.analytics.record("dm.withdraw_completed")
        else:
            await chat.send_message(texts.dm_withdraw_not_found)
            await self.analytics.record("dm.withdraw_missing")

    async def handle_withdraw_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if not query:
            return
        await query.answer()
        user = query.from_user
        if user is None:
            return
        message = query.message
        if message is None:
            return
        texts = self._get_texts(context, getattr(user, "language_code", None))
        success = await self.storage.withdraw_application(user.id)
        context.user_data.pop("is_filling_application", None)
        if success:
            await message.chat.send_message(texts.dm_withdraw_success)
            await self.analytics.record("dm.withdraw_completed")
        else:
            await message.chat.send_message(texts.dm_withdraw_not_found)
            await self.analytics.record("dm.withdraw_missing")

    async def show_language_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if not query:
            return
        await query.answer()
        user = query.from_user
        message = query.message
        if message is None:
            return
        texts = self._get_texts(context, getattr(user, "language_code", None) if user else None)
        active = context.user_data.get("preferred_language") if isinstance(context.user_data, dict) else None
        await message.edit_text(
            text=texts.dm_language_menu_title,
            reply_markup=language_options_keyboard(active if isinstance(active, str) else None, texts),
        )
        await self.analytics.record("dm.language_menu_opened")

    async def close_language_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if not query:
            return
        await query.answer()
        message = query.message
        user = query.from_user
        if message is None:
            return
        texts = self._get_texts(context, getattr(user, "language_code", None) if user else None)
        await message.edit_text(
            text=self._build_welcome_text(texts),
            reply_markup=glass_dm_welcome_keyboard(texts),
            parse_mode=ParseMode.HTML,
        )
        await self.analytics.record("dm.language_menu_closed")

    async def set_language_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if not query:
            return
        data = query.data or ""
        parts = data.split(":", 1)
        if len(parts) != 2:
            await query.answer()
            return
        _, code = parts
        normalised = normalize_language_code(code) or code
        if isinstance(context.user_data, dict):
            context.user_data["preferred_language"] = normalised
        new_texts = get_text_pack(normalised)
        await self.analytics.record("dm.language_updated")
        await query.answer(new_texts.dm_language_updated, show_alert=True)
        message = query.message
        if message is None:
            return
        await message.edit_text(
            text=self._build_welcome_text(new_texts),
            reply_markup=glass_dm_welcome_keyboard(new_texts),
            parse_mode=ParseMode.HTML,
        )

    def _build_welcome_text(self, texts: TextPack) -> str:
        return f"{texts.dm_welcome}\n\n{texts.glass_panel_caption}"

    def _render_application_text(self, user_id: int, texts: TextPack | None = None) -> str:
        application = self.storage.get_application(user_id)
        text_pack = texts or PERSIAN_TEXTS
        if not application:
            return text_pack.dm_no_pending
        full_name = escape(str(application.full_name))
        raw_answer = application.answer if application.answer else "—"
        answer = escape(str(raw_answer))
        created_at = escape(str(application.created_at))
        return text_pack.dm_application_item.format(
            full_name=full_name,
            user_id=application.user_id,
            answer=answer,
            created_at=created_at,
        )

    def _render_status_text(self, status: ApplicationHistoryEntry | None, texts: TextPack | None = None) -> str:
        text_pack = texts or PERSIAN_TEXTS
        if not status:
            return text_pack.dm_status_none

        status_map = {
            "pending": text_pack.dm_status_pending,
            "approved": text_pack.dm_status_approved,
            "denied": text_pack.dm_status_denied,
            "withdrawn": text_pack.dm_status_withdrawn,
        }

        status_label = status_map.get(status.status)
        if not status_label:
            status_label = text_pack.dm_status_unknown.format(status=escape(status.status))

        updated_at = escape(status.updated_at)
        last_updated_label = text_pack.dm_status_last_updated_label

        if status.note:
            note = escape(status.note)
            return text_pack.dm_status_template_with_note.format(
                status=status_label,
                updated_at=updated_at,
                note=note,
                last_updated_label=last_updated_label,
            )

        return text_pack.dm_status_template.format(
            status=status_label,
            updated_at=updated_at,
            last_updated_label=last_updated_label,
        )

    def _get_texts(
        self,
        context: ContextTypes.DEFAULT_TYPE,
        language_code: str | None = None,
    ) -> TextPack:
        user_data = getattr(context, "user_data", None)
        stored_language = None
        if isinstance(user_data, dict):
            stored_language = user_data.get("preferred_language")

        normalised = normalize_language_code(language_code)
        if normalised:
            if isinstance(user_data, dict):
                user_data["preferred_language"] = normalised
            return get_text_pack(normalised)

        if isinstance(stored_language, str):
            return get_text_pack(stored_language)

        return get_text_pack(None)

