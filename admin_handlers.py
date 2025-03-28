from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from database import (
    add_product, remove_product, edit_price, get_products,
    get_orders, update_order_status, remove_order,
    add_admin, remove_admin, get_admins, is_admin, is_super_admin, set_super_admin
)

admin_router = Router()

### 🔹 ИЗМЕНЕНИЕ ЦЕНЫ ТОВАРА
@admin_router.message(Command("edit_price"))
async def edit_price_handler(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для этой команды.")
        return

    try:
        product_id, new_price = map(int, message.text.split()[1:3])
        edit_price(product_id, new_price)
        await message.answer(f"✅ Цена товара с ID `{product_id}` изменена на **{new_price}₽**.")
    except:
        await message.answer("⚠️ Используйте команду так:\n`/edit_price product_id новая_цена`")


### 🔹 ПРОСМОТР СПИСКА ЗАКАЗОВ
@admin_router.message(Command("orders"))
async def list_orders_handler(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для этой команды.")
        return

    orders = get_orders()
    if not orders:
        await message.answer("❌ Заказов нет.")
    else:
        order_list = "\n".join([f"📦 **Заказ #{o[0]}** – {o[1]}₽, **Статус:** {o[2]}" for o in orders])
        await message.answer(f"📜 **Список заказов:**\n{order_list}")


### 🔹 ОБНОВЛЕНИЕ СТАТУСА ЗАКАЗА
@admin_router.message(Command("update_order"))
async def update_order_status_handler(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для этой команды.")
        return

    try:
        args = message.text.split(maxsplit=2)
        order_id, new_status = int(args[1]), args[2]
        update_order_status(order_id, new_status)
        await message.answer(f"✅ Статус заказа **#{order_id}** изменен на **{new_status}**.")
    except:
        await message.answer("⚠️ Используйте команду так:\n`/update_order order_id новый_статус`")


### 🔹 УДАЛЕНИЕ ЗАКАЗА
@admin_router.message(Command("remove_order"))
async def remove_order_handler(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для этой команды.")
        return

    try:
        order_id = int(message.text.split()[1])
        remove_order(order_id)
        await message.answer(f"✅ Заказ **#{order_id}** удален.")
    except:
        await message.answer("⚠️ Используйте команду так:\n`/remove_order order_id`")


### 🔹 ДОБАВЛЕНИЕ АДМИНИСТРАТОРА (ТОЛЬКО ДЛЯ СУПЕР-АДМИНА)
@admin_router.message(Command("add_admin"))
async def add_admin_handler(message: Message):
    if not is_super_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для этой команды.")
        return

    try:
        user_id = int(message.text.split()[1])
        add_admin(user_id)
        await message.answer(f"✅ Пользователь {user_id} добавлен в администраторы.")
    except:
        await message.answer("⚠️ Используйте команду так:\n`/add_admin user_id`")


### 🔹 УДАЛЕНИЕ АДМИНИСТРАТОРА
@admin_router.message(Command("remove_admin"))
async def remove_admin_handler(message: Message):
    if not is_super_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для этой команды.")
        return

    try:
        user_id = int(message.text.split()[1])
        if is_super_admin(user_id):
            await message.answer("⚠️ Нельзя удалить супер-администратора!")
        else:
            remove_admin(user_id)
            await message.answer(f"✅ Пользователь {user_id} удален из администраторов.")
    except:
        await message.answer("⚠️ Используйте команду так:\n`/remove_admin user_id`")


### 🔹 СПИСОК АДМИНИСТРАТОРОВ
@admin_router.message(Command("admins"))
async def admins_handler(message: Message):
    if not is_super_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для этой команды.")
        return

    admins = get_admins()
    if not admins:
        await message.answer("❌ Администраторов нет.")
        return

    text = "👤 **Список администраторов:**\n"
    for user_id, is_super in admins:
        text += f"• `{user_id}` {'(Супер-админ)' if is_super else ''}\n"

    await message.answer(text)


### 🔹 ПРОСМОТР СПИСКА ТОВАРОВ
@admin_router.message(Command("products"))
async def list_products_handler(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав для этой команды.")
        return

    products = get_products()
    if not products:
        await message.answer("❌ Товаров пока нет.")
    else:
        product_list = "\n".join([f"📦 **{p[0]}** – {p[1]}, **Цена:** {p[2]}₽" for p in products])
        await message.answer(f"🛒 **Список товаров:**\n{product_list}")


### 🔹 УСТАНОВКА СУПЕР-АДМИНА (ОДИН РАЗ)
@admin_router.message(Command("set_super_admin"))
async def set_super_admin_handler(message: Message):
    if set_super_admin(message.from_user.id):
        await message.answer("✅ Вы назначены супер-администратором!")
    else:
        await message.answer("⚠️ Супер-администратор уже назначен.")
