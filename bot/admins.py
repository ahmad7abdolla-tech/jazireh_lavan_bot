# bot/admins.py
ADMINS = [
    6251969541,  # احمد
    987654321   # آی دی ادمین دوم (بعداً اضافه می‌کنید)
]

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS
