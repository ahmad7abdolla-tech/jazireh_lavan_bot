import os

# تنظیمات دیتابیس
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DATABASE_NAME = "lavan_island"

# محدودیت‌ها
MAX_IMAGE_SIZE_MB = 5  # حداکثر حجم تصاویر بر حسب مگابایت
