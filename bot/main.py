import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from khayyam import JalaliDatetime
from datetime import datetime
import os

# --- اطلاعات ثابت ---
BOT_TOKEN = "7586578372:AAGlPQ7tNVs4-FxaHatLH8oZjSpPOSZzCsM"
OPENWEATHER_API_KEY = "31cd3332815266315f25a40e56962a52"
LAT, LON = 26.7917, 54.5125
WEATHER_URL = "https://api.openweathermap.org/data/2.5/forecast"

# --- تنظیمات لاگ ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- تبدیل تاریخ ---
def format_dates():
    now = datetime.now()
    jalali = JalaliDatetime(now).strftime('%Y/%m/%d')
    hijri = now.strftime('%Y-%m-%d')  # جایگزین برای تاریخ قمری (به‌صورت نمادین)
    gregorian = now.strftime('%Y/%m/%d')
    return jalali, hijri, gregorian

# --- دریافت پیش‌بینی هوا ---
def get_forecast():
    try:
        response = requests.get(WEATHER_URL, params={
            'lat': LAT,
            'lon': LON,
            'appid': OPENWEATHER_API_KEY,
            'units': 'metric',
            'lang': 'fa',
            'cnt': 40
        })
        response.raise_for_status()
        data = response.json()

        daily = {}
        for item in data['list']:
            dt_txt = item['dt_txt'].split(' ')[0]
            if dt_txt not in daily:
                daily[dt_txt] = item

        forecasts = list(daily.values())[:5]
        return forecasts
    except Exception as e:
        return str(e)

# --- پردازش پیام هواشناسی ---
def build_weather_message(current, forecast_list):
    weather_desc = current['weather'][0]['description'].capitalize()
    temp = current['main']['temp']
    humidity = current['main']['humidity']
    wind_speed = current['wind']['speed']
    wind_dir = current['wind']['deg']
    pressure = current['main']['pressure']

    wind_directions = ['شمال', 'شمال‌شرق', 'شرق', 'جنوب‌شرق', 'جنوب', 'جنوب‌غرب', 'غرب', 'شمال‌غرب']
    wind_index = round(((wind_dir % 360) / 45)) % 8
    wind_compass = wind_directions[wind_index]

    jalali, hijri, gregorian = format_dates()

    message = f"""🌤️ <b>وضعیت فعلی هوای لاوان:</b>

✅ توضیح: {weather_desc}
🌡️ دما: {temp}°C
💧 رطوبت: {humidity}%
💨 باد: {wind_speed} m/s ({wind_compass})
🔽 فشار هوا: {pressure} hPa

──────────────

📆 <b>تاریخ:</b>
🔹 شمسی: {jalali}
🔹 قمری: {hijri}
🔹 میلادی: {gregorian}

──────────────

📈 <b>پیش‌بینی پنج روز آینده:</b>"""

    for day in forecast_list:
        dt = datetime.fromtimestamp(day['dt'])
        jalali_date = JalaliDatetime(dt).strftime('%Y/%m/%d')
        weekday = JalaliDatetime(dt).strftime('%A')
        desc = day['weather'][0]['description'].capitalize()
        temp = day['main']['temp']
        humidity = day['main']['humidity']
        wind = day['wind']['speed']
        rain = day.get('rain', {}).get('3h', 0)

        message += f"""

🔹 {weekday} {jalali_date} – {desc}
   • 🌡️ دما: {temp}°C
   • 💧 رطوبت: {humidity}%
   • 💨 سرعت باد: {wind} m/s
   • ☔ بارندگی: {rain} mm"""

    return message

# --- استارت ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🌦️ هوای لاوان الان چطوره؟", callback_data='weather')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! یکی از گزینه‌های زیر رو انتخاب کن:", reply_markup=reply_markup)

# --- کلیک روی دکمه هوا ---
async def handle_weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        forecast_data = get_forecast()
        if isinstance(forecast_data, str):
            await query.edit_message_text(f"خطا در دریافت اطلاعات هواشناسی: {forecast_data}")
            return

        current = forecast_data[0]
        message = build_weather_message(current, forecast_data)

        await query.edit_message_text(message, parse_mode='HTML')
    except Exception as e:
        await query.edit_message_text(f"خطای غیرمنتظره: {str(e)}")

# --- اجرای ربات ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_weather))
    app.run_polling()
