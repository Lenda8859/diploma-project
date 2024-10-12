from desktop_app.models.database_manager import add_room, get_all_rooms, DATABASE, update_room
import datetime
import sqlite3
from contextlib import contextmanager
import logging
import sys



@contextmanager
def db_connection():
    conn = sqlite3.connect(DATABASE, timeout=10)
    try:
        yield conn
    finally:
        conn.close()

def add_new_room(room_number, room_type, room_status, price, description, capacity, area, amenities, notes):
    add_room(room_number, room_type, room_status, price, description, capacity, area, amenities, notes)

def get_rooms():
    try:
        with db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Номер_комнаты, Тип, Статус FROM Номера")
            rooms = cursor.fetchall()
            if not rooms:
                print("Нет данных о номерах.")
            return rooms
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return None
##################################################################################################################
# def get_change_room_status(room_id, new_status):
#     """Функция для обновления статуса комнаты в базе данных"""
#     try:
#         print(f"Отладка: Обновление статуса комнаты с ID {room_id} на {new_status}")
#         with sqlite3.connect(DATABASE, timeout=10) as conn:
#             cursor = conn.cursor()
#             cursor.execute("""
#                 UPDATE Номера SET Статус_комнаты = ? WHERE id = ?
#             """, (new_status, room_id))
#             conn.commit()
#             print(f"Статус комнаты с ID {room_id} успешно обновлен на {new_status}")
#     except Exception as e:
#         print(f"Ошибка при обновлении статуса комнаты с ID {room_id}: {e}")

# def get_change_room_status(room_id, new_status, check_in_date, check_out_date):
#     """Функция для обновления статуса комнаты, только если бронирование активно"""
#     try:
#         # Проверяем текущую дату
#         today = datetime.now().date()
#
#         # Статус комнаты изменяется только если текущее бронирование активно
#         if check_in_date <= today <= check_out_date:
#             print(f"Отладка: Обновление статуса комнаты с ID {room_id} на {new_status}")
#             with sqlite3.connect(DATABASE, timeout=10) as conn:
#                 cursor = conn.cursor()
#                 cursor.execute("""
#                     UPDATE Номера SET Статус_комнаты = ? WHERE id = ?
#                 """, (new_status, room_id))
#                 conn.commit()
#                 print(f"Статус комнаты с ID {room_id} успешно обновлен на {new_status}")
#         else:
#             print(f"Бронирование еще не активно. Статус комнаты {room_id} не обновлен.")
#     except Exception as e:
#         print(f"Ошибка при обновлении статуса комнаты с ID {room_id}: {e}")

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug("Логирование инициализировано")  # Добавим тестовое сообщение

def get_change_room_status(room_id, new_status, check_in_date, check_out_date):
    """Обновление статуса комнаты с отладкой"""
    logging.debug("Функция get_change_room_status вызвана")
    try:
        today = datetime.now().date()
        logging.info(f"Проверяем необходимость обновления статуса комнаты {room_id}")

        # Статус обновляется, только если бронирование активно
        if check_in_date <= today <= check_out_date:
            logging.info(f"Обновляем статус комнаты {room_id} на {new_status}")
            with sqlite3.connect(DATABASE, timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE Номера SET Статус_комнаты = ? WHERE id = ?
                """, (new_status, room_id))
                conn.commit()
                logging.info(f"Статус комнаты {room_id} успешно обновлен на {new_status}")
        else:
            logging.info(f"Бронирование еще не активно. Статус комнаты {room_id} не обновлен.")
    except Exception as e:
        logging.error(f"Ошибка при обновлении статуса комнаты: {e}")

################################################################################################################
def remove_room(room_number):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT Статус FROM Номера WHERE Номер_комнаты = ?", (room_number,))
        status = cursor.fetchone()

        if status == 'занят':
            raise ValueError("Нельзя удалить комнату, пока она занята.")


from desktop_app.models.database_manager import add_room, get_all_rooms


def add_new_room(room_number, room_type, room_status, price, description, capacity, area, amenities, notes):
    """
    Добавление нового номера с расширенными параметрами.
    """
    rooms = get_all_rooms()  # Получаем список всех комнат
    if any(room[0] == room_number for room in rooms):  # Проверяем, существует ли комната с таким номером
        raise ValueError(f"Комната с номером {room_number} уже существует.")

    # Добавляем новый номер с расширенными параметрами
    add_room(room_number, room_type, room_status, price, description, capacity, area, amenities, notes)