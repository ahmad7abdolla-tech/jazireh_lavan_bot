from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

from bot.locations.locations_data import load_locations, get_location_by_id
from bot.admins import is_admin

def start_locations(update: Update, context: CallbackContext):
    locations = load_locations()
    categories = list({loc['category'] for loc in locations})
    keyboard = [[InlineKeyboardButton(cat, callback_data=f"category_{cat}")] for cat in categories]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("لطفاً یک دسته‌بندی انتخاب کنید:", reply_markup=reply_markup)

def category_selected(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    category = query.data.replace("category_", "")
    locations = [loc for loc in load_locations() if loc['category'] == category]
    keyboard = [[InlineKeyboardButton(loc['name'], callback_data=f"location_{loc['id']}")] for loc in locations]
    keyboard.append([InlineKeyboardButton("بازگشت", callback_data="back_to_categories")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(f"لوکیشن‌های دسته‌بندی {category}:", reply_markup=reply_markup)

def location_selected(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    location_id = query.data.replace("location_", "")
    location = get_location_by_id(location_id)
    if not location:
        query.edit_message_text("لوکیشن پیدا نشد.")
        return

    text = f"🏞️ *{location['name']}*\n\n{location['description']}\n\n📂 دسته‌بندی: {location['category']}"
    # ارسال عکس‌ها و متن
    media_group = []
    for photo_url in location.get('photos', []):
        media_group.append({'type': 'photo', 'media': photo_url})
    query.message.reply_media_group(media_group)
    query.edit_message_text(text, parse_mode='Markdown')

def back_to_categories(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    start_locations(update, context)

# Handler ها و ثبت آن‌ها در Dispatcher:
def register_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('locations', start_locations))
    dispatcher.add_handler(CallbackQueryHandler(category_selected, pattern=r"^category_"))
    dispatcher.add_handler(CallbackQueryHandler(location_selected, pattern=r"^location_"))
    dispatcher.add_handler(CallbackQueryHandler(back_to_categories, pattern="back_to_categories"))
