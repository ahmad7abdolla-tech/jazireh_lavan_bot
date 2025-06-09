import requests
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, CallbackQueryHandler

BOT_TOKEN = "7586578372:AAGlPQ7tNVs4-FxaHatLH8oZjSpPOSZzCsM"
API_KEY = "31cd3332815266315f25a40e56962a52"
LAT = 26.7917
LON = 54.5125

def get_current_weather():
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric&lang=fa"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def get_forecast():
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric&lang=fa"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def format_date(dt: datetime):
    # شمسی - قمری تاریخ ساده می‌سازیم فقط میلادی اینجا موجود است
    shamsi = dt.strftime("%Y/%m/%d")  # به صورت میلادی نمایش می‌دیم (نیاز به تبدیل شمسی جداگانه دارد)
    qamari = "1446/12/13"  # عدد ثابت فعلاً (برای ساده سازی)
    miladi = dt.strftime("%Y/%m/%d")
    return shamsi, qamari, miladi

def analyze_weather(description, temp, humidity, wind_speed):
    # تحلیل ساده و بدون حساسیت زیاد
    travel = "شرایط عمومی هوا مناسب است."
    if "ریزگرد" in description or "گرد و خاک" in description:
        travel = "به‌دلیل وجود ریزگرد برای افراد با بیماری‌های تنفسی توصیه نمی‌شود."

    sea = "وضعیت دریا آرام و مناسب است."
    if wind_speed > 6:
        sea = "باد شدید است، دریا برای ماهی‌گیری و قایق‌سواری مناسب نیست."

    sport = "فعالیت سبک در فضای باز مناسب است."
    if temp > 35:
        sport = "دما بالاست، فعالیت سنگین توصیه نمی‌شود."

    tourism = "آب‌وهوا برای گردش و تفریح مناسب است."
    if temp > 35:
        tourism = "در مناطق بدون سایه، استفاده از کلاه و کرم ضدآفتاب توصیه می‌شود."

    return f"• ✈️ سفر به لاوان: {travel}\n" \
           f"• 🌊 دریا و ماهی‌گیری: {sea}\n" \
           f"• 🤸‍♂️ ورزش در فضای باز: {sport}\n" \
           f"• 🏝️ گردش و تفریح: {tourism}"

def build_message():
    try:
        current = get_current_weather()
        forecast = get_forecast()

        # استخراج اطلاعات وضعیت فعلی
        desc = current['weather'][0]['description']
        temp = current['main']['temp']
        humidity = current['main']['humidity']
        wind_speed = current['wind']['speed']
        wind_deg = current['wind'].get('deg', 0)
        pressure = current['main']['pressure']

        # تبدیل جهت باد به متن
        def wind_direction(deg):
            dirs = ["شمال", "شمال‌شرق", "شرق", "جنوب‌شرق", "جنوب", "جنوب‌غرب", "غرب", "شمال‌غرب"]
            ix = int((deg + 22.5) / 45) % 8
            return dirs[ix]
        wind_dir_text = wind_direction(wind_deg)

        # تاریخ‌ها
        now = datetime.utcnow() + timedelta(hours=3.5)  # تهران +3:30 ساعت
        shamsi, qamari, miladi = format_date(now)

        # تحلیل روزانه
        analysis = analyze_weather(desc, temp, humidity, wind_speed)

        # پیام وضعیت فعلی
        msg = f"🌤️ وضعیت فعلی هوای لاوان:\n\n" \
              f"✅ توضیح: {desc}\n" \
              f"🌡️ دما: {temp:.1f}°C\n" \
              f"💧 رطوبت: {humidity}%\n" \
              f"💨 باد: {wind_speed:.2f} m/s ({wind_dir_text})\n" \
              f"🔽 فشار هوا: {pressure} hPa\n\n" \
              f"──────────────\n\n" \
              f"📆 تاریخ:\n" \
              f"🔹 شمسی: {shamsi}\n" \
              f"🔹 قمری: {qamari}\n" \
              f"🔹 میلادی: {miladi}\n\n" \
              f"──────────────\n\n" \
              f"🧭 تحلیل روزانه:\n{analysis}\n\n" \
              f"──────────────\n\n" \
              f"📈 پیش‌بینی پنج روز آینده:\n"

        # استخراج پیش‌بینی 5 روزه (هر 8 داده 3 ساعته یک روز است، میانگین ساده)
        forecast_list = forecast['list']
        daily_forecast = {}
        for item in forecast_list:
            dt_txt = item['dt_txt']  # "2025-06-09 12:00:00"
            date = dt_txt.split(" ")[0]
            if date not in daily_forecast:
                daily_forecast[date] = []
            daily_forecast[date].append(item)

        dates = sorted(daily_forecast.keys())[:5]

        for date in dates:
            day_items = daily_forecast[date]
            # محاسبه میانگین دما، رطوبت، سرعت باد، بارش
            temps = [i['main']['temp'] for i in day_items]
            humidities = [i['main']['humidity'] for i in day_items]
            winds = [i['wind']['speed'] for i in day_items]
            rains = []
            for i in day_items:
                rain = i.get('rain', {}).get('3h', 0)
                rains.append(rain)
            avg_temp = sum(temps) / len(temps)
            avg_humidity = sum(humidities) / len(humidities)
            avg_wind = sum(winds) / len(winds)
            total_rain = sum(rains)

            # توضیح وضعیت کلی هوا از اولین داده روز
            desc_day = day_items[0]['weather'][0]['description']

            # تبدیل تاریخ به شمسی و روز هفته (ساده با میلادی)
            dt_obj = datetime.strptime(date, "%Y-%m-%d")
            day_week = dt_obj.strftime("%A")  # انگلیسی
            # تبدیل انگلیسی به فارسی روز هفته:
            days_fa = {
                "Saturday": "شنبه",
                "Sunday": "یک‌شنبه",
                "Monday": "دوشنبه",
                "Tuesday": "سه‌شنبه",
                "Wednesday": "چهارشنبه",
                "Thursday": "پنج‌شنبه",
                "Friday": "جمعه"
            }
            day_week_fa = days_fa.get(day_week, day_week)
            shamsi_date = dt_obj.strftime("%Y/%m/%d")  # شمسی ساده (بدون کتابخانه)

            msg += f"🔹 {day_week_fa} {shamsi_date} – {desc_day}\n" \
                   f"   • 🌡️ دما: {avg_temp:.1f}°C\n" \
                   f"   • 💧 رطوبت: {avg_humidity:.0f}%\n" \
                   f"   • 💨 سرعت باد: {avg_wind:.2f} m/s\n" \
                   f"   • ☔ بارندگی: {total_rain:.1f} mm\n\n"

        return msg
    except Exception as e:
        return f"خطا در دریافت اطلاعات هواشناسی: {e}"

async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("🌦️ هوای لاوان الان چطوره؟", callback_data='weather_now')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("سلام! من ربات اطلاعات جزیره لاوان هستم.\nبرای دریافت اطلاعات هواشناسی روی دکمه زیر کلیک کنید.", reply_markup=reply_markup)

async def button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    if query.data == 'weather_now':
        msg = build_message()
        await query.edit_message_text(msg, parse_mode='Markdown')

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    print("ربات در حال اجراست...")
    app.run_polling()

if __name__ == "__main__":
    main()
