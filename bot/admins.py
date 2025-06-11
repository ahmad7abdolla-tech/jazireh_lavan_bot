from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext
from bot.database import get_locations_db, add_location_db, update_location_db, delete_location_db
import logging

# تنظیمات لاگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

ADMIN_IDS = [6251969541]  # احمد

def admin_required(func):
    """دکوراتور برای بررسی دسترسی ادمین"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id not in ADMIN_IDS:
            await update.message.reply_text("⛔ دسترسی محدود به ادمین‌ها")
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
    # سایر عملیات‌ها...

async def add_location_start(update: Update, context: CallbackContext):
    """شروع فرآیند افزودن لوکیشن جدید"""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📝 لطفاً نام لوکیشن جدید را وارد کنید:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ انصراف", callback_data="admin_cancel")]])
    )
    context.user_data['admin_action'] = 'adding_location'
    context.user_data['step'] = 'name'

async def process_location_data(update: Update, context: CallbackContext):
    """پردازش مراحل مختلف افزودن لوکیشن"""
    user_data = context.user_data
    text = update.message.text
    
    if user_data['step'] == 'name':
        user_data['new_location'] = {'name': text}
        await update.message.reply_text("📌 توضیح کوتاه وارد کنید:")
        user_data['step'] = 'short_desc'
    
    elif user_data['step'] == 'short_desc':
        user_data['new_location']['short_desc'] = text
        await update.message.reply_text("📝 توضیح کامل وارد کنید:")
        user_data['step'] = 'long_desc'
    
    # ادامه مراحل...

@admin_required
async def show_edit_list(update: Update, context: CallbackContext):
    """نمایش لیست لوکیشن‌ها برای ویرایش"""
    locations = get_locations_db()
    
    keyboard = [
        [InlineKeyboardButton(
            f"{loc['name']} (🆔{loc['id']})", 
            callback_data=f"admin_edit_{loc['id']}"
        )]
        for loc in locations
    ]
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")])
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📝 لیست لوکیشن‌ها برای ویرایش:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# سایر توابع مدیریتی...

def register_admin_handlers(app):
    """ثبت هندلرهای ادمین"""
    app.add_handler(MessageHandler(
        filters.TEXT & filters.ChatType.PRIVATE & filters.User(ADMIN_IDS),
        process_location_data
    ))
    app.add_handler(CallbackQueryHandler(handle_admin_actions, pattern="^admin_"))
