# bot/google_drive.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

# تنظیمات کلید API
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service-account.json'  # فایل کلید از گوگل

def upload_image(file_path: str) -> str:
    """آپلود عکس به گوگل درایو و بازگرداندن لینک عمومی"""
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    
    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, mimetype='image/jpeg')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    
    # تنظیم دسترسی عمومی
    service.permissions().create(fileId=file['id'], body={'type': 'anyone', 'role': 'reader'}).execute()
    return f"https://drive.google.com/uc?id={file['id']}"
