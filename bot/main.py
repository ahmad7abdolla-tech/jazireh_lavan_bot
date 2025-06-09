import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# توکن اختصاصی ذخیره شده برای همیشه
BOT_TOKEN = "7586578372:AAGlPQ7tNVs4-FxaHatLH8oZjSpPOSZzCsM"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! ربات جزیره لاوان آماده است.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    
    print("ربات اجرا شد...")
    app.run_polling()
