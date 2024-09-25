from desktop_app.models.database_manager import add_reservation, get_all_reservations, update_room_status
from tkinter import messagebox
from desktop_app.models.status_enums import ReservationStatus, RoomStatus
import sqlite3
DATABASE = 'F:/hotel_management_project/hotel_management.db'
import logging


def get_reservations():
    return get_all_reservations()

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def update_statuses(reservation_id, new_reservation_status, room_number, payment_status=None, payment_method=None):
    """Обновление статусов бронирования, номера, статуса оплаты и способа оплаты с логированием и обработкой ошибок."""
    try:
        # Открываем соединение с базой данных
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()

            # Логируем начало операции
            logging.info(f"Начало обновления бронирования {reservation_id} на статус {new_reservation_status.name}")

            # Обновляем статус бронирования
            cursor.execute("""
                UPDATE Бронирования
                SET Статус_бронирования = ?
                WHERE id = ?
            """, (new_reservation_status.value, reservation_id))

            # Определяем новый статус номера на основе нового статуса бронирования
            if new_reservation_status in [ReservationStatus.СОЗДАНО, ReservationStatus.ПОДТВЕРЖДЕНО]:
                new_room_status = RoomStatus.ЗАБРОНИРОВАНО
            elif new_reservation_status == ReservationStatus.ЗАЕЗД:
                new_room_status = RoomStatus.ЗАНЯТО
            elif new_reservation_status == ReservationStatus.ВЫЕЗД:
                new_room_status = RoomStatus.НА_ОБСЛУЖИВАНИИ
            elif new_reservation_status in [ReservationStatus.ЗАВЕРШЕНО, ReservationStatus.ОТМЕНЕНО]:
                new_room_status = RoomStatus.СВОБОДНО
            else:
                raise ValueError(f"Неизвестный статус бронирования: {new_reservation_status}")

            # Логируем новый статус комнаты
            logging.info(f"Обновление статуса комнаты {room_number} на {new_room_status.name}")

            # Обновляем статус комнаты
            cursor.execute("""
                UPDATE Номера
                SET Статус_комнаты = ?
                WHERE Номер_комнаты = ?
            """, (new_room_status.value, room_number))

            # Обновляем статус оплаты, если он предоставлен
            if payment_status:
                logging.info(f"Обновление статуса оплаты для бронирования {reservation_id} на {payment_status}")
                cursor.execute("""
                    UPDATE Бронирования
                    SET Статус_оплаты = ?
                    WHERE id = ?
                """, (payment_status, reservation_id))

            # Обновляем способ оплаты, если он предоставлен
            if payment_method:
                logging.info(f"Обновление способа оплаты для бронирования {reservation_id} на {payment_method}")
                cursor.execute("""
                    UPDATE Бронирования
                    SET Способ_оплаты = ?
                    WHERE id = ?
                """, (payment_method, reservation_id))

            # Сохраняем изменения в базе данных
            conn.commit()

            # Логируем успешное завершение операции
            logging.info(f"Бронирование {reservation_id} и комната {room_number} успешно обновлены.")

    except sqlite3.Error as e:
        # Логируем ошибку работы с базой данных
        logging.error(f"Ошибка базы данных при обновлении бронирования {reservation_id}: {e}")
        raise RuntimeError(f"Ошибка базы данных: {e}")

    except Exception as e:
        # Логируем любые другие ошибки
        logging.error(f"Произошла ошибка при обновлении бронирования {reservation_id}: {e}")
        raise RuntimeError(f"Произошла ошибка: {e}")




def create_reservation(client_id, check_in_date, check_out_date, room_id, reservation_status, payment_status, payment_method, notes):
    """Создание нового бронирования с логированием и обработкой ошибок"""
    try:
        # Открываем соединение с базой данных
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()

            # Логируем создание бронирования
            logging.info(f"Создание бронирования для клиента {client_id}, комната {room_id}, статус {reservation_status}")

            # Проверяем текущий статус комнаты
            cursor.execute("""
                SELECT Статус_комнаты FROM Номера WHERE Номер_комнаты = ?
            """, (room_id,))
            current_status = cursor.fetchone()

            if current_status and current_status[0] in [RoomStatus.ЗАБРОНИРОВАНО.value, RoomStatus.ЗАНЯТО.value, RoomStatus.НА_ОБСЛУЖИВАНИИ.value]:
                logging.warning(f"Комната {room_id} недоступна для бронирования. Статус: {current_status[0]}")
                messagebox.showwarning("Ошибка", f"Комната {room_id} недоступна для бронирования. Статус: {current_status[0]}")
                return

            # Вставляем новое бронирование в таблицу "Бронирования"
            cursor.execute("""
                INSERT INTO Бронирования (client_id, Дата_заезда, Дата_выезда, Номер_комнаты, Статус_бронирования, Статус_оплаты, Способ_оплаты, Примечания, Дата_создания)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (client_id, check_in_date, check_out_date, room_id, reservation_status, payment_status, payment_method, notes))

            # Обновляем статус комнаты на "забронировано", если бронирование успешно создано
            cursor.execute("""
                UPDATE Номера SET Статус_комнаты = ? WHERE Номер_комнаты = ?
            """, (RoomStatus.ЗАБРОНИРОВАНО.value, room_id))

            # Фиксируем изменения
            conn.commit()

            # Логируем успешное создание бронирования
            logging.info(f"Бронирование для клиента {client_id} успешно создано, комната {room_id} обновлена на статус {RoomStatus.ЗАБРОНИРОВАНО.name}")
            messagebox.showinfo("Успех", "Бронирование успешно создано, статус комнаты обновлен!")

    except sqlite3.Error as e:
        # Логируем ошибку базы данных
        logging.error(f"Ошибка базы данных при создании бронирования: {e}")
        messagebox.showerror("Ошибка базы данных", f"Не удалось создать бронирование: {e}")

    except Exception as e:
        # Логируем любую другую ошибку
        logging.error(f"Ошибка при создании бронирования: {e}")
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")


def res_check_out(client_id, room_number):
    """Функция для регистрации выезда (Check-out)"""
    print(f"Отладка: Регистрация выезда для клиента {client_id}, комната {room_number}")
    update_statuses(client_id, 'выезд')  # Изменяем статус бронирования на 'выезд'
    update_room_status(room_number, 'требуется уборка')  # Изменяем статус номера на 'требуется уборка'
    print(f"Отладка: Статус бронирования клиента {client_id} изменен на 'выезд' и статус комнаты {room_number} изменен на 'требуется уборка'")

def cancel_reservation(client_id, room_number):
    """Функция для отмены бронирования"""
    print(f"Отладка: Отмена бронирования для клиента {client_id}, комната {room_number}")
    update_statuses(client_id, 'отменено')  # Изменяем статус бронирования на 'отменено'
    update_room_status(room_number, 'свободен')  # Освобождаем номер
    print(f"Отладка: Статус бронирования клиента {client_id} изменен на 'отменено' и статус комнаты {room_number} изменен на 'свободен'")

def res_check_in(client_id, room_number):
    """Функция для регистрации заезда (Check-in)"""
    update_statuses(client_id, ReservationStatus.ЗАЕЗД.value)  # Используем Enum для статуса бронирования
    update_room_status(room_number, RoomStatus.ЗАНЯТО.value)  # Используем Enum для статуса комнаты