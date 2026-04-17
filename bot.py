import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

from config import TOKEN
from db import (
    init_db,
    get_stock,
    update_stock,
    check_deficit,
    add_recipe,
    add_recipe_item,
    get_recipes,
    cook_dish
)
from i18n import t
from menu import menu

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_lang = {}
waiting_for_input = {}


# =========================
# ✅ КЛАВИАТУРА
# =========================
def main_kb(lang):
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="➕ Поповнення"),
                KeyboardButton(text=t("stock", lang)),
                KeyboardButton(text=t("sales", lang))
            ],
            [
                KeyboardButton(text=t("menu_btn", lang)),
                KeyboardButton(text=t("recipes", lang))
            ],
            [
                KeyboardButton(text=t("deficit", lang))
            ]
        ],
        resize_keyboard=True
    )


# =========================
# 🚀 START
# =========================
@dp.message(Command("start"))
async def start(msg: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="UA"), KeyboardButton(text="RU"), KeyboardButton(text="PL")]
        ],
        resize_keyboard=True
    )

    await msg.answer(
        "Choose language / Обери мову / Wybierz język",
        reply_markup=kb
    )


# =========================
# 🤖 ОСНОВНОЙ ХЕНДЛЕР
# =========================
@dp.message()
async def handler(msg: Message):
    user_id = msg.from_user.id
    text = msg.text.strip()

    if user_id not in user_lang:
        user_lang[user_id] = "ua"

    lang = user_lang[user_id]

    # 🌍 язык
    if text in ["UA", "RU", "PL"]:
        lang = text.lower()
        user_lang[user_id] = lang
        await msg.answer(t("menu", lang), reply_markup=main_kb(lang))
        return

    # =========================
    # 🔥 СОСТОЯНИЯ
    # =========================
    state = waiting_for_input.get(user_id)

    # ➕ склад ввод
    if state == "add_stock":
        try:
            name, amount = text.split()
            amount = float(amount)

            await update_stock(name, amount)

            await msg.answer(f"✅ Додано: {name} +{amount}")
            waiting_for_input[user_id] = None
        except:
            await msg.answer("❌ формат: продукт 5")
        return

    # 🧾 рецепт название
    if state == "recipe_name":
        recipe_id = await add_recipe(text)
        waiting_for_input[user_id] = ("recipe_items", recipe_id)

        await msg.answer("Вводи інгредієнти: назва кількість\nSTOP — завершити")
        return

    # 🧾 ингредиенты рецепта
    if isinstance(state, tuple):
        mode, recipe_id = state

        if mode == "recipe_items":

            if text.lower() == "stop":
                waiting_for_input[user_id] = None
                await msg.answer("✅ Рецепт збережено")
                return

            try:
                name, amount = text.split()
                amount = float(amount)

                await add_recipe_item(recipe_id, name, amount)

                await msg.answer(f"➕ {name} {amount}")
            except:
                await msg.answer("❌ формат: продукт 0.2")

            return

    # 📊 продаж
    if state == "sale":
        try:
            recipe_id = int(text)

            success, product = await cook_dish(recipe_id)

            if success:
                await msg.answer("✅ Продано (склад списаний)")
            else:
                await msg.answer(f"❌ Не вистачає: {product}")

            waiting_for_input[user_id] = None

        except:
            await msg.answer("❌ введи ID страви")

        return

    # =========================
    # 📦 КНОПКИ
    # =========================

    # ➕ пополнение
    if text == "➕ Поповнення":
        waiting_for_input[user_id] = "add_stock"
        await msg.answer("Введи: продукт кількість\nНаприклад: креветки 5")
        return

    # 📦 склад
    if text == t("stock", lang):
        stock = await get_stock()
        text = "\n".join([f"{n} — {s}" for n, s in stock]) or "Пусто"
        await msg.answer(text)
        return

    # 🍽 меню
    if text == t("menu_btn", lang):
        text = "\n".join([f"🍽 {m}" for m in menu])
        await msg.answer(text)
        return

    # ⚠️ дефицит
    if text == t("deficit", lang):
        items = await check_deficit()
        text = "\n".join([f"❗ {i[0]}" for i in items]) or "OK"
        await msg.answer(text)
        return

    # 🧾 рецепты
    if text == t("recipes", lang):
        recipes = await get_recipes()

        if not recipes:
            await msg.answer("Поки немає рецептів")
            return

        text = "\n".join([f"{r[0]} — {r[1]}" for r in recipes])
        await msg.answer(text + "\n\n➕ Напиши: + рецепт")
        return

    # ➕ создать рецепт
    if text.lower() == "+ рецепт":
        waiting_for_input[user_id] = "recipe_name"
        await msg.answer("Введи назву рецепту")
        return

    # 📊 продажи
    if text == t("sales", lang):
        recipes = await get_recipes()

        if not recipes:
            await msg.answer("Немає страв")
            return

        text = "\n".join([f"{r[0]} — {r[1]}" for r in recipes])

        waiting_for_input[user_id] = "sale"

        await msg.answer("Вибери ID страви:\n\n" + text)
        return


# =========================
# ▶️ ЗАПУСК
# =========================
async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())