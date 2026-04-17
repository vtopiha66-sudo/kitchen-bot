import aiosqlite

DB = "kitchen.db"

async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            amount REAL
        )
        """)
        await db.commit()


async def get_stock():
    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute("SELECT name, amount FROM stock")
        return await cursor.fetchall()


async def add_product(name, amount):
    async with aiosqlite.connect(DB) as db:
        await db.execute("INSERT INTO stock (name, amount) VALUES (?, ?)", (name, amount))
        await db.commit()


async def update_stock(name, amount):
    async with aiosqlite.connect(DB) as db:
        await db.execute("UPDATE stock SET amount = amount + ? WHERE name = ?", (amount, name))
        await db.commit()