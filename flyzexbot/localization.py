"""Localised Persian texts for FlyzexBot."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class TextPack:
    dm_welcome: str
    dm_apply_button: str
    dm_application_started: str
    dm_application_question: str
    dm_application_received: str
    dm_application_duplicate: str
    dm_admin_only: str
    dm_no_pending: str
    dm_application_item: str
    dm_application_action_buttons: Dict[str, str]
    dm_application_approved_user: str
    dm_application_denied_user: str
    dm_application_approved_admin: str
    dm_application_denied_admin: str
    dm_admin_added: str
    dm_admin_removed: str
    dm_not_owner: str
    dm_already_admin: str
    dm_not_admin: str
    dm_no_admins: str
    group_xp_updated: str
    group_xp_leaderboard_title: str
    group_cup_added: str
    group_cup_leaderboard_title: str
    group_no_data: str
    error_generic: str
    glass_panel_caption: str
    admin_list_header: str


PERSIAN_TEXTS = TextPack(
    dm_welcome=(
        "<b>🪟 به پنل شیشه‌ای فلیزکس خوش آمدید!</b>\n\n"
        "برای پیوستن به گیلد، روی دکمه زیر کلیک کنید."
    ),
    dm_apply_button="درخواست عضویت در گیلد",
    dm_application_started=(
        "📝 لطفاً دلیل علاقه‌مندی خود برای پیوستن به گیلد را بنویسید.\n"
        "برای لغو، دستور /cancel را ارسال کنید."
    ),
    dm_application_question="لطفاً توضیح خود را ارسال کنید:",
    dm_application_received=(
        "✅ درخواست شما ثبت شد! پس از بررسی نتیجه اطلاع‌رسانی خواهد شد."
    ),
    dm_application_duplicate=(
        "ℹ️ درخواست شما قبلاً ثبت شده و در حال بررسی است."
    ),
    dm_admin_only="⛔️ این بخش فقط برای ادمین‌هاست.",
    dm_no_pending="درخواستی برای بررسی وجود ندارد.",
    dm_application_item=(
        "<b>کاربر:</b> {full_name} ({user_id})\n"
        "<b>پاسخ:</b> {answer}\n"
        "<b>زمان:</b> {created_at}"
    ),
    dm_application_action_buttons={
        "approve": "✅ تأیید",
        "deny": "❌ رد",
        "skip": "⏭ بعدی",
    },
    dm_application_approved_user="🎉 درخواست شما پذیرفته شد! به گیلد خوش آمدید.",
    dm_application_denied_user="❗️ متأسفیم، درخواست شما در حال حاضر پذیرفته نشد.",
    dm_application_approved_admin="✅ درخواست کاربر تأیید شد.",
    dm_application_denied_admin="❌ درخواست کاربر رد شد.",
    dm_admin_added="✅ کاربر {user_id} به عنوان ادمین ثبت شد.",
    dm_admin_removed="♻️ کاربر {user_id} از لیست ادمین‌ها حذف شد.",
    dm_not_owner="⛔️ فقط مالک ربات می‌تواند این دستور را اجرا کند.",
    dm_already_admin="ℹ️ کاربر {user_id} از قبل ادمین است.",
    dm_not_admin="ℹ️ کاربر {user_id} در میان ادمین‌ها نیست.",
    dm_no_admins="هیچ ادمینی ثبت نشده است.",
    group_xp_updated="✨ {full_name} {xp} امتیاز تجربه دارد!",
    group_xp_leaderboard_title="🏆 جدول تجربه اعضای فعال",
    group_cup_added="🏆 جام جدید با عنوان «{title}» ثبت شد.",
    group_cup_leaderboard_title="🥇 جدول جام‌های گیلد",
    group_no_data="هنوز داده‌ای ثبت نشده است.",
    error_generic="⚠️ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
    glass_panel_caption=(
        "<i>طراحی شیشه‌ای با پس‌زمینه‌ی محو و دکمه‌های درخشان برای تجربه‌ای مدرن.</i>"
    ),
    admin_list_header="👮‍♂️ ادمین‌های فعال:\n{admins}",
)

