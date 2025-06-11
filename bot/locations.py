from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ContextTypes, CallbackContext, ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from bot.admins import ADMIN_IDS, admin_required
from bot.database import get_locations_db, add_location_db, update_location_db, delete_location_db
import logging

logger = logging.getLogger(__name__)

# مراحل افزودن لوکیشن توسط ادمین
ADD_NAME, ADD_IMAGE, ADD_DESC = range(3)

async def locations_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش لیست تمام لوکیشن‌ها به کاربر عادی"""
    locations = await get_locations_db()
    if not locations:
        await update.message.reply_text("❌ هیچ لوکیشنی یافت نشد.")
        return

    keyboard = []
    for loc in locations:
        keyboard.append([InlineKeyboardButton(loc['name'], callback_data=f"show_loc_{loc['id']}")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")])

    await update.message.reply_text(
        "📍 لوکیشن‌های جزیره لاوان:\nلطفاً یک لوکیشن انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_location_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نمایش جزئیات لوکیشن و گالری عکس‌ها"""
    query = update.callback_query
    await query.answer()

    loc_id = query.data.split("_")[-1]
    loc = await get_location_db(loc_id)
    if not loc:
        await query.edit_message_text("❌ لوکیشن یافت نشد.")
        return

    media = []
    caption_first = f"📍 {loc['name']}\n\n"
    for i, img_file_id in enumerate(loc.get('images', [])):
        if i == 0:
            media.append(InputMediaPhoto(media=img_file_id, caption=caption_first + loc.get('description', '')))
        else:
            media.append(InputMediaPhoto(media=img_file_id))

    if media:
        await query.edit_message_media(media=media[0], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="locations_menu")]]))
        if len(media) > 1:
            for m in media[1:]:
                await context.bot.send_media_group(chat_id=query.message.chat_id, media=media)
    else:
        await query.edit_message_text(f"📍 {loc['name']}\n\n{loc.get('description', '')}",
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت", callback_data="locations_menu")]]))

@admin_required
async def admin_locations_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پنل ادمین برای مدیریت لوکیشن‌ها"""
    keyboard = [
        [InlineKeyboardButton("➕ افزودن لوکیشن جدید", callback_data="admin_add_loc")],
        [InlineKeyboardButton("✏️ ویرایش لوکیشن‌ها", callback_data="admin_edit_list")],
        [InlineKeyboardButton("🔙 خروج از پنل مدیریت", callback_data="admin_exit")]
    ]
    await update.message.reply_text(
        "🛠️ پنل مدیریت لوکیشن‌ها:\nیک گزینه انتخاب کنید.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@admin_required
async def start_add_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع فرآیند افزودن لوکیشن توسط ادمین - دریافت نام"""
    await update.message.reply_text("📝 لطفاً نام لوکیشن را وارد کنید:")
    return ADD_NAME

async def add_location_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_location'] = {'name': update.message.text, 'images': []}
    await update.message.reply_text("📷 لطفاً یک عکس از لوکیشن ارسال کنید:")
    return ADD_IMAGE

async def add_location_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("⚠️ لطفاً فقط یک عکس ارسال کنید.")
        return ADD_IMAGE

    photo = update.message.photo[-1]  # عکس با بالاترین کیفیت
    file_id = photo.file_id
    context.user_data['new_location']['images'].append(file_id)
    await update.message.reply_text("📝 حالا لطفاً توضیحات کوتاه درباره عکس را وارد کنید:")
    return ADD_DESC

async def add_location_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['new_location']['description'] = update.message.text
    # ذخیره لوکیشن در دیتابیس
    new_loc = context.user_data['new_location']
    loc_id = await add_location_db(new_loc)
    await update.message.reply_text(f"✅ لوکیشن «{new_loc['name']}» با موفقیت اضافه شد.\n\n🔙 برای برگشت /admin بزنید.")
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_add_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ عملیات افزودن لوکیشن لغو شد.")
    context.user_data.clear()
    return ConversationHandler.END


def register_locations_handlers(app):
    from telegram.ext import CommandHandler

    app.add_handler(CommandHandler("locations", locations_menu))
    app.add_handler(CallbackQueryHandler(show_location_details, pattern=r"^show_loc_"))
    app.add_handler(CallbackQueryHandler(lambda u, c: locations_menu(u, c), pattern="locations_menu"))

    # ادمین
    app.add_handler(CommandHandler("admin", admin_locations_menu))
    app.add_handler(CallbackQueryHandler(start_add_location, pattern="admin_add_loc"))

    add_location_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.User(ADMIN_IDS), add_location_name)],
        states={
            ADD_NAME: [MessageHandler(filters.TEXT & filters.User(ADMIN_IDS), add_location_name)],
            ADD_IMAGE: [MessageHandler(filters.PHOTO & filters.User(ADMIN_IDS), add_location_image)],
            ADD_DESC: [MessageHandler(filters.TEXT & filters.User(ADMIN_IDS), add_location_description)],
        },
        fallbacks=[CommandHandler("cancel", cancel_add_location)],
    )
    app.add_handler(add_location_conv)
