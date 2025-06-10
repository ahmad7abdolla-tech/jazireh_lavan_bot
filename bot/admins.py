# bot/locations/admins.py

# لیست ID ادمین‌ها (شناسه عددی تلگرام)
ADMINS = [
    367118717,  # احمد
    987654321,
    111222333,
    444555666,
    777888999
]

def is_admin(user_id: int) -> bool:
    """بررسی اینکه کاربر ادمین هست یا نه"""
    return user_id in ADMINS
