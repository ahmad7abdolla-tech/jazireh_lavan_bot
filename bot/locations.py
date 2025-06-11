from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import json
from bot.database import get_locations_db

async def handle_locations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    locations = get_locations_db()  # دریافت لیست لوکیشن‌ها از دیتابیس
    
    if not locations:
        await update.message.reply_text("⚠️ در حال حاضر لوکیشنی ثبت نشده است.")
        return
    
    # ایجاد کیبورد اینلاین برای لوکیشن‌ها
    keyboard = [
        [InlineKeyboardButton(loc['name'], callback_data=f"loc_{loc['id']}")]
        for loc in locations[:10]  # حداکثر 10 لوکیشن در صفحه اول
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📍 لیست لوکیشن‌های جزیره لاوان:\n\nلطفاً یک مورد را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def show_location_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    location_id = query.data.split('_')[1]
    location = get_location_details(location_id)  # دریافت جزئیات لوکیشن
    
    if not location:
        await query.edit_message_text("⚠️ لوکیشن مورد نظر یافت نشد.")
        return
    
    # ایجاد گالری تصاویر
    media_group = []
    for i, img in enumerate(location['images'][:10]):  # حداکثر 10 تصویر
        media_group.append(InputMediaPhoto(img, caption=location['name'] if i == 0 else ''))
    
    # ارسال گالری تصاویر
    await context.bot.send_media_group(
        chat_id=query.message.chat_id,
        media=media_group
    )
    
    # ارسال جزئیات متنی
    details_text = f"""
🏝️ **{location['name']}**
📌 {location['description']}

🕒 ساعت کاری: {location.get('working_hours', 'تعیین نشده')}
📞 تماس: {location.get('phone', 'تعیین نشده')}

⭐ امکانات:
{'\n'.join(['- ' + feat for feat in location['features']])}
"""
    
    # ایجاد دکمه‌های اشتراک‌گذاری و بازگشت
    share_btn = InlineKeyboardButton("📤 اشتراک‌گذاری", switch_inline_query=f"location_{location_id}")
    back_btn = InlineKeyboardButton("🔙 بازگشت", callback_data="loc_back")
    
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=details_text,
        reply_markup=InlineKeyboardMarkup([[share_btn], [back_btn]]),
        parse_mode='Markdown'
    )

def get_location_details(location_id: str):
    """تابع کمکی برای دریافت جزئیات لوکیشن از دیتابیس"""
    # پیاده‌سازی واقعی باید از دیتابیس اصلی بخواند
    return {
        "id": location_id,
        "name": "ساحل طلایی لاوان",
        "description": "ساحلی با شن‌های طلایی و امکانات تفریحی",
        "images": ["img1.jpg", "img2.jpg"],
        "working_hours": "8 صبح تا 8 شب",
        "phone": "09123456789",
        "features": ["پارکینگ رایگان", "رستوران دریایی", "اجاره قایق"]
    }
