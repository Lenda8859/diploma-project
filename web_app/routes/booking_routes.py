from desktop_app.models.database_manager import get_all_reservations, DATABASE
from flask import Blueprint, render_template, redirect, url_for, session, request
from desktop_app.models.database_manager import add_reservation
import sqlite3
import logging
from desktop_app.models.status_enums import RoomStatus
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    filename='error_log.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s')

# Создаем блюпринт для маршрутов бронирования
booking_bp = Blueprint('booking', __name__)


@booking_bp.route('/book', methods=['GET', 'POST'])
def book_room():
    user_id = session.get('user_id')
    if not user_id:
        logging.error("Ошибка: пользователь не авторизован.")
        return redirect(url_for('user.login', next='booking'))

    if request.method == 'POST':
        room_number = request.form.get('room_number')
        checkin = request.form.get('checkin')
        checkout = request.form.get('checkout')
        middle_name = request.form.get('middle_name')

        logging.info(f"Получены данные для бронирования: room_number={room_number}, checkin={checkin}, checkout={checkout}")

        # Проверка дат
        if not checkin or not checkout:
            logging.error(f"Некорректные даты: checkin={checkin}, checkout={checkout}.")
            return "Ошибка: необходимо указать даты заезда и выезда."

        booking_status = 'Создано'
        payment_status = 'Не оплачено'

        try:
            with sqlite3.connect(DATABASE, timeout=30) as conn:
                cursor = conn.cursor()

                # Получаем данные пользователя из таблицы "Пользователи"
                cursor.execute("SELECT Фамилия, Имя, Телефон, Email FROM Пользователи WHERE id = ?", (user_id,))
                user_data = cursor.fetchone()

                if not user_data:
                    logging.error(f"Пользователь с id={user_id} не найден.")
                    return "Ошибка: пользователь не найден."

                # Убедимся, что все поля заполнены
                last_name, first_name, phone, email = (user_data[0], user_data[1],
                                                       user_data[2] if user_data[2] else '',
                                                       user_data[3] if user_data[3] else '')

                # Проверка, существует ли клиент для данного пользователя в таблице "Клиенты"
                cursor.execute("SELECT id FROM Клиенты WHERE Email = ?", (email,))
                client = cursor.fetchone()

                if not client:
                    logging.info(f"Создаем запись клиента для пользователя с user_id={user_id}")
                    cursor.execute("""
                        INSERT INTO Клиенты (Фамилия, Имя, Отчество, Телефон, Email)
                        VALUES (?, ?, ?, ?, ?)
                    """, (last_name, first_name, middle_name, phone, email))
                    client_id = cursor.lastrowid  # Получаем новый client_id
                    conn.commit()
                    logging.info(f"Клиент успешно создан с client_id={client_id}")
                else:
                    client_id = client[0]
                    logging.info(f"Найден существующий клиент с client_id={client_id}")

                # Вставляем данные бронирования
                add_reservation(client_id=client_id, check_in_date=checkin, check_out_date=checkout,
                                room_number=room_number, booking_status=booking_status, payment_status=payment_status)

                logging.info(f"Бронирование успешно добавлено: client_id={client_id}, room_number={room_number}, checkin={checkin}, checkout={checkout}")
        except sqlite3.OperationalError as e:
            if "locked" in str(e):
                logging.error(f"Ошибка: база данных заблокирована: {e}")
                return "Ошибка: база данных заблокирована, попробуйте снова через несколько секунд."
            else:
                logging.error(f"Ошибка базы данных: {e}")
                raise e

        return redirect(url_for('booking.confirmation'))

    room_number = request.args.get('room_number')
    checkin = request.args.get('checkin')
    checkout = request.args.get('checkout')

    if room_number and checkin and checkout:
        session['room_number'] = room_number
        session['checkin'] = checkin
        session['checkout'] = checkout
        logging.info(f"Сохранены данные в сессии: room_number={room_number}, checkin={checkin}, checkout={checkout}")
    else:
        room_number = session.get('room_number')
        checkin = session.get('checkin')
        checkout = session.get('checkout')

    if not room_number or not checkin or not checkout:
        logging.error(f"Ошибка: номер комнаты или даты не указаны. room_number={room_number}, checkin={checkin}, checkout={checkout}.")
        return "Ошибка: номер комнаты и даты обязательны."

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
                INSERT INTO Клиенты (Имя, Фамилия, Отчество, Email, Телефон)
                SELECT Имя, Фамилия, Отчество, Email, Телефон FROM Пользователи WHERE id = ?
            """, (user_id,))
            client_id = cursor.lastrowid

            # Обновляем client_id в таблице Пользователи
            cursor.execute("UPDATE Пользователи SET client_id = ? WHERE id = ?", (client_id, user_id))
            conn.commit()

        # Получаем текущую дату и время с помощью Python
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logging.info(f"Дата и время создания бронирования: {created_at}")

        # Используем client_id для создания бронирования и вставляем дату и время создания
        cursor.execute("""
            INSERT INTO Бронирования (client_id, room_id, checkin, checkout, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (client_id, room_id, checkin, checkout, created_at))
        conn.commit()

        # Проверка вставки
        cursor.execute("SELECT created_at FROM Бронирования WHERE room_id = ? AND client_id = ? ORDER BY created_at DESC LIMIT 1", (room_id, client_id))
        created_record = cursor.fetchone()
        logging.info(f"Проверка созданного бронирования: {created_record}")

        # Обновляем статус комнаты на "ЗАБРОНИРОВАНО"
        cursor.execute("""
            UPDATE Номера SET Статус = ? WHERE id = ?
        """, (RoomStatus.ЗАБРОНИРОВАНО.value, room_id))
        conn.commit()

        # Проверка обновления статуса
        cursor.execute("SELECT Статус FROM Номера WHERE id = ?", (room_id,))
        updated_status = cursor.fetchone()
        logging.debug("Тест логирования: Это сообщение должно быть записано в файл.")
        logging.info(f"Статус комнаты после обновления: {updated_status}")



# Маршрут для подтверждения бронирования
@booking_bp.route('/confirmation', methods=['GET'])
def confirmation():
    return render_template('confirm_booking.html')

# Маршрут для получения списка всех бронирований
@booking_bp.route('/reservations', methods=['GET'])
def reservations():
    reservations_list = get_all_reservations()
    return render_template('reservations.html', reservations=reservations_list)
