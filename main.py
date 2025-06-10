from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)
from bot.weather_today import handle_weather_today
from bot.locations.locations_handler import register_handlers

BOT_TOKEN = "7586578372:AAGlPQ7tNVs4-FxaHatLH8oZjSpPOSZzCsM"

keyboard = [["هوای لاوان الان چطوره؟"]]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# دستور شروع /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 👋 \n حیاکم الله😉 به ربات جزیره لاوان خوش آمدی.\n\nیکی از دکمه‌ها رو انتخاب کن:",
        reply_markup=reply_markup
    )

# هندلر برای پیام‌های متنی
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "هوای لاوان الان چطوره؟":
        await update.message.reply_text("⏳ در حال دریافت اطلاعات هواشناسی...")
        response = handle_weather_today()
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("لطفاً از دکمه‌های موجود استفاده کن.")

# --- تبدیل register_handlers برای ApplicationBuilder ---

# چون register_handlers هندلرها را به dispatcher اضافه می‌کند با کد sync،
# باید کمی تغییر بدهیم تا با ApplicationBuilder هماهنگ باشد.

def register_handlers_async(application):
    # در locations_handler.py هندلرها با دسترسی به dispatcher اضافه می‌شوند
    # اینجا dispatcher از application میگیریم و می‌فرستیم به تابع اصلی
    register_handlers(application)

# ولی register_handlers در locations_handler.py هندلرها را به dispatcher می‌فرستد
# اما dispatcher در ApplicationBuilder با application.add_handler اضافه می‌شود
# پس باید تابع register_handlers در locations_handler.py طوری اصلاح شود که
# بتواند application را دریافت کند و از آن add_handler کند

# برای همین نسخه به‌روز شده‌ی register_handlers به صورت زیر باید باشه:

"""
# bot/locations/locations_handler.py - نسخه به‌روز شده register_handlers:

def register_handlers(application):
    application.add_handler(CommandHandler('locations', start_locations))
    application.add_handler(CallbackQueryHandler(category_selected, pattern=r"^category_"))
    application.add_handler(CallbackQueryHandler(location_selected, pattern=r"^location_"))
    application.add_handler(CallbackQueryHandler(back_to_categories, pattern="back_to_categories"))

    search_conv = ConversationHandler(
        entry_points=[CommandHandler('search', search_start)],
        states={
            SEARCH_QUERY: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_query_received)]
        },
        fallbacks=[]
    )
    application.add_handler(search_conv)

    add_location_conv = ConversationHandler(
        entry_points=[CommandHandler('addlocation', add_location_start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
            CATEGORY: [CallbackQueryHandler(category_button_handler, pattern=r"^set_category_")],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description)],
            PHOTOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_photos)],
            KEYWORDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_keywords)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(add_location_conv)

    application.add_handler(CommandHandler('deletelocation', delete_location_start))
    application.add_handler(CallbackQueryHandler(delete_location_confirm, pattern=r"^delete_"))
"""

# اگر بخواهی من نسخه کامل locations_handler.py را با این تغییر هم آماده کنم.

# ---

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # هندلرهای فعلی
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # هندلرهای لوکیشن‌ها (با فرض اینکه register_handlers تغییر کرده و application می‌گیرد)
    register_handlers(app)

    print("🤖 ربات با موفقیت اجرا شد.")
    app.run_polling()
