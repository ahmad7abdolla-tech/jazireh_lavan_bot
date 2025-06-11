import os
import json
from typing import List, Dict, Optional
from telegram import File, PhotoSize
import motor.motor_asyncio
from bson import ObjectId
from config import MONGO_URI, MAX_IMAGE_SIZE_MB

# اتصال به دیتابیس MongoDB
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client.lavan_island
locations_collection = db.locations
images_collection = db.images

class Database:
    @staticmethod
    async def save_image(file: File, caption: str = "") -> str:
        """ذخیره تصویر در MongoDB با GridFS"""
        try:
            # دریافت فایل از تلگرام
            image_data = await file.download_as_bytearray()
            
            # بررسی حجم تصویر
            if len(image_data) > MAX_IMAGE_SIZE_MB * 1024 * 1024:
                raise ValueError(f"حجم تصویر نباید بیشتر از {MAX_IMAGE_SIZE_MB} مگابایت باشد")
            
            # ذخیره در GridFS
            fs = motor.motor_asyncio.AsyncIOMotorGridFSBucket(db)
            file_id = await fs.upload_from_stream(
                filename=file.file_id,
                source=bytes(image_data),
                metadata={"caption": caption}
            )
            
            return str(file_id)
        except Exception as e:
            print(f"Error saving image: {e}")
            raise

    @staticmethod
    async def get_image(file_id: str) -> bytes:
        """دریافت تصویر از دیتابیس"""
        try:
            fs = motor.motor_asyncio.AsyncIOMotorGridFSBucket(db)
            grid_out = await fs.open_download_stream(ObjectId(file_id))
            return await grid_out.read()
        except Exception as e:
            print(f"Error getting image: {e}")
            raise

    @staticmethod
    async def add_location(location_data: Dict) -> str:
        """افزودن لوکیشن جدید به دیتابیس"""
        try:
            # تبدیل file_idهای تصاویر به ObjectId
            if 'images' in location_data:
                location_data['images'] = [ObjectId(img_id) for img_id in location_data['images']]
            
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
                if 'images' in loc:
                    loc['images'] = [str(img_id) for img_id in loc['images']]
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
                if 'images' in loc:
                    loc['images'] = [str(img_id) for img_id in loc['images']]
                return loc
            return None
        except Exception as e:
            print(f"Error getting location: {e}")
            return None

    @staticmethod
    async def update_location(location_id: str, update_data: Dict) -> bool:
        """به‌روزرسانی اطلاعات لوکیشن"""
        try:
            if 'images' in update_data:
                update_data['images'] = [ObjectId(img_id) for img_id in update_data['images']]
            
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
            # ابتدا تصاویر مرتبط را پیدا می‌کنیم
            loc = await locations_collection.find_one({"_id": ObjectId(location_id)})
            if loc and 'images' in loc:
                # حذف تصاویر از GridFS
                fs = motor.motor_asyncio.AsyncIOMotorGridFSBucket(db)
                for img_id in loc['images']:
                    await fs.delete(ObjectId(img_id))
            
            # حذف خود لوکیشن
            result = await locations_collection.delete_one({"_id": ObjectId(location_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting location: {e}")
            return False
