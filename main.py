from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from bot.weather_today import handle_weather_today
from bot.locations.locations_handler import register_handlers

BOT_TOKEN = "7586578372:AAGlPQ7tNVs4-FxaHatLH8oZjSpPOSZzCsM"

# کیبورد اصلی با دکمه جدید لوکیشن‌ها
keyboard = [
    ["هوای لاوان الان چطوره؟"],
    ["📍 لوکیشن‌های جذاب از جزیره لاوان"]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 👋 \nحیاکم الله😉 به ربات جزیره لاوان خوش آمدی.\n\nیکی از دکمه‌ها رو انتخاب کن:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "هوای لاوان الان چطوره؟":
        await update.message.reply_text("⏳ در حال دریافت اطلاعات هواشناسی...")
        response = handle_weather_today()
        await update.message.reply_text(response)

    elif text == "📍 لوکیشن‌های جذاب از جزیره لاوان":
        # فراخوانی دستور شروع نمایش لوکیشن‌ها
        # فرض بر این که تابع start_locations در locations_handler هست
        # و آنجا async تعریف شده و export شده
        from bot.locations.locations_handler import start_locations
        await start_locations(update, context)

    else:
        await update.message.reply_text("لطفاً از دکمه‌های موجود استفاده کن.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # ثبت هندلرهای لوکیشن‌ها به شکل صحیح با application
    register_handlers(app)

    print("🤖 ربات با موفقیت اجرا شد.")
    app.run_polling()
