TEXTS = {
    "menu": {
        "ua": "Головне меню",
        "ru": "Главное меню",
        "pl": "Menu główne"
    },
    "stock": {
        "ua": "📦 Склад",
        "ru": "📦 Склад",
        "pl": "📦 Magazyn"
    },
    "sales": {
        "ua": "📊 Продажі",
        "ru": "📊 Продажи",
        "pl": "📊 Sprzedaż"
    },
    "menu_btn": {
        "ua": "🍽 Меню",
        "ru": "🍽 Меню",
        "pl": "🍽 Menu"
    },
    "recipes": {
        "ua": "🧾 Рецепти",
        "ru": "🧾 Рецепты",
        "pl": "🧾 Receptury"
    },
    "deficit": {
        "ua": "⚠️ Дефіцит",
        "ru": "⚠️ Дефицит",
        "pl": "⚠️ Braki"
    },
    "choose_lang": {
        "ua": "Оберіть мову",
        "ru": "Выберите язык",
        "pl": "Wybierz język"
    }
}

def t(key, lang):
    return TEXTS[key][lang]
