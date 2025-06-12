from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

# لیست شناسه‌های ادمین‌ها
ADMINS = [6251969541, 367118717]  # احمد

# تابع بررسی ادمین بودن
def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

# پنل مدیریت برای ادمین
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
    await update.message.reply_text("🛠️ پنل مدیریت:", reply_markup=reply_markup)

# هندل کردن دکمه‌های داخل پنل ادمین
async def handle_admin_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if not is_admin(user_id):
        await query.answer("❌ دسترسی ندارید.", show_alert=True)
        return

    data = query.data

    if data == "admin_add_location":
        await query.answer()
        context.user_data["admin_state"] = "add_name"
        context.user_data["new_location"] = {}
        await query.message.reply_text("🟢 لطفاً نام لوکیشن جدید را ارسال کنید.")

    elif data == "admin_edit_location":
        await query.answer()
        context.user_data["admin_state"] = "edit_select"
        await query.message.reply_text("✏️ لطفاً نام لوکیشنی که می‌خواهید ویرایش کنید را ارسال نمایید.")

    elif data == "admin_delete_location":
        await query.answer()
        context.user_data["admin_state"] = "delete_select"
        await query.message.reply_text("❌ لطفاً نام لوکیشنی که می‌خواهید حذف کنید را ارسال نمایید.")

    else:
        await query.answer()

# ثبت هندلرهای لازم (در صورت نیاز در آینده)
def register_admin_handlers(app):
    pass
