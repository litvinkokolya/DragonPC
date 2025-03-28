import sqlite3

from config import DATABASE_NAME

# Подключение к базе данных
conn = sqlite3.connect(DATABASE_NAME)
cursor = conn.cursor()

# Таблица категорий
cursor.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
)
""")

# Таблица товаров
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    photo_path TEXT NOT NULL, 
    FOREIGN KEY (category_id) REFERENCES categories (id)
)
""")

# Таблица корзины
cursor.execute("""
CREATE TABLE IF NOT EXISTS cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products (id)
)
""")

# Таблица заказов
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    total_price INTEGER NOT NULL,
    phone_number TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
)
""")

# Таблица администраторов
cursor.execute("""
CREATE TABLE IF NOT EXISTS admins (
    user_id INTEGER PRIMARY KEY,
    is_super_admin INTEGER DEFAULT 0
)
""")

conn.commit()
conn.close()


### Функции для работы с категориями
def add_category(name):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def get_categories():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories")
    categories = cursor.fetchall()
    conn.close()
    return categories


def get_category_name(category_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM categories WHERE categories.id=?", (category_id, ))
    category = cursor.fetchall()
    conn.close()
    return category[0][1]

### Функции для работы с товарами
def add_product(name, price, category_id, description, photo_path):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price, category_id, description, photo_path) VALUES (?, ?, ?, ?, ?)",
                   (name, price, category_id, description, photo_path))
    conn.commit()
    conn.close()


def get_product(product_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE products.id=?", (product_id, ))
    product = cursor.fetchall()
    conn.close()
    return product

def get_products_of_category_id(category_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE products.category_id=?", (category_id, ))
    products = cursor.fetchall()
    conn.close()
    return products


def remove_product(product_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()


def edit_price(product_id, new_price):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET price=? WHERE id=?", (new_price, product_id))
    conn.commit()
    conn.close()


def get_products():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return products
### Функции для работы с корзиной


def add_to_cart(user_id, product_id, quantity=1):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT quantity FROM cart WHERE user_id=? AND product_id=?", (user_id, product_id))
    result = cursor.fetchone()

    if result:
        new_quantity = result[0] + quantity
        cursor.execute("UPDATE cart SET quantity=? WHERE user_id=? AND product_id=?",
                       (new_quantity, user_id, product_id))
    else:
        cursor.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)",
                       (user_id, product_id, quantity))

    conn.commit()
    conn.close()


def delete_full_cart(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id=?", (user_id, ))
    conn.commit()
    conn.close()


def remove_from_cart(user_id, product_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT quantity FROM cart WHERE user_id=? AND product_id=?", (user_id, product_id))
    result = cursor.fetchone()

    if result:
        if result[0] > 1:
            new_quantity = result[0] - 1
            cursor.execute("UPDATE cart SET quantity=? WHERE user_id=? AND product_id=?",
                           (new_quantity, user_id, product_id))
        else:
            cursor.execute("DELETE FROM cart WHERE user_id=? AND product_id=?", (user_id, product_id))

    conn.commit()
    conn.close()


def get_cart(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT products.name, cart.quantity, products.price, products.id 
        FROM cart 
        JOIN products ON cart.product_id = products.id 
        WHERE cart.user_id=?
    """, (user_id,))
    cart_items = cursor.fetchall()
    conn.close()
    return cart_items


### Функции для работы с заказами
def get_orders():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, total_price, status FROM orders")
    orders = cursor.fetchall()
    conn.close()
    return orders


def update_order_status(order_id, new_status):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status=? WHERE id=?", (new_status, order_id))
    conn.commit()
    conn.close()


