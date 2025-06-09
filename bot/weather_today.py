import requests
from datetime import datetime, timedelta
from persiantools.jdatetime import JalaliDate
import hijri_converter
from telegram import Update
from telegram.ext import ContextTypes

# مختصات جزیره لاوان
LAT = 26.7917
LON = 54.5125

# کلید API هواشناسی WeatherAPI.com
API_KEY = "5a1b0ee6907845879ff155659250906"

# تابع پردازش دکمه "هوای لاوان الان چطوره؟"
async def handle_weather_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={LAT},{LON}&days=6&lang=fa"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        current = data["current"]
        forecast_days = data["forecast"]["forecastday"]

        # اطلاعات وضعیت فعلی
        description = current["condition"]["text"]
        temperature = round(current["temp_c"], 1)
        humidity = current["humidity"]
        wind_kph = round(current["wind_kph"], 1)
        wind_dir_fa = translate_wind_direction(current["wind_dir"])
        pressure_mb = current["pressure_mb"]

        # تاریخ‌ها
        now = datetime.utcnow()
        date_miladi = now.strftime("%Y/%m/%d")
        date_shamsi = JalaliDate(now).strftime("%Y/%m/%d")
        date_ghamari = hijri_converter.Gregorian(now.year, now.month, now.day).to_hijri().isoformat()

        # تحلیل روزانه
        analysis = generate_daily_analysis(temperature, wind_kph / 3.6)  # تبدیل km/h به m/s برای تحلیل

        # ساخت پیام نهایی
        message = f"""🌤️ وضعیت فعلی هوای لاوان:

✅ توضیح: {description}
🌡️ دما: {temperature}°C
💧 رطوبت: {humidity}%
💨 باد: {wind_kph} km/h ({wind_dir_fa})
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

        # پیش بینی از روز بعد شروع می‌شود (رد کردن اولین روز که امروز است)
        for day in forecast_days[1:6]:
            date_jalali = JalaliDate(datetime.strptime(day["date"], "%Y-%m-%d")).strftime("%Y/%m/%d")
            weekday_fa = get_persian_weekday(datetime.strptime(day["date"], "%Y-%m-%d").weekday())
            desc = day["day"]["condition"]["text"]
            max_temp = round(day["day"]["maxtemp_c"], 1)
            min_temp = round(day["day"]["mintemp_c"], 1)
            humidity_day = day["day"]["avghumidity"]
            wind_day_kph = round(day["day"]["maxwind_kph"], 1)
            rain_mm = day["day"]["totalprecip_mm"]

            message += f"""
🔹 {date_jalali} ({weekday_fa}) – {desc}
   • 🌡️ بیشینه دما: {max_temp}°C، کمینه دما: {min_temp}°C
   • 💧 رطوبت: {humidity_day}%
   • 💨 سرعت باد: {wind_day_kph} km/h
   • ☔ بارندگی: {rain_mm} mm"""

        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"خطا در دریافت اطلاعات هواشناسی: {e}")

def translate_wind_direction(direction_en: str) -> str:
    mapping = {
        "N": "شمال",
        "NNE": "شمال‌شرق",
        "NE": "شمال‌شرق",
        "ENE": "شمال‌شرق",
        "E": "شرق",
        "ESE": "جنوب‌شرق",
        "SE": "جنوب‌شرق",
        "SSE": "جنوب‌شرق",
        "S": "جنوب",
        "SSW": "جنوب‌غرب",
        "SW": "جنوب‌غرب",
        "WSW": "جنوب‌غرب",
        "W": "غرب",
        "WNW": "شمال‌غرب",
        "NW": "شمال‌غرب",
        "NNW": "شمال‌غرب"
    }
    return mapping.get(direction_en, direction_en)

def get_persian_weekday(weekday_index: int) -> str:
    weekdays = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یک‌شنبه"]
    # توجه: در پایتون، دوشنبه=0، یکشنبه=6؛ اینجا ترتیب را بر اساس نیاز فارسی تنظیم کردیم
    return weekdays[weekday_index % 7]

def generate_daily_analysis(temp_c: float, wind_mps: float) -> str:
    result = ""

    # ✈️ سفر
    result += "• ✈️ سفر به لاوان: شرایط عمومی هوا مناسب است.\n"

    # 🌊 دریا
    if wind_mps <= 5:
        result += "• 🌊 دریا و ماهی‌گیری: وضعیت دریا آرام و مناسب است.\n"
    else:
        result += "• 🌊 دریا و ماهی‌گیری: وزش باد نسبتاً شدید است؛ احتیاط شود.\n"

    # 🤸‍♂️ ورزش
    if temp_c >= 35:
        result += "• 🤸‍♂️ ورزش در فضای باز: دما بالاست، فعالیت سنگین توصیه نمی‌شود.\n"
    else:
        result += "• 🤸‍♂️ ورزش در فضای باز: شرایط مناسب برای فعالیت فیزیکی.\n"

    # 🏝️ تفریح
    if temp_c >= 34:
        result += "• 🏝️ گردش و تفریح: در مناطق بدون سایه، استفاده از کلاه و کرم ضدآفتاب توصیه می‌شود."
    else:
        result += "• 🏝️ گردش و تفریح: هوای دلپذیر برای گشت‌وگذار در فضای باز."

    return result
