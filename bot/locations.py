import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.config import MAX_IMAGE_SIZE_MB

LOCATIONS_FILE = "bot/locations.json"

def load_locations():
    try:
        with open(LOCATIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

async def handle_locations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    locations = load_locations()
    if not locations:
        await update.message.reply_text("فعلاً لوکیشنی موجود نیست.")
        return
    
    keyboard = []
    for loc in locations:
        keyboard.append([InlineKeyboardButton(loc['name'], callback_data=f"loc_{loc['id']}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("لطفاً یک لوکیشن را انتخاب کنید:", reply_markup=reply_markup)

async def show_location_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    loc_id = query.data.replace("loc_", "")
    locations = load_locations()
    
    location = next((loc for loc in locations if loc['id'] == loc_id), None)
    if not location:
        await query.answer("لوکیشن یافت نشد.", show_alert=True)
        return
    
    # نمایش نام و توضیح لوکیشن
    text = f"📍 <b>{location['name']}</b>\n\n{location['description']}"
    
    media_group = []
    # اگر عکس‌های متعدد هست، ارسال گروهی عکس‌ها
    for photo_url in location.get("photos", []):
        media_group.append(photo_url)  # این قسمت نیاز به ارسال MediaGroup دارد، اما ساده‌شده است
    
    await query.message.reply_text(text, parse_mode="HTML")
    await query.answer()

