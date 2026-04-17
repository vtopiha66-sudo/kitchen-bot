import aiosqlite

DB = "kitchen.db"


# ✅ создание базы
async def init_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            amount REAL DEFAULT 0
        )
        """)
        await db.commit()


# ✅ получить весь склад
async def get_stock():
    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute(
            "SELECT name, amount FROM stock ORDER BY name"
        )
        return await cursor.fetchall()


# ✅ добавить или обновить продукт
async def update_stock(name, amount):
    name = name.lower().strip()

    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute(
            "SELECT amount FROM stock WHERE name = ?", (name,)
        )
        row = await cursor.fetchone()

        if row:
            await db.execute(
                "UPDATE stock SET amount = amount + ? WHERE name = ?",
                (amount, name)
            )
        else:
            await db.execute(
                "INSERT INTO stock (name, amount) VALUES (?, ?)",
                (name, amount)
            )

        await db.commit()


# ✅ списание (минус со склада)
async def remove_stock(name, amount):
    name = name.lower().strip()

    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute(
            "SELECT amount FROM stock WHERE name = ?", (name,)
        )
        row = await cursor.fetchone()

        if not row:
            return False  # нет продукта

        if row[0] < amount:
            return False  # недостаточно

        await db.execute(
            "UPDATE stock SET amount = amount - ? WHERE name = ?",
            (amount, name)
        )

        await db.commit()
        return True


# ✅ проверить дефицит (меньше 1)
async def check_deficit():
    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute(
            "SELECT name, amount FROM stock WHERE amount < 1"
        )
        return await cursor.fetchall()