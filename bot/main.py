import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime
from persiantools.jdatetime import JalaliDate
from hijri_converter import Gregorian

# توکن ربات و کلید API هواشناسی
TELEGRAM_TOKEN = "7586578372:AAGlPQ7tNVs4-FxaHatLH8oZjSpPOSZzCsM"
OPENWEATHER_API_KEY = "31cd3332815266315f25a40e56962a52"

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# مختصات جزیره لاوان
LAT = 26.7917
LON = 54.5125

def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={LAT}&lon={LON}&appid={OPENWEATHER_API_KEY}&units=metric&lang=fa"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def format_date():
    now = datetime.now()
    persian_date = JalaliDate(now)
    persian_str = persian_date.strftime("%Y/%m/%d")
    hijri_date = Gregorian(now.year, now.month, now.day).to_hijri()
    hijri_str = f"{hijri_date.year}-{hijri_date.month:02d}-{hijri_date.day:02d}"
    gregorian_str = now.strftime("%Y/%m/%d")
    return persian_str, hijri_str, gregorian_str

def wind_direction(deg):
    directions = ['شمال', 'شمال‌شرقی', 'شرق', 'جنوب‌شرقی', 'جنوب', 'جنوب‌غربی', 'غرب', 'شمال‌غربی']
    idx = int((deg + 22.5) // 45) % 8
    return directions[idx]

def daily_analysis(weather_desc, temp, wind_speed):
    # تحلیل ساده و بدون حساسیت زیاد با 4 بخش
    travel = "شرایط عمومی هوا مناسب است."
    sea = "وضعیت دریا آرام است."
    sport = "فعالیت سبک در فضای باز مناسب است."
    tourism = "آب‌وهوا پایدار و قابل قبول است."

    # با کمی منطق ساده (می‌توان پیشرفته‌تر کرد)
    desc = weather_desc.lower()

    if "ریزگرد" in desc or "گرد و خاک" in desc:
        travel = "به‌دلیل وجود ریزگرد برای افراد حساس توصیه نمی‌شود."
        tourism = "استفاده از ماسک و محافظت توصیه می‌شود."
    if wind_speed > 7:
        sea = "سرعت باد زیاد است، شرایط مناسبی برای ماهی‌گیری نیست."
        sport = "ورزش سنگین توصیه نمی‌شود."
    if temp > 30:
        sport = "به‌دلیل دمای بالا، فعالیت سبک در صبح یا عصر مناسب‌تر است."
    if "باران" in desc:
        tourism = "احتمال بارش وجود دارد، برنامه‌ریزی را به‌دقت انجام دهید."

    return f"""\
• ✈️ *سفر به لاوان:* {travel}
• 🌊 *ماهی‌گیری یا دریا:* {sea}
• 🤸‍♂️ *ورزش در فضای باز:* {sport}
• 🏝️ *گردش و تفریح:* {tourism}"""

def build_weather_message(data):
    current = data['current']
    persian_date, hijri_date, gregorian_date = format_date()

    weather_desc = current['weather'][0]['description'].capitalize()
    temp = current['temp']
    humidity = current['humidity']
    wind_speed = current['wind_speed']
    wind_deg = current.get('wind_deg', 0)
    pressure = current['pressure']

    wind_dir = wind_direction(wind_deg)

    analysis_text = daily_analysis(weather_desc, temp, wind_speed)

    # پیش‌بینی پنج روز آینده
    daily = data['daily'][:5]
    forecast_lines = []
    for day in daily:
        dt = datetime.fromtimestamp(day['dt'])
        persian_day = JalaliDate(dt).strftime("%Y/%m/%d")
        desc = day['weather'][0]['description'].capitalize()
        temp_day = day['temp']['day']
        humidity_day = day['humidity']
        wind_day = day['wind_speed']
        rain = day.get('rain', 0)
        line = (
            f"🔹 {persian_day} – {desc}\n"
            f"   • 🌡️ دما: {temp_day:.1f}°C\n"
            f"   • 💧 رطوبت: {humidity_day}%\n"
            f"   • 💨 سرعت باد: {wind_day:.2f} m/s\n"
            f"   • ☔ بارندگی: {rain} mm"
        )
        forecast_lines.append(line)

    forecast_text = "\n\n".join(forecast_lines)

    message = (
        f"🌤️ *وضعیت فعلی هوای لاوان:*\n\n"
        f"✅ توضیح: {weather_desc}\n"
        f"🌡️ دما: {temp:.2f}°C\n"
        f"💧 رطوبت: {humidity}%\n"
        f"💨 باد: {wind_speed:.2f} m/s ({wind_dir})\n"
        f"🔽 فشار هوا: {pressure} hPa\n\n"
        f"──────────────\n\n"
        f"📆 *تاریخ:*\n"
        f"🔹 شمسی: {persian_date}\n"
        f"🔹 قمری: {hijri_date}\n"
        f"🔹 میلادی: {gregorian_date}\n\n"
        f"──────────────\n\n"
        f"🧭 *تحلیل روزانه:*\n"
        f"{analysis_text}\n\n"
        f"──────────────\n\n"
        f"📈 *پیش‌بینی پنج روز آینده:*\n"
        f"{forecast_text}"
    )
    return message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌦️ هوای لاوان الان چطوره؟", callback_data='weather')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! من ربات اطلاعات جزیره لاوان هستم. یکی از گزینه‌ها را انتخاب کنید:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'weather':
        try:
            data = get_weather()
            message = build_weather_message(data)
            await query.edit_message_text(text=message, parse_mode='Markdown')
        except Exception as e:
            await query.edit_message_text(text=f"خطا در دریافت اطلاعات هواشناسی: {e}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == '__main__':
    main()
