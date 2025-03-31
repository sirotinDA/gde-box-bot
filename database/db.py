import os
import aiosqlite

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "storage.db"))

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS boxes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                photo TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        await db.commit()
