import os

# توکن ربات تلگرام
BOT_TOKEN = "7586578372:AAEIkVr4Wq23NSkLuSPRl1yqboqd7_cW0ac"

# تنظیمات دیتابیس (MongoDB)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = "lavan_island"

# محدودیت‌ها
MAX_IMAGE_SIZE_MB = 1000  # حداکثر حجم تصاویر به مگابایت
