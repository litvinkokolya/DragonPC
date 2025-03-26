from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, \
    KeyboardButton, FSInputFile
from aiogram.filters import Command
from database import get_products_of_category_id, add_to_cart, get_cart, create_order, remove_from_cart, get_categories, \
    get_product, get_category_name, delete_full_cart
from keyboards import main_menu

router = Router()


### 🔹 ОБРАБОТКА КОМАНДЫ /START
@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Добро пожаловать в магазин! Выберите действие: 👇", reply_markup=main_menu)


### 🔹 ОБРАБОТКА КОМАНДЫ "Каталог"
@router.message(F.text == "🛍 Каталог")
async def catalog_command(message: Message):
    categories = get_categories()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for category in categories:
        category_id, name = category
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=name, callback_data=f"category_{category_id}")])
    await message.answer("Выберите категорию:", reply_markup=keyboard)


### 🔹 Показ товаров категории
@router.callback_query(F.data.startswith("category_"))
async def show_products(callback: CallbackQuery):
    _, category_id = callback.data.split("_")
    category_id = int(category_id)

    # Получаем список продуктов и информацию о категории
    products = get_products_of_category_id(category_id)
    category_name = get_category_name(category_id)

    # Создаем клавиатуру с продуктами и кнопкой "Назад"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for product in products:
        product_id = product[0]
        name= product[1]
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=name, callback_data=f"product_{product_id}")])

    # Добавляем кнопку "Назад"
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories")])

    # Редактируем сообщение вместо отправки нового
    await callback.message.edit_text(
        f"Категория: {category_name}\n\nВыберите товар:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("product_"))
async def show_product_details(callback: CallbackQuery):
    _, product_id = callback.data.split("_")
    product_id = int(product_id)

    # Получаем информацию о товаре
    product = get_product(product_id)[0]
    if not product:
        await callback.answer("Товар не найден!", show_alert=True)
        return

    product_id, name, price, category_id, description, photo_path = product
    category_name = get_category_name(category_id)

    # Создаем клавиатуру
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить в корзину", callback_data=f"add_{product_id}")],
        [InlineKeyboardButton(text="➖ Удалить из корзины", callback_data=f"remove_{product_id}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_to_products__{category_id}")]
    ])

    try:
        # Используем FSInputFile для загрузки фото
        photo = FSInputFile(photo_path)

        await callback.message.answer_photo(
            photo=photo,
            caption=(
                f"Категория: {category_name}\n\n"
                f"Товар: {name}\n"
                f"Описание: {description}\n"
                f"Цена: {price}₽"
            ),
            reply_markup=keyboard
        )
        await callback.message.delete()
    except FileNotFoundError:
        await callback.message.edit_text(
            f"Категория: {category_name}\n\n"
            f"Товар: {name}\n"
            f"Описание: {description}\n"
            f"Цена: {price}₽\n\n"
            f"⚠️ Фото товара отсутствует",
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Ошибка при отправке фото: {e}")
        await callback.message.edit_text(
            f"Категория: {category_name}\n\n"
            f"Товар: {name}\n"
            f"Описание: {description}\n"
            f"Цена: {price}₽\n\n"
            f"⚠️ Ошибка при загрузке фото",
            reply_markup=keyboard
        )

    await callback.answer()


### 🔹 Обработка кнопки "Назад" к категориям
@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery):
    categories = get_categories()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for category in categories:
        category_id, name = category
        keyboard.inline_keyboard.append([InlineKeyboardButton(text=name, callback_data=f"category_{category_id}")])

    await callback.message.edit_text("Выберите категорию:", reply_markup=keyboard)
    await callback.answer()


