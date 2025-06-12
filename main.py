from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes,
    filters, CallbackQueryHandler, ConversationHandler
)

from bot.weather_today import handle_weather_today
from bot.locations import (
    handle_locations, show_location_details, register_location_handlers,
    add_location_start, add_location_name, add_location_photo, add_location_description, add_location_cancel,
    send_edit_location_list, edit_choose, edit_field_choose,
    edit_name, edit_photo, edit_description,
    send_delete_location_list, delete_choose, delete_confirm,
    NAME, PHOTO, DESCRIPTION, EDIT_CHOOSE, EDIT_NAME, EDIT_PHOTO, EDIT_DESCRIPTION,
    DELETE_CHOOSE, DELETE_CONFIRM
)
from bot.admins import admin_panel, handle_admin_actions, register_admin_handlers

import os
if os.path.exists("bot/locations.json"):
    os.remove("bot/locations.json")

BOT_TOKEN = "7586578372:AAEIkVr4Wq23NSkLuSPRl1yqboqd7_cW0ac"

keyboard = [
    ["🌦 هوای لاوان الان چطوره؟"],
    ["📍لوکیشن‌های جزیره لاوان"],
    ["🏨معرفی اقامتگاه‌ها و امکانات رفاهی"],
    ["📰اخبار جزیره لاوان"],
    ["🛠️ پنل مدیریت (ادمین)"]
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
        await handle_locations(update, context)
    
    elif text == "🏨معرفی اقامتگاه‌ها و امکانات رفاهی":
        await update.message.reply_text("در حال توسعه است ⏳")
        
    elif text == "📰اخبار جزیره لاوان":
        await update.message.reply_text("در حال توسعه است ⏳")
        
    elif text == "🛠️ پنل مدیریت (ادمین)":
        await admin_panel(update, context)
        
    else:
        await update.message.reply_text("لطفاً از دکمه‌های موجود استفاده کن.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # نمایش لوکیشن
    app.add_handler(CallbackQueryHandler(show_location_details, pattern="^loc_"))
    
    # پنل مدیریت
    app.add_handler(CallbackQueryHandler(handle_admin_actions, pattern="^admin_"))
    
 # ConversationHandler افزودن لوکیشن
add_location_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(add_location_start, pattern="^admin_add_location$")],  # ← این خط اصلاح شد
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_location_name)],
        PHOTO: [MessageHandler(filters.PHOTO, add_location_photo)],
        DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_location_description)],
    },
    fallbacks=[CommandHandler("cancel", add_location_cancel)],
)


    # ConversationHandler ویرایش لوکیشن
    edit_location_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(send_edit_location_list, pattern="^admin_edit_location$")],
        states={
            EDIT_CHOOSE: [CallbackQueryHandler(edit_choose, pattern="^admin_edit_.*|admin_edit_cancel$")],
            EDIT_NAME: [CallbackQueryHandler(edit_field_choose, pattern="^edit_name$")] + [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_name)],
            EDIT_PHOTO: [CallbackQueryHandler(edit_field_choose, pattern="^edit_photo$")] + [MessageHandler(filters.PHOTO, edit_photo)],
            EDIT_DESCRIPTION: [CallbackQueryHandler(edit_field_choose, pattern="^edit_description$")] + [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_description)],
        },
        fallbacks=[CommandHandler("cancel", add_location_cancel)],
    )

    # ConversationHandler حذف لوکیشن
    delete_location_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(send_delete_location_list, pattern="^admin_delete_location$")],
        states={
            DELETE_CHOOSE: [CallbackQueryHandler(delete_choose, pattern="^admin_delete_.*|admin_delete_cancel$")],
            DELETE_CONFIRM: [CallbackQueryHandler(delete_confirm, pattern="^delete_confirm_.*")],
        },
        fallbacks=[CommandHandler("cancel", add_location_cancel)],
    )

    # ثبت هندلرها
    app.add_handler(add_location_conv)
    app.add_handler(edit_location_conv)
    app.add_handler(delete_location_conv)
    register_admin_handlers(app)
    register_location_handlers(app)

    print("🤖 ربات با موفقیت اجرا شد. (نسخه کامل: لوکیشن + مدیریت)")
    app.run_polling()