def remove_order(order_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id=?", (order_id,))
    conn.commit()
    conn.close()


def create_order(user_id, phone_number):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT products.id, products.price, cart.quantity
        FROM cart
        JOIN products ON cart.product_id = products.id
        WHERE cart.user_id=?
    """, (user_id,))
    cart_items = cursor.fetchall()

    if not cart_items:
        conn.close()
        return None

    total_price = sum(item[1] * item[2] for item in cart_items)

    cursor.execute("INSERT INTO orders (user_id, total_price, phone_number) VALUES (?, ?, ?)", (user_id, total_price, phone_number))
    order_id = cursor.lastrowid

    cursor.execute("DELETE FROM cart WHERE user_id=?", (user_id,))

    conn.commit()
    conn.close()
    return order_id


### Функции для работы с администраторами
def set_super_admin(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM admins WHERE is_super_admin=1")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO admins (user_id, is_super_admin) VALUES (?, 1)", (user_id,))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False


def add_admin(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()


def remove_admin(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM admins WHERE user_id=? AND is_super_admin=0", (user_id,))
    conn.commit()
    conn.close()


def is_admin(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM admins WHERE user_id=?", (user_id,))
    result = cursor.fetchone()[0]
    conn.close()
    return result > 0


def is_super_admin(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT is_super_admin FROM admins WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result and result[0] == 1


def get_admins():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, is_super_admin FROM admins")
    admins = cursor.fetchall()
    conn.close()
    return admins


# Функция добавления изначальных товаров (перед этим требуется добавить категории)
def add_all_products():
    # Категории:
    # 1 - Игровые кресла
    # 2 - Наушники
    # 3 - Клавиатуры
    # 4 - Мыши
    # 5 - Мониторы
    # 6 - Компьютеры
    # 7 - Столы

    # Клавиатуры (category_id = 3)
    add_product(
        "MCHOSE G98 Pro Flame Orange Switch RGB Gray and Blue RU",
        13000,
        3,
        "Коричневые свечи, HoTSwitch",
        "product_photos/keyboards/MCHOSE G98 Pro Flame.jpg"
    )
    add_product(
        "MCHOSE G98 Pro Snow Tiger Switch RGB Orange and Blue RU",
        13000,
        3,
        "HoTSwitch, коричневые свечи",
        "product_photos/keyboards/MCHOSE G98 Pro Snow.jpg"
    )
    add_product(
        "LOFREE OE901 Wanderfree Grey",
        13990,
        3,
        "Красные свечи, HoTSwitch",
        "product_photos/keyboards/LOFREE OE901.jpg"
    )

    # Мыши (category_id = 4)
    add_product(
        "Razer DeathAdder Essential Black",
        2690,
        4,
        "Bluetooth модуль, беспроводная",
        "product_photos/mice/Razer DeathAdder.jpg"
    )
    add_product(
        "MCHOSE L7 Ultra",
        8490,
        4,
        "Wireless Mouse White 8K",
        "product_photos/mice/MCHOSE L7 Ultra.jpg"
    )
    add_product(
        "MCHOSE AX5",
        11990,
        4,
        "Magnesium Alloy Wireless Mouse Pro Max Pink 8K",
        "product_photos/mice/MCHOSE AX5.jpg"
    )

    # Наушники (category_id = 2)
    add_product(
        "Razer Kraken V4 X",
        11690,
        2,
        "С микрофоном, bluetooth",
        "product_photos/headphones/Razer Kraken V4 X.jpg"
    )

    # Мониторы (category_id = 5)
    add_product(
        "Samsung Odyssey G3 S24AG320NI 24\"",
        16990,
        5,
        "LED, 1 мс",
        "product_photos/monitors/Samsung Odyssey.jpg"
    )
    add_product(
        "MSI MAG 27C6X 27\"",
        24990,
        5,
        "VA, 16:9, Китай",
        "product_photos/monitors/MSI MAG.jpg"
    )
    add_product(
        "ASRock Phantom Gaming 27 PG27QRT1B Black",
        28490,
        5,
        "IPS, 16:9, матовое покрытие",
        "product_photos/monitors/ASRock Phantom.jpg"
    )

    # Игровые кресла (category_id = 1)
    add_product(
        "Eureka Norn Grey",
        24990,
        1,
        "Геймерское кресло компьютерное",
        "product_photos/armchairs/Eureka 2.jpg"
    )
    add_product(
        "ZONE 51 FREELANCER P3",
        23990,
        1,
        "Геймерское кресло компьютерное",
        "product_photos/armchairs/ZONE 51.jpg"
    )
    add_product(
        "Eureka Python II Red",
        42990,
        1,
        "Геймерское кресло компьютерное",
        "product_photos/armchairs/Eureka.jpg"
    )

    # Столы (category_id = 7)
    add_product(
        "EUREKA ERK-IMOD-60B",
        29990,
        7,
        "153x70",
        "product_photos/tables/EUREKA ERK-IMOD-60B.jpg"
    )
    add_product(
        "Cougar MARS 120",
        31990,
        7,
        "125x81",
        "product_photos/tables/Cougar MARS 120.jpg"
    )
    add_product(
        "FoxGear FG-ED-55B",
        74990,
        7,
        "140x70",
        "product_photos/tables/FoxGear FG-ED-55B.jpg"
    )

    # Компьютеры (category_id = 6)
    add_product(
        "Progaming SS",
        85900,
        6,
        "Процессор i5-12400\nВидеокарта RTX 4060 8GB\nОперативная память 16GB\nNVME 1TB",
        "product_photos/pcs/Progaming S.jpg"
    )
    add_product(
        "Progaming A",
        239000,
        6,
        "Процессор i5-13600K\nВидеокарта RTX 4070 Super 12GB\nОперативная память 32GB RGB\nNVME 1TB",
        "product_photos/pcs/Progaming A.jpg"
    )
    add_product(
        "Progaming S",
        62900,
        6,
        "Процессор i3-12100\nВидеокарта RTX 3050 6GB\nОперативная память 16GB\nNVME 500GB",
        "product_photos/pcs/Progaming SS.jpg"
    )
