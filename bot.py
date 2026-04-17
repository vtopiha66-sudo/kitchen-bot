import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from menu import menu
from config import TOKEN
from db import init_db, update_stock
from logic import get_stock, check_deficit
from i18n import t

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_lang = {}


# ✅ клавиатура
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


# ✅ старт
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


# ✅ основной хендлер
@dp.message()
async def handler(msg: Message):
    user_id = msg.from_user.id

    # выбор языка
    if msg.text in ["UA", "RU", "PL"]:
        lang = msg.text.lower()
        user_lang[user_id] = lang
        await msg.answer(t("menu", lang), reply_markup=main_kb(lang))
        return

    lang = user_lang.get(user_id, "ua")

    # ➕ пополнение
    if msg.text == "➕ Поповнення":
        await msg.answer("Введи: назва кількість\nНаприклад: креветки 5")
        return

    # 📦 склад
    elif msg.text == t("stock", lang):
        stock = await get_stock()
        text = "\n".join([f"{n} — {s}" for n, s in stock]) or "Пусто"
        await msg.answer(text)
        return

    # ⚠️ дефицит
    elif msg.text == t("deficit", lang):
        items = await check_deficit()
        text = "\n".join([f"❗ {i[0]}" for i in items]) or "OK"
        await msg.answer(text)
        return

    # 🔥 ввод продукта (креветки 5)
    elif " " in msg.text:
        try:
            name, amount = msg.text.split()
            amount = float(amount)

            await update_stock(name, amount)

            await msg.answer(f"✅ Додано: {name} +{amount}")
        except:
            pass


# ✅ запуск
async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())