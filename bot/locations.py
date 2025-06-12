import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, CallbackQueryHandler

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

# نمایش لیست لوکیشن‌ها به کاربر
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
        await query.message.reply_photo(photo=media[0], caption=text, parse_mode="Markdown")
    else:
        await query.edit_message_text(text, parse_mode="Markdown")

# هندلر پیام‌های ادمین برای مدیریت افزودن، ویرایش، حذف لوکیشن
async def handle_admin_location_steps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = context.user_data
    state = user_data.get("admin_state")
    text = update.message.text if update.message else None
    photos = update.message.photo if update.message else None

    # -------------------- افزودن لوکیشن -------------------
    if state == "add_name":
        if not text:
            await update.message.reply_text("لطفاً نام معتبر ارسال کنید.")
            return True
        user_data["new_location"] = {"name": text.strip()}
        user_data["admin_state"] = "add_photo"
        await update.message.reply_text("لطفاً عکس لوکیشن را ارسال کنید (فقط یک عکس).")
        return True

    if state == "add_photo":
        if not photos:
            await update.message.reply_text("لطفاً یک عکس معتبر ارسال کنید.")
            return True
        photo = photos[-1]
        file_id = photo.file_id
        user_data["new_location"]["photos"] = [file_id]
        user_data["admin_state"] = "add_description"
        await update.message.reply_text("لطفاً توضیح مختصر درباره لوکیشن را ارسال کنید.")
        return True

    if state == "add_description":
        if not text:
            await update.message.reply_text("لطفاً یک توضیح معتبر ارسال کنید.")
            return True
        user_data["new_location"]["description"] = text.strip()

        locations = load_locations()
        new_id = str(len(locations) + 1)
        user_data["new_location"]["id"] = new_id
        locations.append(user_data["new_location"])
        save_locations(locations)

        await update.message.reply_text(f"لوکیشن «{user_data['new_location']['name']}» با موفقیت اضافه شد.")
        user_data.pop("admin_state", None)
        user_data.pop("new_location", None)
        return True

    # -------------------- ویرایش لوکیشن -------------------
    if state == "edit_select":
        locations = load_locations()
        loc = next((l for l in locations if l["id"] == text), None)
        if not loc:
            await update.message.reply_text("لوکیشن نامعتبر است، لطفاً یکی از شناسه‌ها را وارد کنید.")
            return True
        user_data["edit_location"] = loc
        user_data["admin_state"] = "edit_name"
        await update.message.reply_text(f"نام فعلی: {loc['name']}\nنام جدید را ارسال کنید یا /skip را برای رد کردن ارسال کنید.")
        return True

    if state == "edit_name":
        if text == "/skip":
            user_data["admin_state"] = "edit_photo"
            await update.message.reply_text("لطفاً عکس جدید را ارسال کنید یا /skip برای رد کردن.")
            return True
        if not text:
            await update.message.reply_text("لطفاً یک نام معتبر ارسال کنید یا /skip برای رد کردن.")
            return True
        user_data["edit_location"]["name"] = text.strip()
        user_data["admin_state"] = "edit_photo"
        await update.message.reply_text("لطفاً عکس جدید را ارسال کنید یا /skip برای رد کردن.")
        return True

    if state == "edit_photo":
        if text == "/skip":
            user_data["admin_state"] = "edit_description"
            await update.message.reply_text("لطفاً توضیح جدید را ارسال کنید یا /skip برای رد کردن.")
            return True
        if photos:
            photo = photos[-1]
            file_id = photo.file_id
            user_data["edit_location"]["photos"] = [file_id]
            user_data["admin_state"] = "edit_description"
            await update.message.reply_text("عکس جدید ثبت شد.\nلطفاً توضیح جدید را ارسال کنید یا /skip برای رد کردن.")
            return True
        await update.message.reply_text("لطفاً یک عکس معتبر ارسال کنید یا /skip برای رد کردن.")
        return True

    if state == "edit_description":
        if text == "/skip":
            # پایان ویرایش بدون تغییر توضیح
            pass
        elif text:
            user_data["edit_location"]["description"] = text.strip()
        else:
            await update.message.reply_text("لطفاً یک متن معتبر ارسال کنید یا /skip برای رد کردن.")
            return True

        # ذخیره تغییرات
        locations = load_locations()
        for i, loc in enumerate(locations):
            if loc["id"] == user_data["edit_location"]["id"]:
                locations[i] = user_data["edit_location"]
                break
        save_locations(locations)

        await update.message.reply_text(f"لوکیشن «{user_data['edit_location']['name']}» با موفقیت ویرایش شد.")
        user_data.pop("admin_state", None)
        user_data.pop("edit_location", None)
        return True

    # -------------------- حذف لوکیشن -------------------
    if state == "delete_select":
        locations = load_locations()
        loc = next((l for l in locations if l["id"] == text), None)
        if not loc:
            await update.message.reply_text("شناسه نامعتبر است، لطفاً شناسه درست را ارسال کنید.")
            return True
        locations = [l for l in locations if l["id"] != text]
        save_locations(locations)
        await update.message.reply_text(f"لوکیشن «{loc['name']}» با موفقیت حذف شد.")
        user_data.pop("admin_state", None)
        return True

    return False

# نمایش لیست لوکیشن‌ها برای ویرایش یا حذف (دریافت callback)
async def handle_admin_edit_or_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_data = context.user_data

    if data == "admin_add_location":
        user_data["admin_state"] = "add_name"
        await query.message.reply_text("🟢 لطفاً نام لوکیشن جدید را ارسال کنید.")
        return

    elif data == "admin_edit_location":
        locations = load_locations()
        if not locations:
            await query.message.reply_text("فعلاً لوکیشنی ثبت نشده است.")
            return
        keyboard = [[InlineKeyboardButton(f"{loc['name']} (ID: {loc['id']})", callback_data=f"edit_{loc['id']}")] for loc in locations]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("لطفاً لوکیشن مورد نظر برای ویرایش را انتخاب کنید:", reply_markup=
