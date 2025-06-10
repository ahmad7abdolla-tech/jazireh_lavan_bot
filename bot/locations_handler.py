from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler, CallbackQueryHandler,
    MessageHandler, Filters,
    ConversationHandler, CallbackContext
)
from bot.locations.locations_data import (
    load_locations, get_location_by_id,
    add_location, update_location, delete_location
)
from bot.admins import is_admin
import uuid

# مراحل افزودن لوکیشن
NAME, CATEGORY, DESCRIPTION, PHOTOS, KEYWORDS = range(5)

CATEGORIES = ['ساحلی', 'تاریخی', 'تفریحی']

def generate_unique_id():
    return str(uuid.uuid4())

# ---------------- شروع نمایش لوکیشن‌ها -------------------

def start_locations(update: Update, context: CallbackContext):
    locations = load_locations()
    categories = sorted(set(loc['category'] for loc in locations))
    keyboard = [[InlineKeyboardButton(cat, callback_data=f"category_{cat}")] for cat in categories]
    update.message.reply_text("دسته‌بندی‌های لوکیشن‌ها:", reply_markup=InlineKeyboardMarkup(keyboard))

def category_selected(update: Update, context: CallbackContext):
    query = update.callback_query
    category = query.data.replace("category_", "")
    locations = load_locations()
    filtered = [loc for loc in locations if loc['category'] == category]
    keyboard = [[InlineKeyboardButton(loc['name'], callback_data=f"location_{loc['id']}")] for loc in filtered]
    keyboard.append([InlineKeyboardButton("بازگشت", callback_data="back_to_categories")])
    query.edit_message_text(f"لوکیشن‌های دسته‌بندی '{category}':", reply_markup=InlineKeyboardMarkup(keyboard))

def location_selected(update: Update, context: CallbackContext):
    query = update.callback_query
    location_id = query.data.replace("location_", "")
    loc = get_location_by_id(location_id)
    if not loc:
        query.answer("لوکیشن یافت نشد", show_alert=True)
        return

    text = f"🏞️ *{loc['name']}*\n\n"
    text += f"📂 دسته‌بندی: {loc['category']}\n"
    text += f"📝 توضیح: {loc['description']}\n"
    if loc.get('photos'):
        for p in loc['photos']:
            text += f"\n🖼️ {p}"
    if loc.get('keywords'):
        text += "\n\n🔑 کلیدواژه‌ها: " + ", ".join(loc['keywords'])

    query.edit_message_text(text, parse_mode='Markdown')

def back_to_categories(update: Update, context: CallbackContext):
    query = update.callback_query
    start_locations(update, context)

# ---------------- جستجوی لوکیشن -------------------

SEARCH_QUERY = 10

def search_start(update: Update, context: CallbackContext):
    update.message.reply_text("لطفاً کلمه یا عبارت مورد نظر برای جستجو را ارسال کنید:")
    return SEARCH_QUERY

def search_query_received(update: Update, context: CallbackContext):
    query = update.message.text.lower()
    locations = load_locations()
    matched = [loc for loc in locations if
               query in loc['name'].lower() or
               any(query in kw.lower() for kw in loc.get('keywords', []))]
    if not matched:
        update.message.reply_text("هیچ لوکیشنی با این کلیدواژه یافت نشد.")
        return ConversationHandler.END

    keyboard = [[InlineKeyboardButton(loc['name'], callback_data=f"location_{loc['id']}")] for loc in matched]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f"نتایج جستجو برای '{query}':", reply_markup=reply_markup)
    return ConversationHandler.END

# ---------------- افزودن لوکیشن (تعاملی) -------------------

def add_location_start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        update.message.reply_text("شما اجازه استفاده از این دستور را ندارید.")
        return ConversationHandler.END
    update.message.reply_text("لطفاً نام لوکیشن را وارد کنید:")
    return NAME

def receive_name(update: Update, context: CallbackContext):
    context.user_data['new_location'] = {}
    context.user_data['new_location']['id'] = generate_unique_id()
    context.user_data['new_location']['name'] = update.message.text.strip()

    keyboard = [[InlineKeyboardButton(cat, callback_data=f"set_category_{cat}")] for cat in CATEGORIES]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("دسته‌بندی لوکیشن را انتخاب کنید:", reply_markup=reply_markup)
    return CATEGORY

def category_button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    category = query.data.replace("set_category_", "")
    context.user_data['new_location']['category'] = category
    query.answer()
    query.edit_message_text(f"دسته‌بندی '{category}' انتخاب شد.\n\nلطفاً توضیح درباره لوکیشن را وارد کنید:")
    return DESCRIPTION

def receive_description(update: Update, context: CallbackContext):
    context.user_data['new_location']['description'] = update.message.text.strip()
    update.message.reply_text("لطفاً لینک عکس‌ها را به صورت جداشده با ویرگول وارد کنید:")
    return PHOTOS

def receive_photos(update: Update, context: CallbackContext):
    photos_text = update.message.text.strip()
    photos = [p.strip() for p in photos_text.split(',') if p.strip()]
    context.user_data['new_location']['photos'] = photos
    update.message.reply_text("کلیدواژه‌ها را به صورت جداشده با ویرگول وارد کنید:")
    return KEYWORDS

def receive_keywords(update: Update, context: CallbackContext):
    keywords_text = update.message.text.strip()
    keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]
    context.user_data['new_location']['keywords'] = keywords

    new_location = context.user_data['new_location']
    success = add_location(new_location)

    if success:
        update.message.reply_text("لوکیشن با موفقیت اضافه شد!")
    else:
        update.message.reply_text("خطا: شناسه لوکیشن تکراری است.")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("فرایند افزودن لوکیشن لغو شد.")
    return ConversationHandler.END

# ---------------- حذف لوکیشن (ادمین) -------------------

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

# ---------------- ثبت هندلرها -------------------

def register_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler('locations', start_locations))
    dispatcher.add_handler(CallbackQueryHandler(category_selected, pattern=r"^category_"))
    dispatcher.add_handler(CallbackQueryHandler(location_selected, pattern=r"^location_"))
    dispatcher.add_handler(CallbackQueryHandler(back_to_categories, pattern="back_to_categories"))

    # جستجو
    search_conv = ConversationHandler(
        entry_points=[CommandHandler('search', search_start)],
        states={
            SEARCH_QUERY: [MessageHandler(Filters.text & ~Filters.command, search_query_received)]
        },
        fallbacks=[]
    )
    dispatcher.add_handler(search_conv)

    # افزودن لوکیشن تعاملی
    add_location_conv = ConversationHandler(
        entry_points=[CommandHandler('addlocation', add_location_start)],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, receive_name)],
            CATEGORY: [CallbackQueryHandler(category_button_handler, pattern=r"^set_category_")],
            DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, receive_description)],
            PHOTOS: [MessageHandler(Filters.text & ~Filters.command, receive_photos)],
            KEYWORDS: [MessageHandler(Filters.text & ~Filters.command, receive_keywords)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(add_location_conv)

    # حذف لوکیشن
    dispatcher.add_handler(CommandHandler('deletelocation', delete_location_start))
    dispatcher.add_handler(CallbackQueryHandler(delete_location_confirm, pattern=r"^delete_"))
