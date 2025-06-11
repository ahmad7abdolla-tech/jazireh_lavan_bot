# bot/database.py
import sqlite3

DB = sqlite3.connect('lavan.db', check_same_thread=False)
DB.execute("""
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    photo_id TEXT NOT NULL
)
""")
DB.commit()
