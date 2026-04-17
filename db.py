import aiosqlite

DB = "kitchen.db"


# =========================
# ✅ СОЗДАНИЕ БАЗЫ
# =========================
async def init_db():
    async with aiosqlite.connect(DB) as db:

        # 📦 склад
        await db.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            amount REAL DEFAULT 0
        )
        """)

        # 🧾 рецепты (ПФ и блюда)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT  -- pf или dish
        )
        """)

        # 📊 состав рецепта
        await db.execute("""
        CREATE TABLE IF NOT EXISTS recipe_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER,
            ingredient TEXT,
            amount REAL
        )
        """)

        await db.commit()


# =========================
# 📦 СКЛАД
# =========================
async def get_stock():
    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute(
            "SELECT name, amount FROM stock ORDER BY name"
        )
        return await cursor.fetchall()


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


async def remove_stock(name, amount):
    name = name.lower().strip()

    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute(
            "SELECT amount FROM stock WHERE name = ?", (name,)
        )
        row = await cursor.fetchone()

        if not row:
            return False

        if row[0] < amount:
            return False

        await db.execute(
            "UPDATE stock SET amount = amount - ? WHERE name = ?",
            (amount, name)
        )

        await db.commit()
        return True


async def check_deficit():
    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute(
            "SELECT name, amount FROM stock WHERE amount < 1"
        )
        return await cursor.fetchall()


# =========================
# 🧾 РЕЦЕПТЫ
# =========================
async def add_recipe(name, type_="dish"):
    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute(
            "INSERT INTO recipes (name, type) VALUES (?, ?)",
            (name, type_)
        )
        await db.commit()
        return cursor.lastrowid


async def get_recipes():
    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute(
            "SELECT id, name, type FROM recipes ORDER BY name"
        )
        return await cursor.fetchall()


async def delete_recipe(recipe_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "DELETE FROM recipes WHERE id = ?", (recipe_id,)
        )
        await db.execute(
            "DELETE FROM recipe_items WHERE recipe_id = ?", (recipe_id,)
        )
        await db.commit()


# =========================
# 📊 СОСТАВ РЕЦЕПТА
# =========================
async def add_recipe_item(recipe_id, ingredient, amount):
    ingredient = ingredient.lower().strip()

    async with aiosqlite.connect(DB) as db:
        await db.execute(
            """
            INSERT INTO recipe_items (recipe_id, ingredient, amount)
            VALUES (?, ?, ?)
            """,
            (recipe_id, ingredient, amount)
        )
        await db.commit()


async def get_recipe_items(recipe_id):
    async with aiosqlite.connect(DB) as db:
        cursor = await db.execute(
            """
            SELECT ingredient, amount
            FROM recipe_items
            WHERE recipe_id = ?
            """,
            (recipe_id,)
        )
        return await cursor.fetchall()


# =========================
# 🔥 СПИСАНИЕ ПО РЕЦЕПТУ
# =========================
async def cook_dish(recipe_id):
    """
    списывает ингредиенты со склада
    """
    items = await get_recipe_items(recipe_id)

    # проверка хватает ли всего
    async with aiosqlite.connect(DB) as db:
        for name, amount in items:
            cursor = await db.execute(
                "SELECT amount FROM stock WHERE name = ?",
                (name,)
            )
            row = await cursor.fetchone()

            if not row or row[0] < amount:
                return False, name  # не хватает продукта

        # если всё ок — списываем
        for name, amount in items:
            await db.execute(
                "UPDATE stock SET amount = amount - ? WHERE name = ?",
                (amount, name)
            )

        await db.commit()

    return True, None