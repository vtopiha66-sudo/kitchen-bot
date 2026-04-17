import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN
from db import init_db
from logic import get_stock, check_deficit
from i18n import t

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_lang = {}

def main_kb(lang):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(
        KeyboardButton(text=t("stock", lang)),
        KeyboardButton(text=t("sales", lang))
    )
    kb.add(
        KeyboardButton(text=t("menu_btn", lang)),
        KeyboardButton(text=t("recipes", lang))
    )
    kb.add(
        KeyboardButton(text=t("deficit", lang))
    )
    return kb

@dp.message(commands=["start"])
async def start(msg: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("UA", "RU", "PL")
    await msg.answer("Choose language / Обери мову / Wybierz język", reply_markup=kb)

@dp.message()
async def handler(msg: types.Message):
    user_id = msg.from_user.id

    if msg.text in ["UA", "RU", "PL"]:
        lang = msg.text.lower()
        user_lang[user_id] = lang
        await msg.answer(t("menu", lang), reply_markup=main_kb(lang))
        return

    lang = user_lang.get(user_id, "ua")

    if msg.text == t("stock", lang):
        stock = await get_stock()
        text = "\n".join([f"{n} — {s}" for n, s in stock]) or "Пусто"
        await msg.answer(text)

    elif msg.text == t("deficit", lang):
        items = await check_deficit()
        text = "\n".join([f"❗ {i[0]}" for i in items]) or "OK"
        await msg.answer(text)

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
