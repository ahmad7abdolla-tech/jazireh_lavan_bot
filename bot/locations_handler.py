from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CallbackContext, CommandHandler, CallbackQueryHandler,
    MessageHandler, Filters, ConversationHandler
)

from bot.locations.locations_data import load_locations, get_location_by_id, add_location, update_location, delete_location
from bot.admins import is_admin

# --- مراحل جستجو ---
SEARCH_QUERY = 1

def search_start(update: Update, context: CallbackContext):
    update.message.reply_text("لطفاً کلمه یا عبارت مورد نظر برای جستجو را ارسال کنید:")
    return SEARCH_QUERY

def search_query_received(update: Update, context: CallbackContext):
    query = update.message.text.lower()
    locations = load_locations()
    matched = [loc for loc in locations if any(query in kw.lower() for kw in loc.get('keywords', [])) or query in loc['name'].lower()]
    if not matched:
        update.message.reply_text("هیچ لوکیشنی با این کلیدواژه یافت نشد.")
        return ConversationHandler.END

    keyboard = [[InlineKeyboardButton(loc['name'], callback_data=f"location_{loc['id']}")] for loc in matched]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f"نتایج جستجو برای '{query}':", reply_markup=reply_markup)
    return ConversationHandler.END

# --- مدیریت ادمین ---

# مثال ساده حذف لوکیشن (باقی دستورات مشابه می‌شوند)
def delete_location_start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        update.message.reply_text("شما اجازه استفاده از این دستور را ندارید.")
        return

    locations = load_locations()
    keyboard = [[InlineKeyboardButton(loc['name'], callback_data=f"delete_{loc['id']}")] for loc in locations]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("لوکیشنی که می‌خواهید حذف کنید را انتخاب کنید:", reply_markup=reply_markup)

def delete_location_confirm(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        query.answer("شما اجازه حذف ندارید.", show_alert=True)
        return

    location_id = query.data.replace("delete_", "")
    success = delete_location(location_id)
    if success:
        query.edit_message_text("لوکیشن با موفقیت حذف شد.")
    else:
        query.edit_message_text("مشکلی در حذف لوکیشن پیش آمد.")
    query.answer()

def register_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('locations', start_locations))
    dispatcher.add_handler(CallbackQueryHandler(category_selected, pattern=r"^category_"))
    dispatcher.add_handler(CallbackQueryHandler(location_selected, pattern=r"^location_"))
    dispatcher.add_handler(CallbackQueryHandler(back_to_categories, pattern="back_to_categories"))

    # جستجو
    search_conv = ConversationHandler(
        entry_points=[CommandHandler('search', search_start)],
        states={SEARCH_QUERY: [MessageHandler(Filters.text & ~Filters.command, search_query_received)]},
        fallbacks=[]
    )
    dispatcher.add_handler(search_conv)

    # حذف لوکیشن (ادمین)
    dispatcher.add_handler(CommandHandler('deletelocation', delete_location_start))
    dispatcher.add_handler(CallbackQueryHandler(delete_location_confirm, pattern=r"^delete_"))
