from desktop_app.models.database_manager import get_all_reservations, DATABASE
from flask import Blueprint, render_template, redirect, url_for, session, request
from desktop_app.models.database_manager import add_reservation
import sqlite3



# Создаем блюпринт для маршрутов бронирования
booking_bp = Blueprint('booking', __name__)
@booking_bp.route('/book', methods=['GET', 'POST'])
def book_room():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user.login', next='booking'))

    if request.method == 'POST':
        # Получение данных из формы
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        room_number = request.form.get('room_number')
        checkin = request.form.get('checkin')
        checkout = request.form.get('checkout')

        # Проверка обязательных полей
        if not (last_name and first_name and phone and email):
            return "Ошибка: все поля обязательны для заполнения."

        # Устанавливаем статус бронирования и оплаты
        booking_status = 'Создано'
        payment_status = 'Не оплачено'

        # Сохраняем данные бронирования в базу
        try:
            with sqlite3.connect(DATABASE, timeout=30) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Бронирования (client_id, Номер_комнаты, Дата_заезда, Дата_выезда, Статус_бронирования, Статус_оплаты, Дата_создания)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                """, (user_id, room_number, checkin, checkout, booking_status, payment_status))
                conn.commit()
        except sqlite3.OperationalError as e:
            if "locked" in str(e):
                return "Ошибка: база данных заблокирована, попробуйте снова через несколько секунд."
            else:
                raise e

        return redirect(url_for('booking.confirmation'))

    # Обработка GET-запроса для отображения формы бронирования
    room_number = request.args.get('room_number')
    checkin = request.args.get('checkin')
    checkout = request.args.get('checkout')

    # Если данные есть, сохраняем их в сессии
    if room_number and checkin and checkout:
        session['room_number'] = room_number
        session['checkin'] = checkin
        session['checkout'] = checkout
    else:
        # Если данных нет, пытаемся извлечь их из сессии
        room_number = session.get('room_number')
        checkin = session.get('checkin')
        checkout = session.get('checkout')

    # Проверка, что все данные присутствуют
    if not room_number or not checkin or not checkout:
        return "Ошибка: номер комнаты и даты обязательны."

    # Передаем данные в форму бронирования
    return render_template('booking_form.html', room_number=room_number, checkin=checkin, checkout=checkout)


def book_room_via_web(user_id, room_id, checkin, checkout):
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()

        # Проверяем, есть ли client_id для данного пользователя в таблице Пользователи
        cursor.execute("SELECT client_id FROM Пользователи WHERE id = ?", (user_id,))
        client_id = cursor.fetchone()

        if not client_id:
            # Если client_id нет, создаём нового клиента в таблице Клиенты
            cursor.execute("""
                INSERT INTO Клиенты (Имя, Фамилия, Email, Телефон)
                SELECT Имя, Фамилия, Email, Телефон FROM Пользователи WHERE id = ?
            """, (user_id,))
            client_id = cursor.lastrowid

            # Обновляем client_id в таблице Пользователи
            cursor.execute("UPDATE Пользователи SET client_id = ? WHERE id = ?", (client_id, user_id))
            conn.commit()

        # Используем client_id для создания бронирования
        cursor.execute("""
            INSERT INTO Бронирования (client_id, room_id, checkin, checkout)
            VALUES (?, ?, ?, ?)
        """, (client_id, room_id, checkin, checkout))
        conn.commit()



# Маршрут для подтверждения бронирования
@booking_bp.route('/confirmation', methods=['GET'])
def confirmation():
    return render_template('confirm_booking.html')

# Маршрут для получения списка всех бронирований
@booking_bp.route('/reservations', methods=['GET'])
def reservations():
    reservations_list = get_all_reservations()
    return render_template('reservations.html', reservations=reservations_list)
