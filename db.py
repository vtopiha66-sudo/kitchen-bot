import aiosqlite

DB = "db.sqlite"

async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            lang TEXT DEFAULT 'ua'
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS products (
            name TEXT PRIMARY KEY,
            stock REAL,
            min REAL
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS dishes (
            name TEXT PRIMARY KEY
        )
        """)

        await db.commit()
