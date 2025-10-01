"""Direct message handlers for FlyzexBot."""
from __future__ import annotations

from html import escape
import logging
from telegram import InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (CallbackQueryHandler, CommandHandler, ContextTypes,
                          MessageHandler, filters)

from ..localization import PERSIAN_TEXTS
from ..services.storage import Storage
from ..ui.keyboards import (application_review_keyboard,
                            glass_dm_welcome_keyboard)

LOGGER = logging.getLogger(__name__)

class DMHandlers:
    def __init__(self, storage: Storage, owner_id: int) -> None:
        self.storage = storage
        self.owner_id = owner_id

    def build_handlers(self) -> list:
        private_filter = filters.ChatType.PRIVATE
        return [
            CommandHandler("start", self.start, filters=private_filter),
            CommandHandler("cancel", self.cancel, filters=private_filter),
            MessageHandler(private_filter & filters.TEXT & ~filters.COMMAND, self.receive_application),
            CallbackQueryHandler(self.handle_apply_callback, pattern="^apply_for_guild$"),
            CallbackQueryHandler(self.handle_application_action, pattern=r"^application:"),
            CommandHandler("pending", self.list_applications),
            CommandHandler("admins", self.list_admins),
            CommandHandler("promote", self.promote_admin),
            CommandHandler("demote", self.demote_admin),
        ]

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_chat is None:
            return

        await update.effective_chat.send_message(
            text=f"{PERSIAN_TEXTS.dm_welcome}\n\n{PERSIAN_TEXTS.glass_panel_caption}",
            reply_markup=glass_dm_welcome_keyboard(),
            parse_mode=ParseMode.HTML,
        )

    async def handle_apply_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if not query:
            return

        await query.answer()
        user = query.from_user
        if user is None:
            return

        if self.storage.is_admin(user.id):
            await query.edit_message_text(
                text=PERSIAN_TEXTS.dm_admin_only,
            )
            return

        if self.storage.has_application(user.id):
            await query.edit_message_text(PERSIAN_TEXTS.dm_application_duplicate)
            return

        context.user_data["is_filling_application"] = True
        await query.edit_message_text(
            text=PERSIAN_TEXTS.dm_application_started,
        )
        await query.message.chat.send_message(PERSIAN_TEXTS.dm_application_question)
        return

    async def receive_application(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not context.user_data.get("is_filling_application"):
            return

        user = update.effective_user
        if user is None or update.message is None:
            return

        answer = update.message.text.strip()
        success = await self.storage.add_application(
            user_id=user.id,
            full_name=user.full_name or user.username or str(user.id),
            answer=answer,
        )
        if not success:
            LOGGER.warning("Duplicate application prevented for user %s", user.id)
            await update.message.reply_text(PERSIAN_TEXTS.dm_application_duplicate)
            context.user_data.pop("is_filling_application", None)
            return

        await update.message.reply_text(PERSIAN_TEXTS.dm_application_received)
        review_chat_id = context.bot_data.get("review_chat_id")
        if review_chat_id:
            await context.bot.send_message(
                chat_id=review_chat_id,
                text=self._render_application_text(user.id),
                parse_mode=ParseMode.HTML,
                reply_markup=application_review_keyboard(user.id),
            )
        context.user_data.pop("is_filling_application", None)
        return

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        context.user_data.pop("is_filling_application", None)
        if update.message:
            await update.message.reply_text("فرآیند درخواست لغو شد.")

    async def list_applications(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        chat = update.effective_chat
        if user is None or chat is None:
            return
        if not self.storage.is_admin(user.id):
            await chat.send_message(PERSIAN_TEXTS.dm_admin_only)
            return

        pending = self.storage.get_pending_applications()
        if not pending:
            await chat.send_message(PERSIAN_TEXTS.dm_no_pending)
            return

        for application in pending[:5]:
            await chat.send_message(
                text=self._render_application_text(application.user_id),
                parse_mode=ParseMode.HTML,
                reply_markup=application_review_keyboard(application.user_id),
            )

    async def handle_application_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        if not query:
            return
        await query.answer()

        user = query.from_user
        if user is None or not self.storage.is_admin(user.id):
            await query.edit_message_text(PERSIAN_TEXTS.dm_admin_only)
            return

        data = query.data
        if data == "application:skip":
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([]))
            return

        _, user_id_str, action = data.split(":")
        target_id = int(user_id_str)
        application = await self.storage.pop_application(target_id)
        if not application:
            await query.edit_message_text(PERSIAN_TEXTS.dm_no_pending)
            return

        if action == "approve":
            await query.edit_message_text(PERSIAN_TEXTS.dm_application_approved_admin)
            await self._notify_user(context, target_id, PERSIAN_TEXTS.dm_application_approved_user)
        else:
            await query.edit_message_text(PERSIAN_TEXTS.dm_application_denied_admin)
            await self._notify_user(context, target_id, PERSIAN_TEXTS.dm_application_denied_user)

    async def _notify_user(self, context: ContextTypes.DEFAULT_TYPE, user_id: int, text: str) -> None:
        try:
            await context.bot.send_message(chat_id=user_id, text=text)
        except Exception as exc:  # noqa: BLE001 - handled generically
            LOGGER.error("Failed to notify user %s: %s", user_id, exc)

    async def list_admins(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        if chat is None:
            return
        admins = self.storage.list_admins()
        if not admins:
            await chat.send_message(PERSIAN_TEXTS.dm_no_admins)
            return
        formatted = "\n".join(str(admin) for admin in admins)
        await chat.send_message(PERSIAN_TEXTS.admin_list_header.format(admins=formatted))

    async def promote_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self._check_owner(update):
            return
        if not context.args:
            await update.effective_chat.send_message("لطفاً شناسه کاربر را وارد کنید.")
            return
        user_id = int(context.args[0])
        added = await self.storage.add_admin(user_id)
        if added:
            await update.effective_chat.send_message(PERSIAN_TEXTS.dm_admin_added.format(user_id=user_id))
        else:
            await update.effective_chat.send_message(PERSIAN_TEXTS.dm_already_admin.format(user_id=user_id))

    async def demote_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not await self._check_owner(update):
            return
        if not context.args:
            await update.effective_chat.send_message("لطفاً شناسه کاربر را وارد کنید.")
            return
        user_id = int(context.args[0])
        removed = await self.storage.remove_admin(user_id)
        if removed:
            await update.effective_chat.send_message(PERSIAN_TEXTS.dm_admin_removed.format(user_id=user_id))
        else:
            await update.effective_chat.send_message(PERSIAN_TEXTS.dm_not_admin.format(user_id=user_id))

    async def _check_owner(self, update: Update) -> bool:
        user = update.effective_user
        chat = update.effective_chat
        if user is None or chat is None:
            return False
        if user.id != self.owner_id:
            await chat.send_message(PERSIAN_TEXTS.dm_not_owner)
            return False
        return True

    def _render_application_text(self, user_id: int) -> str:
        application = self.storage.get_application(user_id)
        if not application:
            return PERSIAN_TEXTS.dm_no_pending
        full_name = escape(str(application.full_name))
        raw_answer = application.answer if application.answer else "—"
        answer = escape(str(raw_answer))
        created_at = escape(str(application.created_at))
        return PERSIAN_TEXTS.dm_application_item.format(
            full_name=full_name,
            user_id=application.user_id,
            answer=answer,
            created_at=created_at,
        )

