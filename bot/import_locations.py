import json
from pymongo import MongoClient
from bot.config import MONGO_URI, DATABASE_NAME

# اتصال به دیتابیس
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# مسیر فایل JSON
with open("bot/locations.json", "r", encoding="utf-8") as file:
    locations = json.load(file)

# وارد کردن داده‌ها
for loc in locations:
    if db.locations.find_one({"id": loc["id"]}):
        print(f"⏭ لوکیشن {loc['id']} از قبل وجود دارد، رد شد.")
    else:
        db.locations.insert_one(loc)
        print(f"✅ لوکیشن {loc['id']} با موفقیت اضافه شد.")
