import sys
import os
from flask import Flask
import secrets
import sqlite3

# Добавляем директорию проекта в системный путь
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Импорт маршрутов
from web_app.routes.hotel_routes import main_bp
from web_app.routes.booking_routes import booking_bp
from web_app.routes.user_routes import user_bp

app = Flask(__name__)

# Фиксированный секретный ключ
app.secret_key = 'y_super_secret_key_12345!'

# Подключаем маршруты
app.register_blueprint(user_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(main_bp)



conn = sqlite3.connect('F:/Hotel Management System/hotel_management.db')
cursor = conn.cursor()


if __name__ == '__main__':
    # Проверьте подключение к базе данных перед запуском
    conn = sqlite3.connect('F:/Hotel Management System/hotel_management.db')
    cursor = conn.cursor()

    # Проверьте, существует ли таблица Пользователи
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Пользователи';")
    print(cursor.fetchone())  # Вывод имени таблицы, если она существует

    # Выполните простой запрос
    cursor.execute("SELECT * FROM Пользователи LIMIT 1;")
    print(cursor.fetchone())  # Вывод первой записи из таблицы, если она есть

    # Закрытие соединения
    conn.close()

    # Запуск Flask приложения
    app.run(debug=True)