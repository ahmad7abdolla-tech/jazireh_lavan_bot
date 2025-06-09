import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

BOT_TOKEN = "7586578372:AAGlPQ7tNVs4-FxaHatLH8oZjSpPOSZzCsM"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# --- داده نمونه هواشناسی (برای تست) ---
sample_weather_data = {
    "current": {
        "description": "آسمان صاف",
        "temp": 35.0,
        "humidity": 49,
        "wind_speed": 2.37,
        "wind_dir": "غرب",
        "pressure": 1005,
        "date": {
            "shamsi": "1404/03/20",
            "qomari": "1446/12/13",
            "miladi": "2025/06/09"
        }
    },
    "forecast": [
        {"date": "دوشنبه 1404/03/20", "desc": "آسمان صاف", "temp": 35.0, "humidity": 49, "wind_speed": 2.37, "rain": 0},
        {"date": "سه شنبه 1404/03/21", "desc": "آسمان صاف", "temp": 31.6, "humidity": 57, "wind_speed": 4.16, "rain": 0},
        {"date": "چهارشنبه 1404/03/22", "desc": "آسمان صاف", "temp": 32.1, "humidity": 57, "wind_speed": 1.81, "rain": 0},
        {"date": "پنجشنبه 1404/03/23", "desc": "آسمان صاف", "temp": 31.4, "humidity": 58, "wind_speed": 3.43, "rain": 0},
        {"date": "جمعه 1404/03/24", "desc": "آسمان صاف", "temp": 31.3, "humidity": 66, "wind_speed": 6.24, "rain": 0},
    ]
}

def prepare_weather_message(data):
    cur = data["current"]
    fcs = data["forecast"]

    msg = (
        f"🌤️ وضعیت فعلی هوای لاوان:\n\n"
        f"✅ توضیح: {cur['description']}\n"
        f"🌡️ دما: {cur['temp']}°C\n"
        f"💧 رطوبت: {cur['humidity']}%\n"
        f"💨 باد: {cur['wind_speed']} m/s ({cur['wind_dir']})\n"
        f"🔽 فشار هوا: {cur['pressure']} hPa\n\n"
        f"──────────────\n\n"
        f"📆 تاریخ:\n"
        f"🔹 شمسی: {cur['date']['shamsi']}\n"
        f"🔹 قمری: {cur['date']['qomari']}\n"
        f"🔹 میلادی: {cur['date']['miladi']}\n\n"
        f"──────────────\n\n"
        f"📈 پیش‌بینی پنج روز آینده:\n"
    )

    for day in fcs:
        msg += (
            f"🔹 {day['date']} – {day['desc']}\n"
            f"   • 🌡️ دما: {day['temp']}°C\n"
            f"   • 💧 رطوبت: {day['humidity']}%\n"
            f"   • 💨 سرعت باد: {day['wind_speed']} m/s\n"
            f"   • ☔ بارندگی: {day['rain']} mm\n\n"
        )
    return msg.strip()


def send_telegram_message(chat_id, text):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    r = requests.post(url, data=payload)
    return r.json()


@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    update = request.get_json()

    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        if text == "🌦️ هوای لاوان الان چطوره؟":
            weather_message = prepare_weather_message(sample_weather_data)
            send_telegram_message(chat_id, weather_message)
        else:
            send_telegram_message(chat_id, "سلام! لطفاً یکی از دکمه‌های موجود را انتخاب کنید.")

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(port=8443)
