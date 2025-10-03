from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class TextPack:
    dm_welcome: str
    dm_apply_button: str
    dm_open_webapp_button: str
    dm_admin_panel_button: str
    dm_status_button: str
    dm_withdraw_button: str
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
    dm_application_note_prompts: Dict[str, str]
    dm_application_note_confirmations: Dict[str, str]
    dm_application_note_skip_hint: str
    dm_application_note_skip_keyword: str
    dm_application_note_label: str
    dm_application_note_no_active: str
    dm_status_none: str
    dm_status_pending: str
    dm_status_approved: str
    dm_status_denied: str
    dm_status_withdrawn: str
    dm_status_unknown: str
    dm_status_template: str
    dm_status_template_with_note: str
    dm_status_last_updated_label: str
    dm_withdraw_success: str
    dm_withdraw_not_found: str
    dm_admin_added: str
    dm_admin_removed: str
    dm_not_owner: str
    dm_already_admin: str
    dm_not_admin: str
    dm_no_admins: str
    dm_cancelled: str
    dm_admin_enter_user_id: str
    dm_admin_invalid_user_id: str
    group_xp_updated: str
    group_xp_leaderboard_title: str
    group_cup_added: str
    group_cup_leaderboard_title: str
    group_no_data: str
    group_add_cup_usage: str
    group_add_cup_invalid_format: str
    error_generic: str
    glass_panel_caption: str
    admin_list_header: str
    dm_rate_limited: str
    dm_language_button: str
    dm_language_menu_title: str
    dm_language_close_button: str
    dm_language_updated: str
    group_refresh_button: str
    dm_admin_panel_intro: str


