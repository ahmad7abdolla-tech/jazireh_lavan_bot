from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# لیست شناسه‌های ادمین‌ها
ADMINS = [6251969541]  # به‌جای این‌ها شناسه‌های واقعی ادمین‌ها را قرار بده

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ شما دسترسی ادمین ندارید.")
        return
    
    keyboard = [
        [InlineKeyboardButton("➕ افزودن لوکیشن", callback_data="admin_add_location")],
        [InlineKeyboardButton("✏️ ویرایش لوکیشن‌ها", callback_data="admin_edit_location")],
        [InlineKeyboardButton("❌ حذف لوکیشن‌ها", callback_data="admin_delete_location")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("پنل مدیریت:", reply_markup=reply_markup)

async def handle_admin_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if not is_admin(user_id):
        await query.answer("❌ دسترسی ندارید.", show_alert=True)
        return
    
    data = query.data

    if data == "admin_add_location":
        await query.answer()
        await query.message.reply_text("🟢 لطفاً نام لوکیشن جدید را ارسال کنید.")
        # اینجا باید منطق مرحله به مرحله افزودن لوکیشن اضافه شود
    
    elif data == "admin_edit_location":
        await query.answer("در حال حاضر این بخش در دست توسعه است.", show_alert=True)
    
    elif data == "admin_delete_location":
        await query.answer("در حال حاضر این بخش در دست توسعه است.", show_alert=True)
    else:
        await query.answer()

def register_admin_handlers(app):
    # اگر لازم شد هندلرهای اضافی اینجا اضافه شود
    pass
