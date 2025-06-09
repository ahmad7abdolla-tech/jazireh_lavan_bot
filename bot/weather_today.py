import requests
from datetime import datetime
from persiantools.jdatetime import JalaliDate
import hijri_converter
from telegram import Update
from telegram.ext import ContextTypes

# مختصات جزیره لاوان
LAT = 26.7917
LON = 54.5125

# کلید API هواشناسی
API_KEY = "31cd3332815266315f25a40e56962a52"

# تابع پردازش دکمه "هوای لاوان الان چطوره؟"
async def handle_weather_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = f"https://api.openweathermap.org/data/2.5/onecall?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric&lang=fa"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        current = data["current"]
        daily = data["daily"]

        # اطلاعات وضعیت فعلی
        description = current["weather"][0]["description"].capitalize()
        temperature = round(current["temp"], 1)
        humidity = current["humidity"]
        wind_speed = round(current["wind_speed"], 2)
        wind_deg = current["wind_deg"]
        pressure = current["pressure"]
        wind_dir = get_wind_direction(wind_deg)

        # تاریخ‌ها
        now = datetime.utcnow()
        date_miladi = now.strftime("%Y/%m/%d")
        date_shamsi = JalaliDate(now).strftime("%Y/%m/%d")
        date_ghamari = hijri_converter.Gregorian(now.year, now.month, now.day).to_hijri().isoformat()

        # تحلیل روزانه
        analysis = generate_daily_analysis(temperature, wind_speed)

        # ساخت پیام نهایی
        message = f"""🌤️ وضعیت فعلی هوای لاوان:

✅ توضیح: {description}
🌡️ دما: {temperature}°C
💧 رطوبت: {humidity}%
💨 باد: {wind_speed} m/s ({wind_dir})
🔽 فشار هوا: {pressure} hPa

──────────────

📆 تاریخ:
🔹 شمسی: {date_shamsi}
🔹 قمری: {date_ghamari}
🔹 میلادی: {date_miladi}

──────────────

🧭 تحلیل روزانه:
{analysis}

──────────────

📈 پیش‌بینی پنج روز آینده:"""

        # افزودن پیش‌بینی پنج روز آینده
        for day in daily[:5]:
            dt = datetime.utcfromtimestamp(day["dt"])
            date_sh = JalaliDate(dt).strftime("%Y/%m/%d")
            desc = day["weather"][0]["description"].capitalize()
            temp_day = round(day["temp"]["day"], 1)
            hum = day["humidity"]
            wind = round(day["wind_speed"], 2)
            rain = day.get("rain", 0)

            message += f"""
🔹 {date_sh} – {desc}
   • 🌡️ دما: {temp_day}°C
   • 💧 رطوبت: {hum}%
   • 💨 سرعت باد: {wind} m/s
   • ☔ بارندگی: {rain} mm"""

        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"خطا در دریافت اطلاعات هواشناسی: {e}")


def get_wind_direction(degrees: int) -> str:
    dirs = [
        "شمال", "شمال‌شرق", "شرق", "جنوب‌شرق",
        "جنوب", "جنوب‌غرب", "غرب", "شمال‌غرب"
    ]
    idx = int((degrees + 22.5) / 45) % 8
    return dirs[idx]

def generate_daily_analysis(temp: float, wind: float) -> str:
    result = ""

    # ✈️ سفر
    result += "• ✈️ سفر به لاوان: شرایط عمومی هوا مناسب است.\n"

    # 🌊 دریا
    if wind <= 5:
        result += "• 🌊 دریا و ماهی‌گیری: وضعیت دریا آرام و مناسب است.\n"
    else:
        result += "• 🌊 دریا و ماهی‌گیری: وزش باد نسبتاً شدید است؛ احتیاط شود.\n"

    # 🤸‍♂️ ورزش
    if temp >= 35:
        result += "• 🤸‍♂️ ورزش در فضای باز: دما بالاست، فعالیت سنگین توصیه نمی‌شود.\n"
    else:
        result += "• 🤸‍♂️ ورزش در فضای باز: شرایط مناسب برای فعالیت فیزیکی.\n"

    # 🏝️ تفریح
    if temp >= 34:
        result += "• 🏝️ گردش و تفریح: در مناطق بدون سایه، استفاده از کلاه و کرم ضدآفتاب توصیه می‌شود."
    else:
        result += "• 🏝️ گردش و تفریح: هوای دلپذیر برای گشت‌وگذار در فضای باز."

    return result
