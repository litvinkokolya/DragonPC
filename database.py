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


def add_category(name):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def add_product(name, price, category_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price, category_id) VALUES (?, ?, ?)", (name, price, category_id))
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


### Функции для работы с товарами
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
