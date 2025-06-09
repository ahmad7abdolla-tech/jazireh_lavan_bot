# bot/weather_today.py

import requests
from khayyam import JalaliDatetime
import datetime
from hijri_converter import convert
from telegram import Update
from telegram.ext import ContextTypes

API_KEY = "31cd3332815266315f25a40e56962a52"
LAT, LON = 26.7917, 54.5125
UNITS = "metric"
LANG = "fa"

async def handle_weather_today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/onecall?"
            f"lat={LAT}&lon={LON}&appid={API_KEY}&units={UNITS}&lang={LANG}"
        )
        response = requests.get(url)
        data = response.json()

        # وضعیت فعلی
        current = data["current"]
        description = current["weather"][0]["description"].capitalize()
        temp = current["temp"]
        humidity = current["humidity"]
        wind_speed = current["wind_speed"]
        wind_deg = current["wind_deg"]
        pressure = current["pressure"]

        wind_dirs = ['شمال', 'شمال‌شرق', 'شرق', 'جنوب‌شرق', 'جنوب', 'جنوب‌غرب', 'غرب', 'شمال‌غرب']
        wind_index = int((wind_deg + 22.5) % 360 / 45)
        wind_direction = wind_dirs[wind_index]

        # تاریخ‌ها
        now = datetime.datetime.now()
        jalali_date = JalaliDatetime(now).strftime('%Y/%m/%d')
        hijri_date = convert.Gregorian(now.year, now.month, now.day).to_hijri().isoformat()
        gregorian_date = now.strftime('%Y/%m/%d')

        # پیام اصلی
        message = f"🌤️ وضعیت فعلی هوای لاوان:\n\n"
        message += f"✅ توضیح: {description}\n"
        message += f"🌡️ دما: {temp}°C\n"
        message += f"💧 رطوبت: {humidity}%\n"
        message += f"💨 باد: {wind_speed} m/s ({wind_direction})\n"
        message += f"🔽 فشار هوا: {pressure} hPa\n"
        message += f"\n──────────────\n\n"

        message += f"📆 تاریخ:\n"
        message += f"🔹 شمسی: {jalali_date}\n"
        message += f"🔹 قمری: {hijri_date}\n"
        message += f"🔹 میلادی: {gregorian_date}\n"
        message += f"\n──────────────\n\n"

        # پیش‌بینی ۵ روز آینده
        message += f"📈 پیش‌بینی پنج روز آینده:\n"
        for i in range(5):
            day_data = data["daily"][i]
            dt = datetime.datetime.fromtimestamp(day_data["dt"])
            weekday = JalaliDatetime(dt).strftime('%A')
            jalali = JalaliDatetime(dt).strftime('%Y/%m/%d')
            desc = day_data["weather"][0]["description"].capitalize()
            temp_day = day_data["temp"]["day"]
            humidity = day_data["humidity"]
            wind_speed = day_data["wind_speed"]
            rain = day_data.get("rain", 0.0)

            message += f"🔹 {weekday} {jalali} – {desc}\n"
            message += f"   • 🌡️ دما: {temp_day}°C\n"
            message += f"   • 💧 رطوبت: {humidity}%\n"
            message += f"   • 💨 سرعت باد: {wind_speed} m/s\n"
            message += f"   • ☔ بارندگی: {rain} mm\n\n"

        await update.message.reply_text(message.strip())

    except Exception as e:
        await update.message.reply_text(f"خطا در دریافت اطلاعات هواشناسی: {e}")
