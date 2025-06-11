from pymongo import MongoClient
from bot.config import MONGO_URI, DATABASE_NAME

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# نمونه توابع برای کار با دیتابیس لوکیشن‌ها

def get_locations():
    return list(db.locations.find({}))

def get_location_by_id(loc_id):
    return db.locations.find_one({"id": loc_id})

def add_location(location_data):
    return db.locations.insert_one(location_data)

def update_location(loc_id, updated_data):
    return db.locations.update_one({"id": loc_id}, {"$set": updated_data})

def delete_location(loc_id):
    return db.locations.delete_one({"id": loc_id})
