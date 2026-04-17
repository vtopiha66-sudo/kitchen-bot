from db import DB
import aiosqlite

async def get_stock():
    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute("SELECT name, stock FROM products")
        return await cursor.fetchall()

async def add_sale():
    # пока просто заглушка
    return "OK"

async def check_deficit():
    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute(
            "SELECT name FROM products WHERE stock <= min"
        )
        return await cursor.fetchall()
