import os
from typing import List, Dict, Optional
from telegram import File
from bson import ObjectId
from config import MONGO_URI
import motor.motor_asyncio

# اتصال به دیتابیس MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client.lavan_island
locations_collection = db.locations

class Database:
    @staticmethod
    async def add_location(location_data: Dict) -> str:
        """افزودن لوکیشن جدید به دیتابیس"""
        try:
            result = await locations_collection.insert_one(location_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error adding location: {e}")
            raise

    @staticmethod
    async def get_locations() -> List[Dict]:
        """دریافت لیست تمام لوکیشن‌ها"""
        try:
            locations = []
            async for loc in locations_collection.find({}):
                loc['_id'] = str(loc['_id'])
                locations.append(loc)
            return locations
        except Exception as e:
            print(f"Error getting locations: {e}")
            return []

    @staticmethod
    async def get_location(location_id: str) -> Optional[Dict]:
        """دریافت جزئیات یک لوکیشن"""
        try:
            loc = await locations_collection.find_one({"_id": ObjectId(location_id)})
            if loc:
                loc['_id'] = str(loc['_id'])
                return loc
            return None
        except Exception as e:
            print(f"Error getting location: {e}")
            return None

    @staticmethod
    async def update_location(location_id: str, update_data: Dict) -> bool:
        """به‌روزرسانی اطلاعات لوکیشن"""
        try:
            result = await locations_collection.update_one(
                {"_id": ObjectId(location_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating location: {e}")
            return False

    @staticmethod
    async def delete_location(location_id: str) -> bool:
        """حذف لوکیشن از دیتابیس"""
        try:
            result = await locations_collection.delete_one({"_id": ObjectId(location_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting location: {e}")
            return False