PERSIAN_TEXTS = TextPack(
    dm_welcome=(
        "<b>🪟 به پنل شیشه‌ای فلیزکس خوش آمدید!</b>\n\n"
        "برای پیوستن به گیلد، روی دکمه زیر کلیک کنید."
    ),
    dm_apply_button="درخواست عضویت در گیلد",
    dm_open_webapp_button="ورود به پنل وب",
    dm_admin_panel_button="ورود به پنل ادمین",
    dm_status_button="مشاهده وضعیت",
    dm_withdraw_button="لغو درخواست",
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
    dm_application_note_prompts={
        "approve": "✅ شما در حال تأیید {full_name} ({user_id}) هستید. لطفاً دلیل یا پیامی برای او ارسال کنید.",
        "deny": "❌ شما در حال رد {full_name} ({user_id}) هستید. لطفاً دلیل یا توضیحی برای او ارسال کنید.",
    },
    dm_application_note_confirmations={
        "approve": "✅ درخواست کاربر تأیید و پیام ارسال شد.",
        "deny": "❌ درخواست کاربر رد و پیام ارسال شد.",
    },
    dm_application_note_skip_hint="برای ادامه بدون توضیح، عبارت SKIP را ارسال کنید.",
    dm_application_note_skip_keyword="skip",
    dm_application_note_label="یادداشت",
    dm_application_note_no_active="ℹ️ موردی برای ثبت یادداشت وجود ندارد.",
    dm_status_none="ℹ️ هنوز درخواستی ثبت نکرده‌اید.",
    dm_status_pending="در حال بررسی",
    dm_status_approved="تأیید شده",
    dm_status_denied="رد شده",
    dm_status_withdrawn="لغو شده توسط شما",
    dm_status_unknown="نامشخص ({status})",
    dm_status_template=(
        "<b>وضعیت درخواست شما:</b> {status}\n"
        "<i>{last_updated_label}: {updated_at}</i>"
    ),
    dm_status_template_with_note=(
        "<b>وضعیت درخواست شما:</b> {status}\n"
        "<i>{last_updated_label}: {updated_at}</i>\n"
        "📝 {note}"
    ),
    dm_status_last_updated_label="آخرین به‌روزرسانی",
    dm_withdraw_success="♻️ درخواست شما با موفقیت لغو شد.",
    dm_withdraw_not_found="درخواستی در حال بررسی برای لغو یافت نشد.",
    dm_admin_added="✅ کاربر {user_id} به عنوان ادمین ثبت شد.",
    dm_admin_removed="♻️ کاربر {user_id} از لیست ادمین‌ها حذف شد.",
    dm_not_owner="⛔️ فقط مالک ربات می‌تواند این دستور را اجرا کند.",
    dm_already_admin="ℹ️ کاربر {user_id} از قبل ادمین است.",
    dm_not_admin="ℹ️ کاربر {user_id} در میان ادمین‌ها نیست.",
    dm_no_admins="هیچ ادمینی ثبت نشده است.",
    dm_cancelled="فرآیند درخواست لغو شد.",
    dm_admin_enter_user_id="لطفاً شناسه کاربر را وارد کنید.",
    dm_admin_invalid_user_id="شناسه باید عددی باشد.",
    group_xp_updated="✨ {full_name} {xp} امتیاز تجربه دارد!",
    group_xp_leaderboard_title="🏆 جدول تجربه اعضای فعال",
    group_cup_added="🏆 جام جدید با عنوان «{title}» ثبت شد.",
    group_cup_leaderboard_title="🥇 جدول جام‌های گیلد",
    group_no_data="هنوز داده‌ای ثبت نشده است.",
    group_add_cup_usage="استفاده: /add_cup عنوان | توضیح | قهرمان,نایب‌قهرمان,سوم",
    group_add_cup_invalid_format="ساختار ورودی صحیح نیست. از جداکننده | استفاده کنید.",
    error_generic="⚠️ خطایی رخ داد. لطفاً مجدداً تلاش کنید.",
    glass_panel_caption=(
        "<i>طراحی شیشه‌ای با پس‌زمینه‌ی محو و دکمه‌های درخشان برای تجربه‌ای مدرن.</i>"
    ),
    admin_list_header="👮‍♂️ ادمین‌های فعال:\n{admins}",
    dm_rate_limited="⏳ درخواست‌های شما موقتاً محدود شده است. لطفاً چند لحظه بعد دوباره تلاش کنید.",
    dm_language_button="تغییر زبان",
    dm_language_menu_title="یک زبان را انتخاب کنید:",
    dm_language_close_button="بازگشت",
    dm_language_updated="✅ زبان ربات به‌روزرسانی شد.",
    group_refresh_button="🔄 تازه‌سازی",
    dm_admin_panel_intro=(
        "<b>🛡️ پنل مدیریت فلیزکس</b>\n"
        "آخرین درخواست‌های در انتظار بررسی در زیر نمایش داده می‌شوند."
    ),
)


