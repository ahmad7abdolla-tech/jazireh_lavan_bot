import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters

LOCATIONS_FILE = os.path.join(os.path.dirname(__file__), "locations.json")

# بارگذاری لوکیشن‌ها از فایل JSON
def load_locations():
    if not os.path.exists(LOCATIONS_FILE):
        return []
    with open(LOCATIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ذخیره لوکیشن‌ها در فایل JSON
def save_locations(locations):
    with open(LOCATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(locations, f, ensure_ascii=False, indent=2)

# هندلر نمایش لیست لوکیشن‌ها به کاربر
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

# نمایش جزئیات لوکیشن بر اساس callback_data
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
        # ارسال اولین عکس با کپشن (برای ساده‌سازی)
        await query.message.reply_photo(photo=media[0], caption=text, parse_mode="Markdown")
    else:
        await query.edit_message_text(text, parse_mode="Markdown")

# هندلر پیام‌های ادمین برای افزودن لوکیشن مرحله به مرحله
async def handle_admin_add_location_steps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    state = user_data.get("admin_state")
    if state not in ("add_name", "add_photo", "add_description"):
        return False  # به این هندلر مربوط نیست
    
    text = update.message.text if update.message else None
    photos = update.message.photo if update.message else None

    if state == "add_name":
        if not text:
            await update.message.reply_text("لطفاً نام معتبر ارسال کنید.")
            return True
        user_data["new_location"] = {"name": text.strip()}
        user_data["admin_state"] = "add_photo"
        await update.message.reply_text("لطفاً عکس لوکیشن را ارسال کنید (فقط یک عکس).")
        return True

    elif state == "add_photo":
        if not photos:
            await update.message.reply_text("لطفاً یک عکس معتبر ارسال کنید.")
            return True
        photo = photos[-1]
        file_id = photo.file_id
        user_data["new_location"]["photos"] = [file_id]
        user_data["admin_state"] = "add_description"
        await update.message.reply_text("لطفاً توضیح مختصر درباره لوکیشن را ارسال کنید.")
        return True

    elif state == "add_description":
        if not text:
            await update.message.reply_text("لطفاً یک توضیح معتبر ارسال کنید.")
            return True
        user_data["new_location"]["description"] = text.strip()

        # ذخیره لوکیشن جدید
        locations = load_locations()
        new_id = str(len(locations) + 1)
        user_data["new_location"]["id"] = new_id
        locations.append(user_data["new_location"])
        save_locations(locations)

        await update.message.reply_text(f"لوکیشن «{user_data['new_location']['name']}» با موفقیت اضافه شد.")
        # پاک کردن وضعیت ادمین و داده موقتی
        user_data.pop("admin_state", None)
        user_data.pop("new_location", None)
        return True

    return False

# ثبت هندلرهای مربوط به لوکیشن‌ها (فقط هندلر نمایش و افزودن مرحله به مرحله)
def register_location_handlers(app):
    from telegram.ext import MessageHandler, filters

    # هندلر پیام عمومی برای مراحل ادمین افزودن لوکیشن
    app.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_admin_add_location_steps))
