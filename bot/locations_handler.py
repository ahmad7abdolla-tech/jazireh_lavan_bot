from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from .locations_data import load_locations
from .admins import is_admin

# --- استیت‌های Conversation ---
SEARCH_QUERY, NAME, CATEGORY, DESCRIPTION, PHOTOS, KEYWORDS = range(6)

# --- نمایش دسته‌بندی‌ها ---
async def start_locations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    locations = load_locations()
    categories = sorted(set(loc["category"] for loc in locations))

    keyboard = [
        [InlineKeyboardButton(cat, callback_data=f"category_{cat}")]
        for cat in categories
    ]
    await update.message.reply_text(
        "📂 لطفاً یک دسته‌بندی انتخاب کن:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.replace("category_", "")
    locations = [loc for loc in load_locations() if loc["category"] == category]

    keyboard = [
        [InlineKeyboardButton(loc["name"], callback_data=f"location_{loc['id']}")]
        for loc in locations
    ]
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_categories")])

    await query.edit_message_text(
        f"📍 لوکیشن‌های دسته «{category}»:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def location_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    loc_id = query.data.replace("location_", "")
    locations = load_locations()
    location = next((loc for loc in locations if loc["id"] == loc_id), None)

    if location:
        text = f"📌 {location['name']}\n\n📝 {location['description']}"
        for photo_url in location["photos"]:
            await query.message.reply_photo(photo_url)
        await query.message.reply_text(text)
    else:
        await query.message.reply_text("❌ لوکیشن پیدا نشد.")

async def back_to_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start_locations(update, context)

# --- ثبت هندلرها ---
def register_handlers(application):
    application.add_handler(CommandHandler("locations", start_locations))
    application.add_handler(CallbackQueryHandler(category_selected, pattern=r"^category_"))
    application.add_handler(CallbackQueryHandler(location_selected, pattern=r"^location_"))
    application.add_handler(CallbackQueryHandler(back_to_categories, pattern="^back_to_categories"))
