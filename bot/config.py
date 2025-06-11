import os

# توکن ربات
BOT_TOKEN = "7586578372:AAEIkVr4Wq23NSkLuSPRl1yqboqd7_cW0ac"

# تنظیمات دیتابیس MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = "lavan_island"

# محدودیت‌ها
MAX_IMAGE_SIZE_MB = 1000  # حداکثر حجم مجاز تصاویر به مگابایت

# ساختار پوشه ذخیره تصاویر (در Telegram File API فقط file_id ذخیره می‌شود، نه فایل فیزیکی)
USE_TELEGRAM_FILE_API = True  # ذخیره فقط file_id به‌جای لینک مستقیم یا آدرس گوگل‌درایو
