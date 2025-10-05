from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from ..localization import PERSIAN_TEXTS, TextPack


LANGUAGE_CODES: tuple[str, ...] = ("fa", "en")
DEFAULT_LANGUAGE_LABELS: dict[str, str] = {"fa": "فارسی", "en": "English"}


def glass_dm_welcome_keyboard(
    texts: TextPack | None = None,
    webapp_url: str | None = None,
    *,
    is_admin: bool = False,
) -> InlineKeyboardMarkup:
    text_pack = texts or PERSIAN_TEXTS
    rows = [
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
        [
            InlineKeyboardButton(
                text=f"🌐 {text_pack.dm_language_button}",
                callback_data="language_menu",
            )
        ],
    ]
    if webapp_url:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"🧊 {text_pack.dm_open_webapp_button}",
                    web_app=WebAppInfo(url=webapp_url),
                )
            ]
        )
    if is_admin:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"🛡️ {text_pack.dm_admin_panel_button}",
                    callback_data="admin_panel",
                )
            ]
        )
    return InlineKeyboardMarkup(rows)


def admin_panel_keyboard(
    texts: TextPack | None = None,
    webapp_url: str | None = None,
) -> InlineKeyboardMarkup:
    text_pack = texts or PERSIAN_TEXTS
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text=f"📬 {text_pack.dm_admin_panel_view_applications_button}",
                callback_data="admin_panel:view_applications",
            )
        ],
        [
            InlineKeyboardButton(
                text=f"✅ {text_pack.dm_admin_panel_view_members_button}",
                callback_data="admin_panel:view_members",
            )
        ],
        [
            InlineKeyboardButton(
                text=f"➕ {text_pack.dm_admin_panel_add_admin_button}",
                callback_data="admin_panel:add_admin",
            )
        ],
        [
            InlineKeyboardButton(
                text=f"📊 {text_pack.dm_admin_panel_insights_button}",
                callback_data="admin_panel:insights",
            )
        ],
    ]
    if webapp_url:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"🌐 {text_pack.dm_admin_panel_more_tools_button}",
                    web_app=WebAppInfo(url=webapp_url),
                )
            ]
        )
    else:
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"✨ {text_pack.dm_admin_panel_more_tools_button}",
                    callback_data="admin_panel:more_tools",
                )
            ]
        )
    rows.append(
        [
            InlineKeyboardButton(
                text=f"⬅️ {text_pack.dm_admin_panel_back_button}",
                callback_data="admin_panel:back",
            )
        ]
    )
    return InlineKeyboardMarkup(rows)


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


def language_options_keyboard(active: str | None, texts: TextPack | None = None) -> InlineKeyboardMarkup:
    text_pack = texts or PERSIAN_TEXTS
    rows: list[list[InlineKeyboardButton]] = []
    for code in LANGUAGE_CODES:
        language_names = getattr(text_pack, "language_names", {})
        label = language_names.get(code, DEFAULT_LANGUAGE_LABELS.get(code, code))
        prefix = "✅ " if code == active else ""
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{prefix}{label}",
                    callback_data=f"set_language:{code}",
                )
            ]
        )
    rows.append(
        [
            InlineKeyboardButton(
                text=text_pack.dm_language_close_button,
                callback_data="close_language_menu",
            )
        ]
    )
    return InlineKeyboardMarkup(rows)


def leaderboard_refresh_keyboard(board_type: str, chat_id: int, texts: TextPack | None = None) -> InlineKeyboardMarkup:
    text_pack = texts or PERSIAN_TEXTS
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=text_pack.group_refresh_button,
                    callback_data=f"leaderboard:{board_type}:{chat_id}",
                )
            ]
        ]
    )
