import requests
from persiantools.jdatetime import JalaliDate
from datetime import datetime
from hijri_converter import convert

# --- تابع تبدیل جهت باد به فارسی ---
def convert_wind_direction(direction):
    mapping = {
        "N": "شمال", "NE": "شمال‌شرق", "E": "شرق", "SE": "جنوب‌شرق",
        "S": "جنوب", "SW": "جنوب‌غرب", "W": "غرب", "NW": "شمال‌غرب",
        "NNE": "شمال شمال‌شرق", "ENE": "شرق شمال‌شرق", "ESE": "شرق جنوب‌شرق",
        "SSE": "جنوب جنوب‌شرق", "SSW": "جنوب جنوب‌غرب", "WSW": "غرب جنوب‌غرب",
        "WNW": "غرب شمال‌غرب", "NNW": "شمال شمال‌غرب"
    }
    return mapping.get(direction, direction)

# --- تابع ترجمه وضعیت آب‌وهوا به فارسی ---
def translate_condition(condition):
    translations = {
        "Sunny": "آفتابی",
        "Clear": "صاف",
        "Partly cloudy": "نیمه‌ابری",
        "Cloudy": "ابری",
        "Overcast": "تمام‌ابری",
        "Mist": "مه",
        "Patchy rain possible": "احتمال بارش پراکنده",
        "Light rain": "باران سبک",
        "Moderate rain": "باران متوسط",
        "Heavy rain": "باران شدید",
        "Thunderstorm": "طوفان رعدوبرق",
        # موارد دیگر در صورت نیاز اضافه شود
    }
    return translations.get(condition, condition)

# --- تابع تبدیل شماره هفته به نام فارسی ---
def get_day_name_fa(weekday_number):
    names = ["دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یک‌شنبه"]
    return names[weekday_number % 7]

# --- تابع تحلیل روزانه ---
def generate_daily_advice(current):
    advice = ""
    temp = current["temp_c"]
    wind = current["wind_kph"]
    condition = current["condition"]["text"]
    humidity = current["humidity"]

    # ✈️ سفر به لاوان
    if temp >= 15 and temp <= 40 and "rain" not in condition.lower():
        advice += "• ✈️ سفر به لاوان: شرایط عمومی هوا مناسب است.\n"
    else:
        advice += "• ✈️ سفر به لاوان: شرایط سفر ممکن است چالش‌برانگیز باشد.\n"

    # 🌊 دریا و ماهی‌گیری
    if wind <= 20:
        advice += "• 🌊 دریا و ماهی‌گیری: وضعیت دریا آرام و مناسب است.\n"
    else:
        advice += "• 🌊 دریا و ماهی‌گیری: احتمال مواج بودن دریا وجود دارد.\n"

    # 🤸‍♂️ ورزش در فضای باز
    if humidity < 70 and temp <= 35:
        advice += "• 🤸‍♂️ ورزش در فضای باز: شرایط مناسب برای فعالیت فیزیکی.\n"
    else:
        advice += "• 🤸‍♂️ ورزش در فضای باز: توصیه به احتیاط در انجام فعالیت‌ها.\n"

    # 🏝️ گردش و تفریح
    if "rain" not in condition.lower() and temp <= 38:
        advice += "• 🏝️ گردش و تفریح: هوای دلپذیر برای گشت‌وگذار در فضای باز.\n"
    else:
        advice += "• 🏝️ گردش و تفریح: بهتر است برنامه تفریحی را با احتیاط تنظیم کنید.\n"

    return advice

# --- دریافت اطلاعات آب‌وهوا ---
WEATHER_API_KEY = "31cd3332815266315f25a40e56962a52"
BASE_URL = "http://api.weatherapi.com/v1/forecast.json"

def get_weather_forecast():
    params = {
        "key": WEATHER_API_KEY,
        "q": "Lavan Island",
        "days": 6,
        "lang": "en",
        "aqi": "no",
        "alerts": "no"
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()

    current = data["current"]
    forecast_days = data["forecast"]["forecastday"]

    today = datetime.today()
    today_jalali = JalaliDate.today()
    today_hijri = convert.Gregorian(today.year, today.month, today.day).to_hijri()

    condition_text = translate_condition(current["condition"]["text"])
    wind_dir_fa = convert_wind_direction(current["wind_dir"])

    message = f"🌤️ وضعیت فعلی هوای لاوان:\n\n"
    message += f"✅ توضیح: {condition_text}\n"
    message += f"🌡️ دما: {current['temp_c']}°C\n"
    message += f"💧 رطوبت: {current['humidity']}%\n"
    message += f"💨 باد: {current['wind_kph']} km/h ({wind_dir_fa})\n"
    message += f"🔽 فشار هوا: {current['pressure_mb']} hPa\n"

    message += "\n──────────────\n\n"

    message += f"📆 تاریخ:\n"
    message += f"🔹 شمسی: {today_jalali}\n"
    message += f"🔹 قمری: {today_hijri}\n"
    message += f"🔹 میلادی: {today.strftime('%Y/%m/%d')}\n"

    message += "\n──────────────\n\n"

    message += "🧭 تحلیل روزانه:\n"
    message += generate_daily_advice(current)

    message += "\n──────────────\n\n"

    message += "📈 پیش‌بینی پنج روز آینده:\n"
    for i in range(1, 6):
        forecast = forecast_days[i]
        date_obj = datetime.strptime(forecast['date'], "%Y-%m-%d")
        jalali_date = JalaliDate(date_obj)
        day_name_fa = get_day_name_fa(date_obj.weekday())

        condition = translate_condition(forecast['day']['condition']['text'])
        max_temp = forecast['day']['maxtemp_c']
        min_temp = forecast['day']['mintemp_c']
        humidity = forecast['day']['avghumidity']
        wind_kph = forecast['day']['maxwind_kph']
        rain_mm = forecast['day']['totalprecip_mm']

        message += f"🔹 {jalali_date} ({day_name_fa}) – {condition}\n"
        message += f"   • 🌡️ بیشینه دما: {max_temp}°C، کمینه دما: {min_temp}°C\n"
        message += f"   • 💧 رطوبت: {humidity}%\n"
        message += f"   • 💨 سرعت باد: {wind_kph} km/h\n"
        message += f"   • ☔ بارندگی: {rain_mm} mm\n"

    return message

# --- هندلر نهایی ---
def handle_weather_today():
    try:
        return get_weather_forecast()
    except Exception as e:
        return f"خطا در دریافت اطلاعات هواشناسی: {str(e)}"
