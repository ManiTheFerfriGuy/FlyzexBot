"""Inline keyboards for the glass panel UI."""
from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from ..localization import PERSIAN_TEXTS, TextPack


def glass_dm_welcome_keyboard(texts: TextPack | None = None) -> InlineKeyboardMarkup:
    text_pack = texts or PERSIAN_TEXTS
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=f"🪟 {text_pack.dm_apply_button}",
                    callback_data="apply_for_guild",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"📨 {text_pack.dm_status_button}",
                    callback_data="application_status",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"❌ {text_pack.dm_withdraw_button}",
                    callback_data="application_withdraw",
                )
            ],
        ]
    )


def application_review_keyboard(user_id: int, texts: TextPack | None = None) -> InlineKeyboardMarkup:
    text_pack = texts or PERSIAN_TEXTS
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text_pack.dm_application_action_buttons["approve"],
                    callback_data=f"application:{user_id}:approve",
                ),
                InlineKeyboardButton(
                    text_pack.dm_application_action_buttons["deny"],
                    callback_data=f"application:{user_id}:deny",
                ),
            ],
            [
                InlineKeyboardButton(
                    text_pack.dm_application_action_buttons["skip"],
                    callback_data="application:skip",
                )
            ],
        ]
    )

