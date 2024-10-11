from flask import Blueprint, render_template, request
import sqlite3
from datetime import datetime

main_bp = Blueprint('main', __name__)

DATABASE = 'F:/Hotel Management System/hotel_management.db'

@main_bp.route('/', methods=['GET'])
def index():
    checkin = request.args.get('checkin')
    checkout = request.args.get('checkout')

    rooms = []
    if checkin and checkout:
        try:
            # Преобразование дат
            checkin_date = datetime.strptime(checkin, '%Y-%m-%d').date()
            checkout_date = datetime.strptime(checkout, '%Y-%m-%d').date()

            # Открываем соединение с базой данных
            with sqlite3.connect(DATABASE, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT Номер_комнаты, Тип_комнаты, Стоимость, Вместимость, Площадь, Удобства, Описание
                    FROM Номера
                    WHERE Статус_комнаты = 'свободно'
                """)
                rooms = cursor.fetchall()

                # Подсчёт цены за несколько ночей
                nights = (checkout_date - checkin_date).days
                rooms = [{
                    'number': row[0],  # Номер комнаты
                    'category': row[1],  # Тип комнаты
                    'price_per_night': row[2],  # Стоимость за сутки
                    'guests': row[3],  # Вместимость
                    'area': row[4],  # Площадь
                    'facilities': row[5],  # Удобства
                    'description': row[6],  # Описание
                    'total_price': row[2] * nights  # Общая стоимость за период
                } for row in rooms]

        except ValueError as e:
            # Если произошла ошибка в формате даты, выводим сообщение
            print(f"Ошибка преобразования даты: {e}")
            return render_template('index.html', rooms=[], error_message="Неверный формат даты.")

    return render_template('index.html', rooms=rooms, checkin=checkin, checkout=checkout)