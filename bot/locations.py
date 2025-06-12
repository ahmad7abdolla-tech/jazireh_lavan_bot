import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

LOCATIONS_FILE = os.path.join(os.path.dirname(__file__), "locations.json")

def load_locations():
    if not os.path.exists(LOCATIONS_FILE):
        return []
    with open(LOCATIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_locations(locations):
    with open(LOCATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(locations, f, ensure_ascii=False, indent=2)

async def handle_locations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    locations = load_locations()
    if not locations:
        await update.message.reply_text("فعلاً لوکیشنی ثبت نشده است.")
        return
    keyboard = [
        [InlineKeyboardButton(loc["name"], callback_data=f"loc_{loc['id']}")]
        for loc in locations
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("لوکیشن‌های جزیره لاوان:", reply_markup=reply_markup)

async def show_location_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    loc_id = query.data.replace("loc_", "")
    locations = load_locations()
    loc = next((l for l in locations if l["id"] == loc_id), None)
    if not loc:
        await query.edit_message_text("لوکیشن پیدا نشد.")
        return
    
    text = f"🏝️ *{loc['name']}*\n\n{loc.get('description', 'بدون توضیح')}"
    media = loc.get("photos", [])
    if media:
        await query.message.reply_photo(photo=media[0], caption=text, parse_mode="Markdown")
    else:
        await query.edit_message_text(text, parse_mode="Markdown")

# هندلر مرحله‌ای افزودن لوکیشن برای ادمین
async def handle_admin_add_location_steps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    state = user_data.get("admin_state")
    if state not in ("add_name", "add_photo", "add_description"):
        return False  # این هندلر مسئول این پیام نیست
    
    # بررسی نوع پیام
    if update.message is None:
        return True  # پیام نامعتبر اما هندل شده

    if state == "add_name":
        name = update.message.text
        if not name or name.strip() == "":
            await update.message.reply_text("لطفاً نام معتبر ارسال کنید.")
            return True
        user_data["new_location"] = {"name": name.strip()}
        user_data["admin_state"] = "add_photo"
        await update.message.reply_text("لطفاً عکس لوکیشن را ارسال کنید (فقط یک عکس).")
        return True

    elif state == "add_photo":
        if not update.message.photo:
            await update.message.reply_text("لطفاً یک عکس معتبر ارسال کنید.")
            return True
        photo = update.message.photo[-1]
        file_id = photo.file_id
        user_data["new_location"]["photos"] = [file_id]
        user_data["admin_state"] = "add_description"
        await update.message.reply_text("لطفاً توضیح مختصر درباره لوکیشن را ارسال کنید.")
        return True

    elif state == "add_description":
        description = update.message.text
        if not description or description.strip() == "":
            await update.message.reply_text("لطفاً یک توضیح معتبر ارسال کنید.")
            return True
        user_data["new_location"]["description"] = description.strip()

        locations = load_locations()
        new_id = str(len(locations) + 1)
        user_data["new_location"]["id"] = new_id
        locations.append(user_data["new_location"])
        save_locations(locations)

        await update.message.reply_text(f"لوکیشن «{user_data['new_location']['name']}» با موفقیت اضافه شد.")
        user_data.pop("admin_state", None)
        user_data.pop("new_location", None)
        return True

    return False

def register_location_handlers(app):
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_admin_add_location_steps))
