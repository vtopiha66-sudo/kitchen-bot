waiting_for_input = set()

@dp.message()
async def handler(msg: Message):
    user_id = msg.from_user.id

    if user_id not in user_lang:
        user_lang[user_id] = "ua"

    # выбор языка
    if msg.text in ["UA", "RU", "PL"]:
        lang = msg.text.lower()
        user_lang[user_id] = lang
        await msg.answer(t("menu", lang), reply_markup=main_kb(lang))
        return

    lang = user_lang[user_id]

    # ➕ пополнение
    if msg.text == "➕ Поповнення":
        waiting_for_input.add(user_id)
        await msg.answer("Введи: назва кількість\nНаприклад: креветки 5")
        return

    # 📦 склад
    elif msg.text == t("stock", lang):
        stock = await get_stock()
        text = "\n".join([f"{n} — {s}" for n, s in stock]) or "Пусто"
        await msg.answer(text)
        return

    # 🍽 меню
    elif msg.text == t("menu_btn", lang):
        text = "\n".join([f"🍽 {m}" for m in menu])
        await msg.answer(text)
        return

    # ⚠️ дефицит
    elif msg.text == t("deficit", lang):
        items = await check_deficit()
        text = "\n".join([f"❗ {i[0]}" for i in items]) or "OK"
        await msg.answer(text)
        return

    # 📊 продажи
    elif msg.text == t("sales", lang):
        await msg.answer("📊 Продажі скоро будуть")
        return

    # 🧾 рецепты
    elif msg.text == t("recipes", lang):
        await msg.answer("🧾 Рецепти скоро будуть")
        return

    # 🔥 ввод продукта
    elif user_id in waiting_for_input:
        try:
            name, amount = msg.text.split()
            amount = float(amount)

            await update_stock(name, amount)

            await msg.answer(f"✅ Додано: {name} +{amount}")
            waiting_for_input.remove(user_id)
        except:
            await msg.answer("❌ Невірний формат. Напиши: продукт 5")
        return