ENGLISH_TEXTS = TextPack(
    dm_welcome=(
        "<b>🪟 Welcome to the Flyzex glass panel!</b>\n\n"
        "Tap the button below to apply for the guild."
    ),
    dm_apply_button="Apply to the guild",
    dm_open_webapp_button="Open web panel",
    dm_admin_panel_button="Open admin panel",
    dm_status_button="Check status",
    dm_withdraw_button="Withdraw request",
    dm_application_started=(
        "📝 Please tell us why you would like to join the guild.\n"
        "Send /cancel to stop."
    ),
    dm_application_question="Please send your response:",
    dm_application_received=(
        "✅ Your application has been submitted! We will notify you after review."
    ),
    dm_application_duplicate=(
        "ℹ️ Your application is already on file and is being reviewed."
    ),
    dm_admin_only="⛔️ This section is for admins only.",
    dm_no_pending="There are no applications to review.",
    dm_application_item=(
        "<b>User:</b> {full_name} ({user_id})\n"
        "<b>Answer:</b> {answer}\n"
        "<b>Submitted:</b> {created_at}"
    ),
    dm_application_action_buttons={
        "approve": "✅ Approve",
        "deny": "❌ Reject",
        "skip": "⏭ Skip",
    },
    dm_application_approved_user="🎉 Your application has been approved! Welcome aboard.",
    dm_application_denied_user="❗️ Unfortunately your application was not approved.",
    dm_application_approved_admin="✅ The application was approved.",
    dm_application_denied_admin="❌ The application was rejected.",
    dm_application_note_prompts={
        "approve": "✅ You chose to approve {full_name} ({user_id}). Please send a note for the applicant.",
        "deny": "❌ You chose to deny {full_name} ({user_id}). Please share a note for the applicant.",
    },
    dm_application_note_confirmations={
        "approve": "✅ The application was approved and the applicant has been notified.",
        "deny": "❌ The application was rejected and the applicant has been notified.",
    },
    dm_application_note_skip_hint="Type SKIP to continue without adding a note.",
    dm_application_note_skip_keyword="skip",
    dm_application_note_label="Note",
    dm_application_note_no_active="ℹ️ There is no application awaiting a note.",
    dm_status_none="ℹ️ You have not submitted an application yet.",
    dm_status_pending="In review",
    dm_status_approved="Approved",
    dm_status_denied="Rejected",
    dm_status_withdrawn="Withdrawn by you",
    dm_status_unknown="Unknown ({status})",
    dm_status_template=(
        "<b>Your application status:</b> {status}\n"
        "<i>{last_updated_label}: {updated_at}</i>"
    ),
    dm_status_template_with_note=(
        "<b>Your application status:</b> {status}\n"
        "<i>{last_updated_label}: {updated_at}</i>\n"
        "📝 {note}"
    ),
    dm_status_last_updated_label="Last update",
    dm_withdraw_success="♻️ Your application has been withdrawn.",
    dm_withdraw_not_found="No pending application was found to withdraw.",
    dm_admin_added="✅ User {user_id} is now an admin.",
    dm_admin_removed="♻️ User {user_id} has been removed from the admins.",
    dm_not_owner="⛔️ Only the bot owner can run this command.",
    dm_already_admin="ℹ️ User {user_id} is already an admin.",
    dm_not_admin="ℹ️ User {user_id} is not an admin.",
    dm_no_admins="No admins have been registered yet.",
    dm_cancelled="The application process was cancelled.",
    dm_admin_enter_user_id="Please provide a user ID.",
    dm_admin_invalid_user_id="The user ID must be numeric.",
    group_xp_updated="✨ {full_name} now has {xp} XP!",
    group_xp_leaderboard_title="🏆 Active members leaderboard",
    group_cup_added="🏆 A new cup titled \"{title}\" has been added.",
    group_cup_leaderboard_title="🥇 Guild cups leaderboard",
    group_no_data="No data has been recorded yet.",
    group_add_cup_usage="Usage: /add_cup Title | Description | Champion,Runner-up,Third",
    group_add_cup_invalid_format="The input format is invalid. Please use the | separator.",
    error_generic="⚠️ Something went wrong. Please try again.",
    glass_panel_caption=(
        "<i>Glassmorphic styling with soft blur for a modern experience.</i>"
    ),
    admin_list_header="👮‍♂️ Active admins:\n{admins}",
    dm_rate_limited="⏳ You are sending requests too quickly. Please try again shortly.",
    dm_language_button="Change language",
    dm_language_menu_title="Choose a language:",
    dm_language_close_button="Back",
    dm_language_updated="✅ Language updated successfully.",
    group_refresh_button="🔄 Refresh",
    dm_admin_panel_intro=(
        "<b>🛡️ Flyzex admin panel</b>\n"
        "Pending applications appear below for quick review."
    ),
)


DEFAULT_LANGUAGE_CODE = "fa"

_TEXT_PACKS: Dict[str, TextPack] = {
    "fa": PERSIAN_TEXTS,
    "en": ENGLISH_TEXTS,
}


def normalize_language_code(language_code: str | None) -> str | None:
    if not language_code:
        return None
    return language_code.split("-")[0].lower()


def get_text_pack(language_code: str | None) -> TextPack:
    normalised = normalize_language_code(language_code)
    if normalised and normalised in _TEXT_PACKS:
        return _TEXT_PACKS[normalised]
    return _TEXT_PACKS[DEFAULT_LANGUAGE_CODE]

