from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


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
    dm_application_role_prompt: str
    dm_application_role_options: Dict[str, List[str]]
    dm_application_followup_prompts: Dict[str, str]
    dm_application_goals_prompt: str
    dm_application_availability_prompt: str
    dm_application_summary_title: str
    dm_application_summary_item: str
    dm_application_invalid_choice: str
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
    dm_admin_panel_view_applications_button: str
    dm_admin_panel_view_members_button: str
    dm_admin_panel_add_admin_button: str
    dm_admin_panel_more_tools_button: str
    dm_admin_panel_insights_button: str
    dm_admin_panel_back_button: str
    dm_admin_panel_members_header: str
    dm_admin_panel_members_empty: str
    dm_admin_panel_add_admin_prompt: str
    dm_admin_panel_more_tools_text: str
    dm_admin_panel_more_tools_no_webapp: str
    dm_admin_panel_insights_title: str
    dm_admin_panel_insights_counts: str
    dm_admin_panel_insights_languages: str
    dm_admin_panel_insights_languages_empty: str
    dm_admin_panel_insights_recent: str
    dm_admin_panel_insights_recent_empty: str
    language_names: Dict[str, str]


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
        "📝 آماده‌اید برای پیوستن به گیلد؟ در چند سوال کوتاه با ما بیشتر آشنا شوید!\n"
        "برای لغو، دستور /cancel را ارسال کنید."
    ),
    dm_application_question="۱️⃣ نقش مورد علاقه‌تان در گیلد چیست؟",
    dm_application_received=(
        "✅ درخواست شما ثبت شد! پس از بررسی نتیجه اطلاع‌رسانی خواهد شد.\n"
        "برای پیگیری می‌توانید از دکمه «مشاهده وضعیت» استفاده کنید."
    ),
    dm_application_duplicate=(
        "ℹ️ درخواست شما قبلاً ثبت شده و در حال بررسی است."
    ),
    dm_application_role_prompt="۱️⃣ نقش مورد علاقه‌تان در گیلد چیست؟ (تاجر، مبارز، کاوشگر، پشتیبان)",
    dm_application_role_options={
        "trader": ["تاجر", "trader"],
        "fighter": ["مبارز", "fighter"],
        "explorer": ["کاوشگر", "explorer"],
        "support": ["پشتیبان", "support"],
    },
    dm_application_followup_prompts={
        "trader": "۲️⃣ چه تجربه‌ای در معامله‌گری یا مدیریت منابع دارید؟",
        "fighter": "۲️⃣ سبک مبارزه یا استراتژی مورد علاقه‌تان چیست؟",
        "explorer": "۲️⃣ چه نوع ماجراجویی یا اکتشافی را بیشتر دوست دارید؟",
        "support": "۲️⃣ چگونه از هم‌تیمی‌های خود پشتیبانی می‌کنید؟",
    },
    dm_application_goals_prompt="۳️⃣ با پیوستن به گیلد می‌خواهید به چه دستاوردی برسید؟",
    dm_application_availability_prompt="۴️⃣ معمولاً چه زمان‌هایی آنلاین هستید یا می‌توانید مشارکت کنید؟",
    dm_application_summary_title="<b>📋 خلاصه پاسخ‌های شما</b>",
    dm_application_summary_item="• <b>{question}</b>\n  {answer}",
    dm_application_invalid_choice="لطفاً یکی از گزینه‌های معتبر را وارد کنید: {options}",
    dm_admin_only="⛔️ این بخش فقط برای ادمین‌هاست.",
    dm_no_pending="درخواستی برای بررسی وجود ندارد.",
    dm_application_item=(
        "<b>کاربر:</b> {full_name} ({user_id})\n"
        "<b>پاسخ‌ها:</b>\n{answers}\n"
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
    dm_application_note_skip_hint="برای ادامه بدون توضیح، عبارت «صرفنظر» را ارسال کنید.",
    dm_application_note_skip_keyword="صرفنظر",
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
        "برای ادامه یکی از گزینه‌های شیشه‌ای زیر را انتخاب کنید."
    ),
    dm_admin_panel_view_applications_button="مشاهده درخواست‌ها",
    dm_admin_panel_view_members_button="اعضای تایید‌شده",
    dm_admin_panel_add_admin_button="افزودن ادمین جدید",
    dm_admin_panel_more_tools_button="ابزارهای بیشتر",
    dm_admin_panel_insights_button="گزارش‌ها و تحلیل‌ها",
    dm_admin_panel_back_button="بازگشت به خانه",
    dm_admin_panel_members_header="✅ اعضای تایید‌شده ({count} نفر):\n{members}",
    dm_admin_panel_members_empty="هیچ عضوی تأیید نشده است.",
    dm_admin_panel_add_admin_prompt="شناسه عددی کاربر موردنظر را ارسال کنید.",
    dm_admin_panel_more_tools_text=(
        "✨ می‌توانید از نسخه وب برای مدیریت کامل‌تر استفاده کنید:\n"
        "<a href=\"{webapp_url}\">ورود به داشبورد</a>"
    ),
    dm_admin_panel_more_tools_no_webapp=(
        "ℹ️ هنوز وب‌اپ معرفی نشده است. در فایل پیکربندی مقدار webapp_url را تنظیم کنید."
    ),
    dm_admin_panel_insights_title="<b>📊 داشبورد مدیریتی</b>",
    dm_admin_panel_insights_counts=(
        "• در انتظار بررسی: {pending}\n"
        "• تأیید شده: {approved}\n"
        "• رد شده: {denied}\n"
        "• لغو شده: {withdrawn}\n"
        "• مجموع ثبت‌شده: {total}\n"
        "• میانگین طول پاسخ‌های در انتظار: {average_length:.0f} کاراکتر"
    ),
    dm_admin_panel_insights_languages="<b>🌐 زبان‌های پرکاربرد:</b>\n{languages}",
    dm_admin_panel_insights_languages_empty="هیچ زبان ترجیحی ثبت نشده است.",
    dm_admin_panel_insights_recent="<b>🕒 آخرین فعالیت‌ها:</b>\n{items}",
    dm_admin_panel_insights_recent_empty="سابقه‌ای برای نمایش وجود ندارد.",
    language_names={
        "fa": "فارسی",
        "en": "انگلیسی",
    },
)


