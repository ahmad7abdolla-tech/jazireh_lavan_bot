import requests
from persiantools.jdatetime import JalaliDate
from datetime import datetime
from hijri_converter import convert
from utils.convert_wind import convert_wind_direction
from utils.weather_advice import generate_daily_advice
from utils.weather_condition_translate import translate_condition
from utils.day_name import get_day_name_fa

WEATHER_API_KEY = "5a1b0ee6907845879ff155659250906"
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


def handle_weather_today():
    try:
        return get_weather_forecast()
    except Exception as e:
        return f"خطا در دریافت اطلاعات هواشناسی: {str(e)}"
