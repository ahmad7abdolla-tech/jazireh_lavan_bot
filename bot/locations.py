import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, ConversationHandler, MessageHandler, filters

LOCATIONS_FILE = os.path.join(os.path.dirname(__file__), "locations.json")

# مراحل افزودن لوکیشن
NAME, PHOTO, DESCRIPTION = range(3)

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
    media = []
    for file_id in loc.get("photos", []):
        media.append(file_id)
    # ارسال عکس و متن
    if media:
        # اگر چند عکس هست، می‌توان از media group استفاده کرد (اختیاری)
        await query.message.reply_photo(photo=media[0], caption=text, parse_mode="Markdown")
    else:
        await query.edit_message_text(text, parse_mode="Markdown")

# --------------- افزودن لوکیشن توسط ادمین -----------------

async def add_location_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.bot_data.get("admins") or user_id not in context.bot_data["admins"]:
        await update.message.reply_text("شما دسترسی ادمین ندارید.")
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
    photo = update.message.photo[-1]  # بهترین کیفیت عکس
    file_id = photo.file_id
    context.user_data["new_location"]["photos"] = [file_id]
    await update.message.reply_text("توضیح مختصر درباره لوکیشن بنویسید:")
    return DESCRIPTION

async def add_location_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text.strip()
    context.user_data["new_location"]["description"] = description
    
    # بارگذاری لوکیشن‌های قبلی
    locations = load_locations()
    
    # تولید شناسه جدید (می‌تواند یک رشته یکتا ساده باشد)
    new_id = str(len(locations) + 1)
    context.user_data["new_location"]["id"] = new_id
    
    # اضافه کردن لوکیشن جدید به لیست
    locations.append(context.user_data["new_location"])
    save_locations(locations)
    
    await update.message.reply_text(f"لوکیشن «{context.user_data['new_location']['name']}» با موفقیت اضافه شد.")
    return ConversationHandler.END

async def add_location_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("عملیات افزودن لوکیشن لغو شد.")
    return ConversationHandler.END

def register_location_handlers(app):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("addlocation", add_location_start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_location_name)],
            PHOTO: [MessageHandler(filters.PHOTO, add_location_photo)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_location_description)],
        },
        fallbacks=[CommandHandler("cancel", add_location_cancel)],
        allow_reentry=True,
    )
    app.add_handler(conv_handler)
