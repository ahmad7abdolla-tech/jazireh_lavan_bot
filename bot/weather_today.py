import requests
from datetime import datetime
from persiantools.jdatetime import JalaliDate
import hijri_converter
from telegram import Update
from telegram.ext import ContextTypes

API_KEY = "5a1b0ee6907845879ff155659250906"
LAT = 26.7917
LON = 54.5125

async def handle_weather_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = "http://api.weatherapi.com/v1/forecast.json"
        params = {
            "key": API_KEY,
            "q": f"{LAT},{LON}",
            "days": 5,
            "lang": "fa",
            "aqi": "no",
            "alerts": "no"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        current = data["current"]
        forecast_days = data["forecast"]["forecastday"]

        # اطلاعات وضعیت فعلی
        condition = current["condition"]["text"]
        temperature = current["temp_c"]
        humidity = current["humidity"]
        wind_kph = current["wind_kph"]
        wind_dir = current["wind_dir"]
        pressure_mb = current["pressure_mb"]

        # تاریخ‌ها
        now = datetime.strptime(current["last_updated"], "%Y-%m-%d %H:%M")
        date_miladi = now.strftime("%Y/%m/%d")
        date_shamsi = JalaliDate(now).strftime("%Y/%m/%d")
        date_ghamari = hijri_converter.Gregorian(now.year, now.month, now.day).to_hijri().isoformat()

        # تحلیل روزانه (می‌تونیم تغییر بدیم یا نگه داریم)
        analysis = generate_daily_analysis(temperature, wind_kph)

        # ساخت پیام نهایی
        message = f"""🌤️ وضعیت فعلی هوای لاوان:

✅ توضیح: {condition}
🌡️ دما: {temperature}°C
💧 رطوبت: {humidity}%
💨 باد: {wind_kph} km/h ({wind_dir})
🔽 فشار هوا: {pressure_mb} hPa

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

        for day in forecast_days:
            date_obj = datetime.strptime(day["date"], "%Y-%m-%d")
            date_sh = JalaliDate(date_obj).strftime("%Y/%m/%d")
            day_condition = day["day"]["condition"]["text"]
            max_temp = day["day"]["maxtemp_c"]
            min_temp = day["day"]["mintemp_c"]
            humidity = day["day"]["avghumidity"]
            wind_kph = day["day"]["maxwind_kph"]
            rain_mm = day["day"]["totalprecip_mm"]

            message += f"""
🔹 {date_sh} – {day_condition}
   • 🌡️ بیشینه دما: {max_temp}°C، کمینه دما: {min_temp}°C
   • 💧 رطوبت متوسط: {humidity}%
   • 💨 سرعت باد: {wind_kph} km/h
   • ☔ بارندگی: {rain_mm} mm"""

        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"خطا در دریافت اطلاعات هواشناسی: {e}")


def generate_daily_analysis(temp: float, wind_kph: float) -> str:
    result = ""

    # ✈️ سفر
    result += "• ✈️ سفر به لاوان: شرایط عمومی هوا مناسب است.\n"

    # 🌊 دریا
    if wind_kph <= 20:
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
