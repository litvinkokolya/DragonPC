
---

# DragonPC - Telegram Bot for Online Computer Store

Описание:  
Это проект интернет магазин Telegram-бот компьютерных товаров. Бот помогает пользователям находить и заказывать различные игровые товары, такие как столы, стулья, сборки и другие товары.

Функциональность:  
- Поиск товаров по категориям
- Просмотр информации о товаре
- Оформление заказов через чат
- Интеграция с базой данных для хранения информации о товарах и заказах

## Технологии
- Python
- aiogram — библиотека для работы с Telegram API
- .env — для конфиденциальных настроек (например, API ключей)

## Требования

Для запуска проекта локально потребуется:

- Python 3.8 и выше
- pip (для установки зависимостей)
- Telegram Bot API Token
- SQLite или другая СУБД для хранения данных
- Git (для клонирования репозитория)

## Установка и запуск

### Шаг 1: Клонирование репозитория
git clone https://github.com/litvinkokolya/dragonPc.git

### Шаг 2: Создание и активация виртуального окружения

Если вы не использовали виртуальные окружения раньше, создайте и активируйте его:

python -m venv venv


source venv/bin/activate  # Для Linux/Mac

venv\Scripts\activate  # Для Windows

### Шаг 3: Установка зависимостей

Установите необходимые библиотеки:
pip install -r requirements.txt

### Шаг 4: Создание файла конфигурации .env

Для работы бота необходимо создать файл .env в корне проекта, в котором будут храниться конфиденциальные данные, такие как токен для бота и настройки базы данных.

Пример содержания файла можете посмотреть в файле .env.example

Параметры:
- BOT_TOKEN — это токен Telegram бота, выдается при регистрации бота в BotFather.
- DB_NAME — название базы данных

Запустить команду python database.py - создастся база данных.

### Шаг 5: Запуск проекта

Теперь, когда все настройки сделаны, запустите бота:
python bot.py

Бот начнёт работать, и вы сможете взаимодействовать с ним через Telegram.

## Структура проекта
dragonPc/

├── bot.py                 # Главный файл для запуска бота

├── config.py              # Конфигурационные файлы для проекта

├── database.py            # Модели базы данных

├── requirements.txt       # Список зависимостей

├── .env                   # Конфигурационный файл для конфиденциальных данных

└── README.md              # Документация проекта

## Примечания

Убедитесь, что ваш токен бота и настройки базы данных правильно указаны в .env.

---

