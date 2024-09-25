from desktop_app.models.database_manager import add_room, get_all_rooms, DATABASE
import sqlite3
from contextlib import contextmanager

@contextmanager
def db_connection():
    conn = sqlite3.connect(DATABASE)
    try:
        yield conn
    finally:
        conn.close()

def add_new_room(room_number, room_type, price):
    add_room(room_number, room_type, price)

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

def get_change_room_status(room_id, new_status):
    """Функция для обновления статуса комнаты в базе данных"""
    try:
        print(f"Отладка: Обновление статуса комнаты с ID {room_id} на {new_status}")
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Номера SET Статус_комнаты = ? WHERE id = ?
            """, (new_status, room_id))
            conn.commit()
            print(f"Статус комнаты с ID {room_id} успешно обновлен на {new_status}")
    except Exception as e:
        print(f"Ошибка при обновлении статуса комнаты с ID {room_id}: {e}")
def remove_room(room_number):
    with db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT Статус FROM Номера WHERE Номер_комнаты = ?", (room_number,))
        status = cursor.fetchone()

        if status == 'занят':
            raise ValueError("Нельзя удалить комнату, пока она занята.")


from desktop_app.models.database_manager import add_room, get_all_rooms

def add_new_room(room_number, room_type, price):
    rooms = get_all_rooms()  # Получаем список всех комнат
    if any(room[0] == room_number for room in rooms):  # Проверяем, существует ли комната с таким номером
        raise ValueError(f"Комната с номером {room_number} уже существует.")
    add_room(room_number, room_type, price)