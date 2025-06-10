import json
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from .locations_data import load_locations, save_locations
from .admins import is_admin

SEARCH_QUERY, NAME, CATEGORY, DESCRIPTION, PHOTOS, KEYWORDS = range(6)

# همان کدهای قبل نمایش لوکیشن‌ها اینجا هست...

# ذخیره لوکیشن جدید به صورت موقت در context.user_data
async def add_location_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("❌ شما اجازه افزودن لوکیشن را ندارید.")
        return ConversationHandler.END
    await update.message.reply_text("لطفاً نام لوکیشن جدید را وارد کنید:")
    return NAME

async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_location'] = {}
    context.user_data['new_location']['name'] = update.message.text
    await update.message.reply_text("دسته‌بندی لوکیشن را وارد کنید (مثلاً ساحلی، تاریخی):")
    return CATEGORY

async def receive_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_location']['category'] = update.message.text
    await update.message.reply_text("توضیح مختصر درباره لوکیشن را وارد کنید:")
    return DESCRIPTION

async def receive_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_location']['description'] = update.message.text
    await update.message.reply_text("لینک عکس(ها) را با کاما جدا وارد کنید:")
    return PHOTOS

async def receive_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photos_text = update.message.text
    photos = [p.strip() for p in photos_text.split(",") if p.strip()]
    context.user_data['new_location']['photos'] = photos
    await update.message.reply_text("کلمات کلیدی مرتبط را با کاما جدا وارد کنید:")
    return KEYWORDS

async def receive_keywords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keywords_text = update.message.text
    keywords = [k.strip() for k in keywords_text.split(",") if k.strip()]
    context.user_data['new_location']['keywords'] = keywords

    # شناسه یکتا ایجاد می‌کنیم
    new_loc = context.user_data['new_location']
    new_loc['id'] = str(uuid.uuid4())

    # بارگذاری و افزودن لوکیشن جدید
    locations = load_locations()
    locations.append(new_loc)
    save_locations(locations)

    await update.message.reply_text(f"✅ لوکیشن «{new_loc['name']}» با موفقیت اضافه شد.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ عملیات لغو شد.")
    return ConversationHandler.END

def register_handlers(application):
    application.add_handler(CommandHandler("locations", start_locations))
    application.add_handler(CallbackQueryHandler(category_selected, pattern=r"^category_"))
    application.add_handler(CallbackQueryHandler(location_selected, pattern=r"^location_"))
    application.add_handler(CallbackQueryHandler(back_to_categories, pattern="^back_to_categories"))

    add_location_conv = ConversationHandler(
        entry_points=[CommandHandler("addlocation", add_location_start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_category)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_description)],
            PHOTOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_photos)],
            KEYWORDS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_keywords)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(add_location_conv)