### 🔹 Обработка кнопки "Назад" к товарам категории
@router.callback_query(F.data.startswith("back_to_products__"))
async def back_to_products(callback: CallbackQuery):
    _, category_id = callback.data.split("__")
    category_id = int(category_id)

    products = get_products_of_category_id(category_id)
    category_name = get_category_name(category_id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for product in products:
        product_id = product[0]
        name = product[1]
        keyboard.inline_keyboard.append(
            [InlineKeyboardButton(text=name, callback_data=f"product_{product_id}")]
        )

    keyboard.inline_keyboard.append(
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories")]
    )

    # Всегда отправляем новое сообщение
    await callback.message.delete()
    await callback.message.answer(
        f"Категория: {category_name}\n\nВыберите товар:",
        reply_markup=keyboard
    )


### 🔹 ОБРАБОТКА КНОПОК "ДОБАВИТЬ" И "УДАЛИТЬ"
@router.callback_query(F.data.startswith("add_") | F.data.startswith("remove_"))
async def update_cart_handler(callback: CallbackQuery):
    action, product_id = callback.data.split("_")
    product_id = int(product_id)

    if action == "add":
        add_to_cart(callback.from_user.id, product_id)
        await callback.answer("✅ Товар добавлен!")
    elif action == "remove":
        remove_from_cart(callback.from_user.id, product_id)
        await callback.answer("❌ Товар убран!")


@router.message(F.text == "🛒 Корзина")
@router.callback_query(F.data == "refresh_cart")
async def cart_command(event):
    user_id = event.from_user.id
    cart_items = get_cart(user_id)

    if not cart_items:
        text = "Ваша корзина пуста."
        if isinstance(event, CallbackQuery):
            await event.message.edit_text(text) if event.message.text != text else await event.answer()
        else:
            await event.answer(text)
        return

    cart_text = "🛒 <b>Ваша корзина:</b>\n\n"
    total_price = 0

    for idx, (name, quantity, price, product_id) in enumerate(cart_items, 1):
        item_total = quantity * price
        total_price += item_total
        cart_text += (
            f"<b>{idx}. {name}</b>\n"
            f"   × {quantity} шт. | {price}₽/шт. | <b>{item_total}₽</b>\n\n"
        )

    cart_text += f"💰 <b>Итого: {total_price}₽</b>"

    # Создаем кнопки управления для каждого товара
    keyboard_buttons = []
    for product_name, _, _, product_id in cart_items:
        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"❌ Удалить {product_name}",
                callback_data=f"remove_{product_id}"
            )
        ])

    keyboard_buttons.extend([
        [
            InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_cart"),
            InlineKeyboardButton(text="✅ Оформить", callback_data="checkout")
        ],
        [InlineKeyboardButton(text="🗑️ Очистить корзину", callback_data="clear_cart")]
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    if isinstance(event, CallbackQuery):
        try:
            await event.message.edit_text(
                cart_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except TelegramBadRequest:
            await event.answer()
    else:
        await event.answer(
            cart_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )


### 🔹 ОБРАБОТКА "Очистить корзину"
@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    delete_full_cart(user_id)
    await cart_command(callback)


### 🔹 ОБРАБОТКА "ОФОРМИТЬ ЗАКАЗ"
@router.callback_query(F.data == "checkout")
async def request_contact(callback: CallbackQuery):
    user_id = callback.from_user.id
    cart_items = get_cart(user_id)
    if cart_items:
        contact_keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📱 Отправить номер", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await callback.message.answer("📱 Отправьте свой номер телефона для оформления заказа:",
                                      reply_markup=contact_keyboard)
        await callback.answer()
    else:
        await callback.answer("Ошибка! Ваша корзина пустая.")


### 🔹 ПОЛУЧЕНИЕ НОМЕРА ТЕЛЕФОНА
@router.message(F.contact | F.text.regexp(r'^\+?\d{10,15}$'))
async def receive_contact(message: Message):
    phone_number = message.contact.phone_number if message.contact else message.text
    order_id = create_order(message.from_user.id, phone_number)

    if order_id:
        await message.answer(f"✅ Заказ #{order_id} оформлен!\n📞 Мы свяжемся с вами по номеру: {phone_number}.")
    else:
        await message.answer("❌ Ваша корзина пуста, добавьте товары перед заказом.")
