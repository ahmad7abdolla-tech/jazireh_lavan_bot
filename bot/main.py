import requests
from datetime import datetime
from khayyam import JalaliDatetime
from hijri_converter import convert
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = "7586578372:AAGlPQ7tNVs4-FxaHatLH8oZjSpPOSZzCsM"
API_KEY = "31cd3332815266315f25a40e56962a52"
LAT, LON = 26.8053, 53.3480

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🌦️ هوای لاوان الان چطوره؟", callback_data="weather_now")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! به ربات جزیره لاوان خوش اومدی 🌴", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "weather_now":
        weather_data = requests.get(
            f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric&lang=fa"
        ).json()

        current = weather_data["list"][0]
        description = current["weather"][0]["description"]
        temp = current["main"]["temp"]
        humidity = current["main"]["humidity"]
        wind_speed = current["wind"]["speed"]
        pressure = current["main"]["pressure"]
        wind_dir = current["wind"].get("deg", 0)

        wind_direction = get_wind_direction(wind_dir)

        today = datetime.utcnow()
        jalali = JalaliDatetime(today).strftime("%Y/%m/%d")
        hijri = convert.Gregorian(today.year, today.month, today.day).to_hijri().isoformat()
        miladi = today.strftime("%Y/%m/%d")

        message = f"""🌤️ *وضعیت فعلی هوای لاوان:*

✅ توضیح: {description.capitalize()}
🌡️ دما: {temp:.1f}°C
💧 رطوبت: {humidity}%
💨 باد: {wind_speed} m/s ({wind_direction})
🔽 فشار هوا: {pressure} hPa

──────────────

📆 *تاریخ:*
🔹 شمسی: {jalali}
🔹 قمری: {hijri}
🔹 میلادی: {miladi}

──────────────

📈 *پیش‌بینی هفت روز آینده:*
"""     
        forecast_text = ""
        for item in weather_data["list"][:7*8:8]:
            date = datetime.utcfromtimestamp(item["dt"])
            day_jalali = JalaliDatetime(date).strftime("%A %Y/%m/%d")
            desc = item["weather"][0]["description"].capitalize()
            t = item["main"]["temp"]
            h = item["main"]["humidity"]
            w = item["wind"]["speed"]
            forecast_text += f"\n🔹 *{day_jalali} – {desc}*\n   • 🌡️ دما: {t:.1f}°C\n   • 💧 رطوبت: {h}%\n   • 💨 سرعت باد: {w} m/s\n   • ☔ بارندگی: 0 mm\n\n"

        message += forecast_text.strip()
        await query.edit_message_text(message, parse_mode="Markdown")

def get_wind_direction(degree):
    dirs = ["شمال", "شمال‌شرق", "شرق", "جنوب‌شرق", "جنوب", "جنوب‌غرب", "غرب", "شمال‌غرب"]
    ix = round(degree / 45) % 8
    return dirs[ix]

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot is running...")
    app.run_polling()
