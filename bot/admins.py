from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext, MessageHandler, CallbackQueryHandler, filters
from bot.database import add_location_db, update_location_db, delete_location_db, get_locations_db
import logging

# تنظیمات لاگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

ADMIN_IDS = [6251969541]  # شناسه ادمین‌ها (مثلاً احمد)

def admin_required(func):
    """دکوراتور بررسی دسترسی ادمین"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            if update.message:
                await update.message.reply_text("⛔ دسترسی محدود به ادمین‌ها")
            elif update.callback_query:
                await update.callback_query.answer("⛔ دسترسی محدود به ادمین‌ها", show_alert=True)
            return
        return await func(update, context)
    return wrapper

@admin_required
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پنل مدیریت اصلی"""
    keyboard = [
        [InlineKeyboardButton("➕ افزودن لوکیشن جدید", callback_data="admin_add_loc")],
        [InlineKeyboardButton("✏️ ویرایش لوکیشن‌ها", callback_data="admin_edit_list")],
        [InlineKeyboardButton("📊 آمار و گزارشات", callback_data="admin_stats")],
        [InlineKeyboardButton("🔙 خروج از حالت ادمین", callback_data="admin_exit")]
    ]
    await update.message.reply_text(
        "🛠️ **پنل مدیریت لوکیشن‌ها**\n\nلطفاً یک گزینه را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

@admin_required
async def handle_admin_actions(update: Update, context: CallbackContext):
    """مدیریت کلیک‌های اینلاین کیبورد"""
    query = update.callback_query
    await query.answer()
    action = query.data

    if action == "admin_add_loc":
        await add_location_start(update, context)
    elif action == "admin_edit_list":
        await show_edit_list(update, context)
    elif action.startswith("admin_edit_"):
        location_id = action.split("_")[-1]
        await edit_location_start(update, context, location_id)
    elif action == "admin_cancel":
        await cancel_admin_action(update, context)
    elif action == "admin_back":
        await admin_panel(update, context)
    elif action == "admin_exit":
        await exit_admin_mode(update, context)
    # سایر عملیات مدیریتی...

async def add_location_start(update: Update, context: CallbackContext):
    """شروع افزودن لوکیشن جدید"""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📝 لطفاً نام لوکیشن جدید را وارد کنید:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ انصراف", callback_data="admin_cancel")]])
    )
    context.user_data['admin_action'] = 'adding_location'
    context.user_data['step'] = 'name'
    context.user_data['new_location'] = {}

async def process_location_data(update: Update, context: CallbackContext):
    """پردازش مراحل افزودن لوکیشن (نام، عکس، توضیحا
