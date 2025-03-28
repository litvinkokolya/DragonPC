from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Reply-клавиатура (главное меню)
button_catalog = KeyboardButton(text="🛍 Каталог")
button_cart = KeyboardButton(text="🛒 Корзина")

main_menu = ReplyKeyboardMarkup(
    keyboard=[[button_catalog, button_cart]],
    resize_keyboard=True
)
