from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

# لیست آیدی عددی ادمین‌ها
SUPER_ADMINS = [367118717]  # آیدی ادمین اصلی (توسعه‌دهنده)
CONTENT_ADMINS = [6251969541]  # آیدی ادمین‌های محتوا

# بررسی اینکه آیا کاربر ادمین هست
def is_admin(user_id: int) -> bool:
    return user_id in SUPER_ADMINS or user_id in CONTENT_ADMINS

def is_super_admin(user_id: int) -> bool:
    return user_id in SUPER_ADMINS

def is_content_admin(user_id: int) -> bool:
    return user_id in CONTENT_ADMINS

# نمایش پنل مدیریت
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("⛔ شما دسترسی به پنل مدیریت ندارید.")
        return

    buttons = []

    # دکمه‌های مشترک بین ادمین‌ها
    if is_content_admin(user_id) or is_super_admin(user_id):
        buttons.extend([
            [InlineKeyboardButton("➕ افزودن لوکیشن", callback_data="admin_add_location")],
            [InlineKeyboardButton("✏️ ویرایش لوکیشن", callback_data="admin_edit_location")],
            [InlineKeyboardButton("❌ حذف لوکیشن", callback_data="admin_delete_location")],
        ])

    # دکمه‌های مخصوص سوپر ادمین (در صورت نیاز)
    if is_super_admin(user_id):
        buttons.append([
            InlineKeyboardButton("⚙️ تنظیمات بیشتر (به‌زودی)", callback_data="admin_settings")
        ])

    markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("🛠️ به پنل مدیریت خوش آمدید:", reply_markup=markup)

# هندلرهای مربوط به ادمین‌ها (در آینده گسترش‌پذیر)
async def handle_admin_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # این تابع فقط به خاطر الگو در CallbackHandler استفاده شده
    pass

# ثبت هندلر ادمین‌ها
def register_admin_handlers(app):
    # (در صورت نیاز، CallbackHandler اختصاصی اینجا اضافه شود)
    pass
