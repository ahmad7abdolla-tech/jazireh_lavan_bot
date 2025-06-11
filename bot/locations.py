import json
import os
from telegram import Update, InputMediaPhoto
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters

LOCATIONS_FILE = "bot/locations.json"

# مراحل گفتگو
NAME, PHOTO, PHOTO_DESC = range(3)

# بارگذاری لوکیشن‌ها
def load_locations():
    if not os.path.exists(LOCATIONS_FILE):
        return []
    with open(LOCATIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# ذخیره لوکیشن‌ها
def save_locations(data):
    with open(LOCATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def start_add_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لطفاً نام لوکیشن را ارسال کنید:")
    return NAME

async def receive_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['location_name'] = update.message.text.strip()
    await update.message.reply_text("حالا لطفاً یک عکس ارسال کنید:")
    return PHOTO

async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("لطفاً فقط عکس ارسال کنید.")
        return PHOTO
    photo_file_id = update.message.photo[-1].file_id  # بهترین کیفیت
    context.user_data['photo_file_id'] = photo_file_id
    await update.message.reply_text("لطفاً توضیح تصویر را بنویسید:")
    return PHOTO_DESC

async def receive_photo_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_desc = update.message.text.strip()
    location_name = context.user_data.get('location_name')
    photo_file_id = context.user_data.get('photo_file_id')

    # بارگذاری لوکیشن‌ها و اضافه کردن لوکیشن جدید
    locations = load_locations()
    new_location = {
        "id": f"loc_{len(locations) + 1}",
        "name": location_name,
        "photos": [
            {
                "file_id": photo_file_id,
                "description": photo_desc
            }
        ]
    }
    locations.append(new_location)
    save_locations(locations)

    await update.message.reply_text(f"لوکیشن '{location_name}' با موفقیت اضافه شد.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("فرآیند اضافه کردن لوکیشن لغو شد.")
    return ConversationHandler.END

def register_location_handlers(app):
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('addlocation', start_add_location)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_name)],
            PHOTO: [MessageHandler(filters.PHOTO, receive_photo)],
            PHOTO_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_photo_desc)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    app.add_handler(conv_handler)
