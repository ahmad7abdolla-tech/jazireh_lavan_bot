from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from bot.weather_today import handle_weather_today

BOT_TOKEN = "7586578372:AAEIkVr4Wq23NSkLuSPRl1yqboqd7_cW0ac"

keyboard = [
    ["🌦 هوای لاوان الان چطوره؟"],
    ["📍لوکیشن‌های جزیره لاوان"],
    ["🏨معرفی اقامتگاه‌ها و امکانات رفاهی"],
    ["📰اخبار جزیره لاوان"]  # دکمه جدید اضافه شد
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 👋 \n حیاکم الله😉 به ربات جزیره لاوان خوش آمدی.\n\nیکی از دکمه‌ها رو انتخاب کن:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🌦 هوای لاوان الان چطوره؟":
        await update.message.reply_text("⏳ در حال دریافت اطلاعات هواشناسی...")
        response = handle_weather_today()
        await update.message.reply_text(response)
    
    elif text == "📍لوکیشن‌های جزیره لاوان":
        await update.message.reply_text("در حال توسعه است ⏳")
    
    elif text == "🏨معرفی اقامتگاه‌ها و امکانات رفاهی":
        await update.message.reply_text("در حال توسعه است ⏳")
        
    elif text == "📰اخبار جزیره لاوان":  # پاسخ دکمه جدید
        await update.message.reply_text("در حال توسعه است ⏳")
        
    else:
        await update.message.reply_text("لطفاً از دکمه‌های موجود استفاده کن.")

if __name__ == "__main__":  # ✅ صحیح (با دو underline)
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 ربات با موفقیت اجرا شد.")
    app.run_polling()