ENGLISH_TEXTS = TextPack(
    dm_welcome=(
        "<b>🪟 Welcome to the Flyzex Glass Panel!</b>\n\n"
        "Tap the button below to begin your application to the guild."
    ),
    dm_apply_button="Apply to join the guild",
    dm_open_webapp_button="Open web panel",
    dm_admin_panel_button="Open admin panel",
    dm_status_button="Check status",
    dm_withdraw_button="Withdraw application",
    dm_application_started=(
        "📝 Ready to apply? Let's go through a few quick questions together!\n"
        "Send /cancel anytime to stop."
    ),
    dm_application_question="1️⃣ Which role fits you best in the guild?",
    dm_application_received=(
        "✅ Your application has been submitted! We will notify you after review.\n"
        "Use the ‘Check status’ button anytime for updates."
    ),
    dm_application_duplicate=(
        "ℹ️ Your application is already on file and is being reviewed."
    ),
    dm_application_role_prompt="1️⃣ Which role fits you best in the guild? (Trader, Fighter, Explorer, Support)",
    dm_application_role_options={
        "trader": ["trader", "merchant"],
        "fighter": ["fighter", "warrior"],
        "explorer": ["explorer", "scout"],
        "support": ["support", "healer"],
    },
    dm_application_followup_prompts={
        "trader": "2️⃣ What kind of trading or resource management experience do you have?",
        "fighter": "2️⃣ What combat style or strategy do you excel at?",
        "explorer": "2️⃣ Tell us about an adventure or discovery you're proud of.",
        "support": "2️⃣ How do you usually empower or assist your teammates?",
    },
    dm_application_goals_prompt="3️⃣ What do you hope to achieve by joining the guild?",
    dm_application_availability_prompt="4️⃣ When are you usually available to participate?",
    dm_application_summary_title="<b>📋 Summary of your answers</b>",
    dm_application_summary_item="• <b>{question}</b>\n  {answer}",
    dm_application_invalid_choice="Please choose one of the available options: {options}",
    dm_admin_only="⛔️ This section is for admins only.",
    dm_no_pending="There are no applications to review.",
    dm_application_item=(
        "<b>Applicant:</b> {full_name} ({user_id})\n"
        "<b>Answers:</b>\n{answers}\n"
        "<b>Submitted:</b> {created_at}"
    ),
    dm_application_action_buttons={
        "approve": "✅ Approve",
        "deny": "❌ Deny",
        "skip": "⏭ Skip",
    },
    dm_application_approved_user="🎉 Your application has been approved! Welcome aboard.",
    dm_application_denied_user="❗️ Unfortunately your application was not approved.",
    dm_application_approved_admin="✅ The application was approved.",
    dm_application_denied_admin="❌ The application was rejected.",
    dm_application_note_prompts={
        "approve": "✅ You are approving {full_name} ({user_id}). Please send a welcome note or reason.",
        "deny": "❌ You are denying {full_name} ({user_id}). Please send a brief reason.",
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
    dm_status_pending="Pending review",
    dm_status_approved="Approved",
    dm_status_denied="Denied",
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
    dm_status_last_updated_label="Last updated",
    dm_withdraw_success="♻️ Your application has been withdrawn.",
    dm_withdraw_not_found="No pending application was found to withdraw.",
    dm_admin_added="✅ User {user_id} is now an admin.",
    dm_admin_removed="♻️ User {user_id} was removed from admins.",
    dm_not_owner="⛔️ Only the bot owner can run this command.",
    dm_already_admin="ℹ️ User {user_id} is already an admin.",
    dm_not_admin="ℹ️ User {user_id} is not listed as an admin.",
    dm_no_admins="No admins have been added yet.",
    dm_cancelled="The application process was cancelled.",
    dm_admin_enter_user_id="Please provide the user ID.",
    dm_admin_invalid_user_id="The user ID must be numeric.",
    group_xp_updated="✨ {full_name} now has {xp} XP!",
    group_xp_leaderboard_title="🏆 Experience leaderboard",
    group_cup_added="🏆 A new cup named '{title}' has been recorded.",
    group_cup_leaderboard_title="🥇 Guild cups leaderboard",
    group_no_data="No records yet.",
    group_add_cup_usage="Usage: /add_cup title | description | gold,silver,bronze",
    group_add_cup_invalid_format="Invalid format. Separate items with |",
    error_generic="⚠️ Something went wrong. Please try again.",
    glass_panel_caption=(
        "<i>A modern glassmorphism-inspired interface with frosted cards and vibrant buttons.</i>"
    ),
    admin_list_header="👮‍♂️ Current admins:\n{admins}",
    dm_rate_limited="⏳ You're sending messages too quickly. Please wait a moment and try again.",
    dm_language_button="Change language",
    dm_language_menu_title="Choose a language:",
    dm_language_close_button="Back",
    dm_language_updated="✅ Language updated successfully.",
    group_refresh_button="🔄 Refresh",
    dm_admin_panel_intro=(
        "<b>🛡️ Flyzex Admin Panel</b>\n"
        "Select one of the glass buttons below to continue."
    ),
    dm_admin_panel_view_applications_button="View applications",
    dm_admin_panel_view_members_button="Approved members",
    dm_admin_panel_add_admin_button="Add a new admin",
    dm_admin_panel_more_tools_button="More tools",
    dm_admin_panel_insights_button="Analytics & reports",
    dm_admin_panel_back_button="Back to welcome",
    dm_admin_panel_members_header="✅ Approved members ({count}):\n{members}",
    dm_admin_panel_members_empty="No members have been approved yet.",
    dm_admin_panel_add_admin_prompt=(
        "Send the numeric user ID of the member you want to promote."
        "\nSend /cancel to abort."
    ),
    dm_admin_panel_more_tools_text=(
        "✨ Access the full dashboard through the web app:\n"
        "<a href=\"{webapp_url}\">Open dashboard</a>"
    ),
    dm_admin_panel_more_tools_no_webapp=(
        "ℹ️ Configure webapp_url in settings.yaml to enable the web dashboard."
    ),
    dm_admin_panel_insights_title="<b>📊 Admin dashboard</b>",
    dm_admin_panel_insights_counts=(
        "• Pending review: {pending}\n"
        "• Approved: {approved}\n"
        "• Denied: {denied}\n"
        "• Withdrawn: {withdrawn}\n"
        "• Total submissions: {total}\n"
        "• Avg. pending answer length: {average_length:.0f} characters"
    ),
    dm_admin_panel_insights_languages="<b>🌐 Preferred languages:</b>\n{languages}",
    dm_admin_panel_insights_languages_empty="No language preferences have been recorded yet.",
    dm_admin_panel_insights_recent="<b>🕒 Recent activity:</b>\n{items}",
    dm_admin_panel_insights_recent_empty="No recent activity to display.",
    language_names={
        "fa": "Persian",
        "en": "English",
    },
)


DEFAULT_LANGUAGE_CODE = "fa"

_TEXT_PACKS: Dict[str, TextPack] = {
    "fa": PERSIAN_TEXTS,
    "en": ENGLISH_TEXTS,
}

AVAILABLE_LANGUAGE_CODES = tuple(_TEXT_PACKS.keys())


def normalize_language_code(language_code: str | None) -> str | None:
    if not language_code:
        return None
    code = language_code.replace("_", "-").strip()
    if not code:
        return None
    primary = code.split("-", 1)[0].strip().lower()
    return primary or None


def get_text_pack(language_code: str | None) -> TextPack:
    normalised = normalize_language_code(language_code)
    if normalised and normalised in _TEXT_PACKS:
        return _TEXT_PACKS[normalised]
    return _TEXT_PACKS[DEFAULT_LANGUAGE_CODE]

