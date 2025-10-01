"""Inline keyboards for the glass panel UI."""
from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from ..localization import PERSIAN_TEXTS


def glass_dm_welcome_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=f"🪟 {PERSIAN_TEXTS.dm_apply_button}",
                    callback_data="apply_for_guild",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"📨 {PERSIAN_TEXTS.dm_status_button}",
                    callback_data="application_status",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"❌ {PERSIAN_TEXTS.dm_withdraw_button}",
                    callback_data="application_withdraw",
                )
            ],
        ]
    )


def application_review_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    PERSIAN_TEXTS.dm_application_action_buttons["approve"],
                    callback_data=f"application:{user_id}:approve",
                ),
                InlineKeyboardButton(
                    PERSIAN_TEXTS.dm_application_action_buttons["deny"],
                    callback_data=f"application:{user_id}:deny",
                ),
            ],
            [
                InlineKeyboardButton(
                    PERSIAN_TEXTS.dm_application_action_buttons["skip"],
                    callback_data="application:skip",
                )
            ],
        ]
    )

