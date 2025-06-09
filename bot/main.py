# main.py

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from bot.weather_today import handle_weather_today

# توکن ربات شما (در حافظه ذخیره شده)
BOT_TOKEN = "7586578372:AAGlPQ7tNVs4-FxaHatLH8oZjSpPOSZzCsM"

# فعال کردن لاگ
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# دکمه‌های منوی اصلی
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("🌦️ هوای لاوان الان چطوره؟", callback_data="weather_today")],
        # دکمه‌های آینده اینجا اضافه می‌شن
    ]
    return InlineKeyboardMarkup(keyboard)

# دستور /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("به ربات جزیره لاوان خوش آمدید 🌴", reply_markup=get_main_menu())

# مدیریت دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "weather_today":
        await handle_weather_today(update, context)
    else:
        await query.edit_message_text("این گزینه هنوز پشتیبانی نمی‌شود.")

# راه‌اندازی ربات
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
