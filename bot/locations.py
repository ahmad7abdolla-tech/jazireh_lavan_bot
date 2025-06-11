# bot/locations.py
from bot.admins import is_admin
from bot.google_drive import upload_image

locations = []

def add_location(admin_id: int, name: str, photo_path: str):
    if not is_admin(admin_id):
        return False
    
    photo_url = upload_image(photo_path)
    locations.append({"name": name, "photo": photo_url})
    return True

def get_locations():
    return locations
