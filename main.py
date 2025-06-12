from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, CallbackQueryHandler
)

from bot.weather_today import handle_weather_today
from bot.locations import (
    handle_locations, show_location_details, register_location_handlers,
    handle_add_location_steps, handle_edit_location_steps, handle_delete_location_steps
)
from bot.admins import (
    admin_panel, handle_admin_actions, register_admin_handlers,
    is_admin
)

BOT_TOKEN = "7586578372:AAEIkVr4Wq23NSkLuSPRl1yqboqd7_cW0ac"

# منوی اصلی ربات
keyboard = [
    ["🌦 هوای لاوان الان چطوره؟"],
    ["📍لوکیشن‌های جزیره لاوان"],
    ["🏨معرفی اقامتگاه‌ها و امکانات رفاهی"],
    ["📰اخبار جزیره لاوان"],
    ["🛠️ پنل مدیریت (ادمین)"]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


# استارت ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! 👋 \n حیاکم الله😉 به ربات جزیره لاوان خوش آمدی.\n\nیکی از دکمه‌ها رو انتخاب کن:",
        reply_markup=reply_markup
    )


# مدیریت پیام‌های کاربر (دکمه‌ها)
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
        if is_admin(update.effective_user.id):
            await admin_panel(update, context)
        else:
            await update.message.reply_text("⛔ شما دسترسی ادمین ندارید.")

    else:
        # اگر کاربر در حالت افزودن یا ویرایش بود، این پیام بررسی می‌شود:
        user_id = update.effective_user.id
        if context.user_data.get("admin_state"):
            state = context.user_data["admin_state"]
            if state.startswith("add_"):
                await handle_add_location_steps(update, context)
            elif state.startswith("edit_"):
                await handle_edit_location_steps(update, context)
            elif state.startswith("delete_"):
                await handle_delete_location_steps(update, context)
            return
        await update.message.reply_text("لطفاً از دکمه‌های موجود استفاده کن.")


# اجرای ربات
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ثبت هندلرهای پایه
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Callback‌ها
    app.add_handler(CallbackQueryHandler(show_location_details, pattern="^loc_"))
    app.add_handler(CallbackQueryHandler(handle_admin_actions, pattern="^admin_"))

    # هندلرهای خاص لوکیشن و ادمین
    register_admin_handlers(app)
    register_location_handlers(app)

    print("🤖 ربات با موفقیت اجرا شد. (نسخه نهایی با قابلیت کامل پنل ادمین)")
    app.run_polling()
