import os

# تنظیمات دیتابیس
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "lavan_island")

# محدودیت‌ها
MAX_IMAGE_SIZE_MB = 5  # حداکثر حجم تصاویر بر حسب مگابایت

# توکن ربات تلگرام
TELEGRAM_BOT_TOKEN = "7586578372:AAEIkVr4Wq23NSkLuSPRl1yqboqd7_cW0ac"

# سطح لاگینگ
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
