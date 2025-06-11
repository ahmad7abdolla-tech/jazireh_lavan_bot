import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters,
)
from bot.weather_today import handle_weather_today
from bot.locations import handle_locations, show_location_details
from bot.admins import admin_panel, handle_admin_actions, register_admin_handlers

BOT_TOKEN = os.environ.get("7586578372:AAEIkVr4Wq23NSkLuSPRl1yqboqd7_cW0ac")  # توی Render باید BOT_TOKEN تعریف بشه
WEBHOOK_URL = f"https://jazireh-lavan-bot.onrender.com/{BOT_TOKEN}"  # آدرس دامنه‌ی رباتت در Render

# کیبورد اصلی ربات
keyboard = [
    ["🌦 هوای لاوان الان چطوره؟"],
    ["📍لوکیشن‌های جزیره لاوان"],
    ["🏨معرفی اقامتگاه‌ها و امکانات رفاهی"],
    ["📰اخبار جزیره لاوان"],
    ["🛠️ پنل مدیریت (ادمین)"]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# شروع گفتگو
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 👋 \n حیاکم الله😉 به ربات جزیره لاوان خوش آمدی.\n\nیکی از دکمه‌ها رو انتخاب کن:",
        reply_markup=reply_markup
    )

# بررسی پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🌦 هوای لاوان الان چطوره؟":
        await update.message.reply_text("⏳ در حال دریافت اطلاعات هواشناسی...")
        response = handle_weather_today()
        await update.message.reply_text(response)

    elif text == "📍لوکیشن‌های جزیره لاوان":
        await handle_locations(update, context)

    elif text == "🏨معرفی اقامتگاه‌ها و امکانات رفاهی":
        await update.message.reply_text("در حال توسعه است ⏳")

    elif text == "📰اخبار جزیره لاوان":
        await update.message.reply_text("در حال توسعه است ⏳")

    elif text == "🛠️ پنل مدیریت (ادمین)":
        await admin_panel(update, context)

    else:
        await update.message.reply_text("لطفاً از دکمه‌های موجود استفاده کن.")

# اجرای اپلیکیشن
if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 8443))
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ثبت هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(show_location_details, pattern="^loc_"))
    app.add_handler(CallbackQueryHandler(handle_admin_actions, pattern="^admin_"))
    register_admin_handlers(app)

    print("🤖 ربات با موفقیت اجرا شد. (با Webhook روی Render)")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=WEBHOOK_URL
    )
