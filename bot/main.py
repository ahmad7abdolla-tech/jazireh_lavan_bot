from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from weather_today import handle_weather_today

# توکن ربات
BOT_TOKEN = "7586578372:AAGlPQ7tNVs4-FxaHatLH8oZjSpPOSZzCsM"

# کیبورد اصلی
main_keyboard = ReplyKeyboardMarkup(
    [["🌦️ هوای لاوان الان چطوره؟"]],
    resize_keyboard=True
)

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! به ربات جزیره لاوان خوش آمدید 👋", reply_markup=main_keyboard)

# مدیریت پیام‌های متنی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🌦️ هوای لاوان الان چطوره؟":
        await handle_weather_today(update, context)
    else:
        await update.message.reply_text("دستور نامعتبر است. لطفاً یکی از دکمه‌ها را انتخاب کنید.")

# راه‌اندازی برنامه
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
