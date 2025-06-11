from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes
from bot.database import Database

async def handle_locations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        locations = await Database.get_locations()
        
        if not locations:
            await update.message.reply_text("🌴 هنوز نقطه طبیعتی ثبت نشده است.")
            return
        
        keyboard = [
            [InlineKeyboardButton(loc['name'], callback_data=f"loc_{loc['id']}")]
            for loc in locations[:10]  # حداکثر ۱۰ نقطه طبیعت
        ]
        
        await update.message.reply_text(
            "🌿 **نقاط طبیعت جزیره لاوان**\n\n"
            "لطفاً یک گزینه را انتخاب کنید:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("⚠️ خطا در دریافت لیست نقاط طبیعت")

async def show_location_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()
        
        location_id = query.data.split('_')[1]
        location = await Database.get_location(location_id)
        
        if not location:
            await query.edit_message_text("⚠️ نقطه مورد نظر یافت نشد")
            return
        
        # ارسال گالری تصاویر
        if location.get('images'):
            media_group = [
                InputMediaPhoto(img, caption=location['name'] if i == 0 else '')
                for i, img in enumerate(location['images'][:5])  # حداکثر ۵ تصویر
            ]
            await context.bot.send_media_group(
                chat_id=query.message.chat_id,
                media=media_group
            )
        
        # متن معرفی نقطه طبیعت
        description = (
            f"🌄 **{location['name']}**\n\n"
            f"📜 {location.get('description', 'توضیحات تکمیلی موجود نیست')}\n\n"
            f"🌱 ویژگی‌های طبیعی:\n"
            f"{' '.join(['#' + tag for tag in location.get('tags', [])])}"
        )
        
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=description,
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Error: {e}")
        await query.edit_message_text("⚠️ خطا در نمایش اطلاعات")
