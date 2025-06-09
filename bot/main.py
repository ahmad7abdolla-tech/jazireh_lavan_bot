import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# توکن ذخیره‌شده
BOT_TOKEN = "7586578372:AAGlPQ7tNVs4-FxaHatLH8oZjSpPOSZzCsM"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# دکمه‌های اولیه
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        ["🗺️ درباره لاوان", "🌦️ هوای لاوان الان چطوره؟"],
        ["📅 پیش‌بینی ۳ روز آینده", "📸 تصاویر لاوان"]
    ],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! به ربات جزیره لاوان خوش اومدی 🌴",
        reply_markup=main_menu
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🗺️ درباره لاوان":
        await update.message.reply_text("جزیره لاوان یکی از جزایر زیبا و استراتژیک خلیج‌فارسه...")
    elif text == "🌦️ هوای لاوان الان چطوره؟":
        await update.message.reply_text("در آینده اطلاعات هواشناسی به این بخش اضافه میشه.")
    elif text == "📅 پیش‌بینی ۳ روز آینده":
        await update.message.reply_text("پیش‌بینی سه‌روزه در حال توسعه است.")
    elif text == "📸 تصاویر لاوان":
        await update.message.reply_text("در آینده تصاویر زیبایی از لاوان قرار می‌دیم.")
    else:
        await update.message.reply_text("دستور نامعتبر. لطفاً از دکمه‌ها استفاده کن.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("ربات اجرا شد...")
    app.run_polling()
