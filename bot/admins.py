from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackContext, MessageHandler, filters, CallbackQueryHandler
from bot.database import add_location_db, update_location_db, delete_location_db, get_locations_db
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

ADMIN_IDS = [6251969541]  # شناسه ادمین‌ها

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
    query = update.callback_query
    await query.answer()
    action = query.data

    if action == "admin_add_loc":
        await add_location_start(update, context)
    elif action == "admin_edit_list":
        await show_edit_list(update, context)
    elif action.startswith("admin_edit_"):
        loc_id = action.split("_")[-1]
        await edit_location_start(update, context, loc_id)
    elif action == "admin_cancel":
        await cancel_admin_action(update, context)
    elif action == "admin_back":
        await admin_panel(update, context)
    elif action == "admin_exit":
        await update.callback_query.message.edit_text("✅ از حالت ادمین خارج شدید.")
    # سایر عملیات‌ها...

async def add_location_start(update: Update, context: CallbackContext):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📝 لطفاً نام لوکیشن جدید را وارد کنید:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ انصراف", callback_data="admin_cancel")]])
    )
    context.user_data['admin_action'] = 'adding_location'
    context.user_data['step'] = 'name'

async def process_location_data(update: Update, context: CallbackContext):
    user_data = context.user_data
    text = update.message.text

    if user_data.get('admin_action') == 'adding_location':
        step = user_data.get('step')
        if step == 'name':
            user_data['new_location'] = {'name': text}
            await update.message.reply_text("📷 لطفاً تصویر لوکیشن را ارسال کنید:")
            user_data['step'] = 'image'
        elif step == 'image':
            await update.message.reply_text("⛔ لطفاً فقط یک عکس ارسال کنید.")
        elif step == 'desc':
            user_data['new_location']['description'] = text
            # ذخیره لوکیشن در دیتابیس
            loc_data = user_data['new_location']
            loc_data['images'] = user_data.get('images', [])
            await add_location_db(loc_data)
            await update.message.reply_text("✅ لوکیشن جدید با موفقیت اضافه شد.")
            user_data.clear()
    else:
        await update.message.reply_text("⛔ دستور نامشخص یا خارج از فرآیند مدیریت است.")

async def process_photo(update: Update, context: CallbackContext):
    user_data = context.user_data
    if user_data.get('admin_action') == 'adding_location' and user_data.get('step') == 'image':
        photo = update.message.photo[-1]  # با کیفیت‌ترین عکس
        file_id = photo.file_id
        user_data.setdefault('images', []).append(file_id)
        await update.message.reply_text("📌 تصویر دریافت شد. حالا لطفاً توضیحات مربوط به تصویر را وارد کنید:")
        user_data['step'] = 'desc'
    else:
        await update.message.reply_text("⛔ لطفاً ابتدا نام لوکیشن را وارد کنید.")

@admin_required
async def show_edit_list(update: Update, context: CallbackContext):
    locations = await get_locations_db()
    keyboard = [
        [InlineKeyboardButton(f"{loc['name']} (🆔{loc['id']})", callback_data=f"admin_edit_{loc['id']}")]
        for loc in locations
    ]
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="admin_back")])
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📝 لیست لوکیشن‌ها برای ویرایش:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def edit_location_start(update: Update, context: CallbackContext, loc_id: str):
    # شروع فرآیند ویرایش لوکیشن (نمونه اولیه)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✏️ در حال ویرایش لوکیشن با شناسه {loc_id}...\n(قابلیت در حال توسعه است)"
    )

async def cancel_admin_action(update: Update, context: CallbackContext):
    context.user_data.clear()
    await update.callback_query.message.edit_text("❌ عملیات لغو شد.")

def register_admin_handlers(app):
    from telegram.ext import MessageHandler, filters, CallbackQueryHandler

    app.add_handler(MessageHandler(
        filters.TEXT & filters.ChatType.PRIVATE & filters.User(ADMIN_IDS),
        process_location_data
    ))
    app.add_handler(MessageHandler(
        filters.PHOTO & filters.ChatType.PRIVATE & filters.User(ADMIN_IDS),
        process_photo
    ))
    app.add_handler(CallbackQueryHandler(handle_admin_actions, pattern="^admin_"))
