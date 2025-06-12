import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler, filters
)

LOCATIONS_FILE = os.path.join(os.path.dirname(__file__), "locations.json")

NAME, PHOTO, DESCRIPTION = range(3)
EDIT_CHOOSE, EDIT_FIELD_CHOOSE, EDIT_NAME, EDIT_PHOTO, EDIT_DESCRIPTION = range(10, 15)
DELETE_CHOOSE, DELETE_CONFIRM = range(20, 22)

def load_locations():
    if not os.path.exists(LOCATIONS_FILE):
        return []
    with open(LOCATIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_locations(locations):
    with open(LOCATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(locations, f, ensure_ascii=False, indent=2)

# نمایش لوکیشن‌ها به کاربر عادی
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

# --- افزودن لوکیشن ---

async def add_location_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in context.bot_data.get("admins", []):
        await update.message.reply_text("❌ شما دسترسی ادمین ندارید.")
        return ConversationHandler.END
    await update.message.reply_text("لطفاً نام لوکیشن جدید را وارد کنید:")
    return NAME

async def add_location_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    context.user_data["new_location"] = {"name": name}
    await update.message.reply_text("عکس لوکیشن را ارسال کنید (فقط یک عکس):")
    return PHOTO

async def add_location_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("لطفاً یک عکس معتبر ارسال کنید.")
        return PHOTO
    photo = update.message.photo[-1]
    file_id = photo.file_id
    context.user_data["new_location"]["photos"] = [file_id]
    await update.message.reply_text("توضیح مختصر درباره لوکیشن بنویسید:")
    return DESCRIPTION

async def add_location_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text.strip()
    context.user_data["new_location"]["description"] = description
    locations = load_locations()
    new_id = str(len(locations) + 1)
    context.user_data["new_location"]["id"] = new_id
    locations.append(context.user_data["new_location"])
    save_locations(locations)
    await update.message.reply_text(f"لوکیشن «{context.user_data['new_location']['name']}» با موفقیت اضافه شد.")
    return ConversationHandler.END

async def add_location_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات افزودن لوکیشن لغو شد.")
    return ConversationHandler.END

# --- ویرایش لوکیشن ---

async def send_edit_location_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    locations = load_locations()
    if not locations:
        await update.callback_query.message.reply_text("فعلاً لوکیشنی برای ویرایش وجود ندارد.")
        return ConversationHandler.END
    keyboard = [[InlineKeyboardButton(loc["name"], callback_data=f"admin_edit_{loc['id']}")] for loc in locations]
    keyboard.append([InlineKeyboardButton("❌ انصراف", callback_data="admin_edit_cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text("لوکیشن مورد نظر برای ویرایش را انتخاب کنید:", reply_markup=reply_markup)
    return EDIT_CHOOSE

async def edit_choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "admin_edit_cancel":
        await query.message.edit_text("عملیات ویرایش لغو شد.")
        return ConversationHandler.END
    loc_id = data.replace("admin_edit_", "")
    context.user_data["edit_loc_id"] = loc_id
    keyboard = [
        [InlineKeyboardButton("✏️ ویرایش نام", callback_data="edit_name")],
        [InlineKeyboardButton("📷 ویرایش عکس", callback_data="edit_photo")],
        [InlineKeyboardButton("📝 ویرایش توضیح", callback_data="edit_description")],
        [InlineKeyboardButton("❌ انصراف", callback_data="edit_cancel")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.edit_text("کدام بخش را می‌خواهید ویرایش کنید؟", reply_markup=reply_markup)
    return EDIT_FIELD_CHOOSE

async def edit_field_choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "edit_cancel":
        await query.message.edit_text("عملیات ویرایش لغو شد.")
        return ConversationHandler.END
    if data == "edit_name":
        await query.message.edit_text("نام جدید را وارد کنید:")
        return EDIT_NAME
    elif data == "edit_photo":
        await query.message.edit_text("عکس جدید را ارسال کنید:")
        return EDIT_PHOTO
    elif data == "edit_description":
        await query.message.edit_text("توضیح جدید را وارد کنید:")
        return EDIT_DESCRIPTION
    else:
        await query.answer()
        return EDIT_FIELD_CHOOSE

async def edit_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_name = update.message.text.strip()
    loc_id = context.user_data.get("edit_loc_id")
    locations = load_locations()
    loc = next((l for l in locations if l["id"] == loc_id), None)
    if not loc:
        await update.message.reply_text("لوکیشن پیدا نشد.")
        return ConversationHandler.END
    loc["name"] = new_name
    save_locations(locations)
    await update.message.reply_text(f"نام لوکیشن با موفقیت به «{new_name}» تغییر کرد.")
    return ConversationHandler.END

async def edit_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("لطفاً یک عکس معتبر ارسال کنید.")
        return EDIT_PHOTO
    photo = update.message.photo[-1]
    file_id = photo.file_id
    loc_id = context.user_data.get("edit_loc_id")
    locations = load_locations()
    loc = next((l for l in locations if l["id"] == loc_id), None)
    if not loc:
        await update.message.reply_text("لوکیشن پیدا نشد.")
        return ConversationHandler.END
    loc["photos"] = [file_id]
    save_locations(locations)
    await update.message.reply_text("عکس لوکیشن با موفقیت تغییر کرد.")
    return ConversationHandler.END

async def edit_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_desc = update.message.text.strip()
    loc_id = context.user_data.get("edit_loc_id")
    locations = load_locations()
    loc = next((l for l in locations if l["id"] == loc_id), None)
    if not loc:
        await update.message.reply_text("لوکیشن پیدا نشد.")
        return ConversationHandler.END
    loc["description"] = new_desc
    save_locations(locations)
    await update.message.reply_text("توضیحات لوکیشن با موفقیت تغییر کرد.")
    return ConversationHandler.END

# --- حذف لوکیشن ---

async def send_delete_location_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    locations = load_locations()
    if not locations:
        await update.callback_query.message.reply_text("فعلاً لوکیشنی برای حذف وجود ندارد.")
        return ConversationHandler.END
    keyboard = [[InlineKeyboardButton(loc["name"], callback_data=f"admin_delete_{loc['id']}")] for loc in locations]
    keyboard.append([InlineKeyboardButton("❌ انصراف", callback_data="admin_delete_cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.message.edit_text("لوکیشن مورد نظر برای حذف را انتخاب کنید:", reply_markup=reply_markup)
    return DELETE_CHOOSE

async def delete_choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "admin_delete_cancel":
        await query.message.edit_text("عملیات حذف لغو شد.")
        return ConversationHandler.END
    loc_id = data.replace("admin_delete_", "")
    context.user_data["delete_loc_id"] = loc_id
    await query.message.edit_text("آیا مطمئن هستید که می‌خواهید این لوکیشن را حذف کنید؟", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ بله", callback_data="delete_confirm_yes")],
        [InlineKeyboardButton("❌ خیر", callback_data="delete_confirm_no")],
    ]))
    return DELETE_CONFIRM

async def delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    if data == "delete_confirm_no":
        await query.message.edit_text("عملیات حذف لغو شد.")
        return ConversationHandler.END
    elif data == "delete_confirm_yes":
        loc_id = context.user_data.get("delete_loc_id")
        locations = load_locations()
        new_locations = [l for l in locations if l["id"] != loc_id]
        save_locations(new_locations)
        await query.message.edit_text("لوکیشن با موفقیت حذف شد.")
        return ConversationHandler.END
    else:
        await query.answer()
        return DELETE_CONFIRM

# تعریف ConversationHandlerها

add_location_conv = ConversationHandler(
    entry_points=[CommandHandler("add_location", add_location_start)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_location_name)],
        PHOTO: [MessageHandler(filters.PHOTO, add_location_photo)],
        DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_location_description)],
    },
    fallbacks=[CommandHandler("cancel", add_location_cancel)],
)

edit_location_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(send_edit_location_list, pattern="^admin_edit_start$")],
    states={
        EDIT_CHOOSE: [CallbackQueryHandler(edit_choose, pattern="^admin_edit_.*|admin_edit_cancel$")],
        EDIT_FIELD_CHOOSE: [CallbackQueryHandler(edit_field_choose, pattern="^edit_.*|edit_cancel$")],
        EDIT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_name)],
        EDIT_PHOTO: [MessageHandler(filters.PHOTO, edit_photo)],
        EDIT_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_description)],
    },
    fallbacks=[CommandHandler("cancel", add_location_cancel)],
)

delete_location_conv = ConversationHandler(
    entry_points=[CallbackQueryHandler(send_delete_location_list, pattern="^admin_delete_start$")],
    states={
        DELETE_CHOOSE: [CallbackQueryHandler(delete_choose, pattern="^admin_delete_.*|admin_delete_cancel$")],
        DELETE_CONFIRM: [CallbackQueryHandler(delete_confirm, pattern="^delete_confirm_.*$")],
    },
    fallbacks=[CommandHandler("cancel", add_location_cancel)],
)

def register_location_handlers(app):
    app.add_handler(add_location_conv)
    app.add_handler(edit_location_conv)
    app.add_handler(delete_location_conv)
