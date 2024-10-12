from desktop_app.models.database_manager import add_reservation, get_all_reservations, update_room_status
from tkinter import messagebox
from desktop_app.models.status_enums import ReservationStatus, RoomStatus
import sqlite3
import datetime
import sys

DATABASE = 'F:/Hotel Management System/hotel_management.db'
import logging


def get_reservations():
    return get_all_reservations()


def update_statuses(reservation_id, new_reservation_status, room_number, payment_status=None, payment_method=None,
                    check_in_date=None, check_out_date=None):
    """Обновление статусов бронирования, номера, статуса оплаты, способа оплаты и дат с логированием и обработкой ошибок."""
    try:
        # Открываем соединение с базой данных
        with sqlite3.connect(DATABASE, timeout=10) as conn:
            cursor = conn.cursor()

            # Логируем начало операции
            logging.info(f"Начало обновления бронирования {reservation_id} на статус {new_reservation_status.name}")

            # Формируем запрос для обновления полей
            query = """
                UPDATE Бронирования
                SET Статус_бронирования = ?
            """
            params = [new_reservation_status.value]

            if check_in_date:
                query += ", Дата_заезда = ?"
                params.append(check_in_date)

            if check_out_date:
                query += ", Дата_выезда = ?"
                params.append(check_out_date)

            query += " WHERE id = ?"
            params.append(reservation_id)

            # Обновляем статус бронирования и даты
            cursor.execute(query, params)

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
###########################################################################################################################

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug("Логирование инициализировано")  # Добавим тестовое сообщение

# Обновленная версия функции create_reservation с логикой проверки пересечений
def create_reservation(client_id, check_in_date, check_out_date, room_id, reservation_status, payment_status,
                       payment_method, notes):
    """Создание нового бронирования с отладочными сообщениями"""
    logging.debug("Функция create_reservation вызвана")
    try:
        logging.info(f"Пытаемся создать бронирование для комнаты {room_id} с {check_in_date} по {check_out_date}")

        # Открываем соединение с базой данных
        with sqlite3.connect(DATABASE, timeout=10) as conn:
            cursor = conn.cursor()

            # Проверяем пересечения с существующими бронированиями для этой комнаты
            logging.info(f"Проверяем существующие бронирования для комнаты {room_id}")
            cursor.execute("""
                SELECT Дата_заезда, Дата_выезда FROM Бронирования WHERE Номер_комнаты = ?
            """, (room_id,))
            existing_reservations = cursor.fetchall()

            # Проверяем каждое существующее бронирование на пересечение
            for existing_check_in, existing_check_out in existing_reservations:
                logging.debug(f"Существующее бронирование: {existing_check_in} - {existing_check_out}")
                if check_in_date <= existing_check_out and check_out_date >= existing_check_in:
                    logging.warning(
                        f"Пересечение с бронированием: {existing_check_in} - {existing_check_out}. Бронирование отменено.")
                    messagebox.showwarning(
                        "Ошибка",
                        f"Комната {room_id} уже забронирована с {existing_check_in} по {existing_check_out}."
                    )
                    return

            logging.info(f"Нет пересечений для бронирования с {check_in_date} по {check_out_date}. Продолжаем процесс.")

            # Проверяем текущий статус комнаты
            logging.info(f"Проверяем статус комнаты {room_id}")
            cursor.execute("""
                SELECT Статус_комнаты FROM Номера WHERE Номер_комнаты = ?
            """, (room_id,))
            current_status = cursor.fetchone()
            logging.debug(f"Текущий статус комнаты: {current_status[0]}")

            if current_status and current_status[0] in [RoomStatus.ЗАБРОНИРОВАНО.value, RoomStatus.ЗАНЯТО.value]:
                logging.info(f"Комната {room_id} забронирована, но проверяем на активное бронирование.")
            else:
                # Обновляем статус комнаты
                room_status = RoomStatus.ЗАБРОНИРОВАНО.value if reservation_status != ReservationStatus.ЗАЕЗД.value else RoomStatus.ЗАНЯТО.value
                logging.info(f"Обновляем статус комнаты {room_id} на {room_status}")
                cursor.execute("""
                    UPDATE Номера SET Статус_комнаты = ? WHERE Номер_комнаты = ?
                """, (room_status, room_id))

            # Вставляем новое бронирование в таблицу "Бронирования"
            logging.info(f"Вставляем новое бронирование для клиента {client_id} с {check_in_date} по {check_out_date}")
            cursor.execute("""
                INSERT INTO Бронирования (client_id, Дата_заезда, Дата_выезда, Номер_комнаты, Статус_бронирования, Статус_оплаты, Способ_оплаты, Примечания, Дата_создания)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (client_id, check_in_date, check_out_date, room_id, reservation_status, payment_status, payment_method,
                  notes))

            # Фиксируем изменения
            conn.commit()
            logging.info(f"Бронирование для комнаты {room_id} успешно создано.")
            messagebox.showinfo("Успех", "Бронирование успешно создано!")

    except sqlite3.Error as e:
        logging.error(f"Ошибка базы данных: {e}")
        messagebox.showerror("Ошибка базы данных", f"Не удалось создать бронирование: {e}")

    except Exception as e:
        logging.error(f"Ошибка при создании бронирования: {e}")
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

# def create_reservation(client_id, check_in_date, check_out_date, room_id, reservation_status, payment_status, payment_method, notes):
#     """Создание нового бронирования с проверкой на пересечение дат и корректировкой статуса комнаты для активных бронирований"""
#     try:
#         # Открываем соединение с базой данных
#         with sqlite3.connect(DATABASE, timeout=10) as conn:
#             cursor = conn.cursor()
#
#             # Логируем создание бронирования
#             logging.info(f"Создание бронирования для клиента {client_id}, комната {room_id}, статус {reservation_status}")
#
#             # Проверяем пересечения с существующими бронированиями для этой комнаты
#             cursor.execute("""
#                 SELECT Дата_заезда, Дата_выезда FROM Бронирования WHERE Номер_комнаты = ?
#             """, (room_id,))
#             existing_reservations = cursor.fetchall()
#
#             for existing_check_in, existing_check_out in existing_reservations:
#                 # Проверка на пересечение дат: новое бронирование должно начинаться после даты выезда предыдущего
#                 if check_in_date <= existing_check_out:
#                     logging.warning(f"Пересечение с существующим бронированием: {existing_check_in} - {existing_check_out}")
#                     messagebox.showwarning(
#                         "Ошибка",
#                         f"Комната {room_id} уже забронирована с {existing_check_in} по {existing_check_out}. Следующее бронирование возможно с {existing_check_out + timedelta(days=1)}."
#                     )
#                     return
#
#             # Проверяем текущий статус комнаты только для активных бронирований (если текущее бронирование активно)
#             cursor.execute("""
#                 SELECT Статус_комнаты FROM Номера WHERE Номер_комнаты = ?
#             """, (room_id,))
#             current_status = cursor.fetchone()
#
#             # Обновляем статус комнаты только для активных бронирований
#             # Если текущая дата попадает в диапазон бронирования, комната считается активной
#             today = datetime.now().date()
#             if check_in_date <= today <= check_out_date:
#                 if reservation_status == ReservationStatus.ЗАЕЗД.value:
#                     room_status = RoomStatus.ЗАНЯТО.value
#                 else:
#                     room_status = RoomStatus.ЗАБРОНИРОВАНО.value
#
#                 # Обновляем статус комнаты
#                 cursor.execute("""
#                     UPDATE Номера SET Статус_комнаты = ? WHERE Номер_комнаты = ?
#                 """, (room_status, room_id))
#
#             # Вставляем новое бронирование в таблицу "Бронирования"
#             cursor.execute("""
#                 INSERT INTO Бронирования (client_id, Дата_заезда, Дата_выезда, Номер_комнаты, Статус_бронирования, Статус_оплаты, Способ_оплаты, Примечания, Дата_создания)
#                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
#             """, (client_id, check_in_date, check_out_date, room_id, reservation_status, payment_status, payment_method, notes))
#
#             # Фиксируем изменения
#             conn.commit()
#
#             # Логируем успешное создание бронирования
#             logging.info(f"Бронирование для клиента {client_id} успешно создано, комната {room_id} обновлена на статус {RoomStatus.ЗАБРОНИРОВАНО.name}")
#             messagebox.showinfo("Успех", "Бронирование успешно создано, статус комнаты обновлен!")
#
#     except sqlite3.Error as e:
#         # Логируем ошибку базы данных
#         logging.error(f"Ошибка базы данных при создании бронирования: {e}")
#         messagebox.showerror("Ошибка базы данных", f"Не удалось создать бронирование: {e}")
#
#     except Exception as e:
#         # Логируем любую другую ошибку
#         logging.error(f"Ошибка при создании бронирования: {e}")
#         messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")




###########################################################################################################################


def res_check_out(client_id, room_number):
    """Функция для регистрации выезда (Check-out)"""
    #print(f"Отладка: Регистрация выезда для клиента {client_id}, комната {room_number}")
    update_statuses(client_id, 'выезд')  # Изменяем статус бронирования на 'выезд'
    update_room_status(room_number, 'требуется уборка')  # Изменяем статус номера на 'требуется уборка'
    #print(f"Отладка: Статус бронирования клиента {client_id} изменен на 'выезд' и статус комнаты {room_number} изменен на 'требуется уборка'")

def cancel_reservation(client_id, room_number):
    """Функция для отмены бронирования"""
    #print(f"Отладка: Отмена бронирования для клиента {client_id}, комната {room_number}")
    update_statuses(client_id, 'отменено')  # Изменяем статус бронирования на 'отменено'
    update_room_status(room_number, 'свободен')  # Освобождаем номер
    #print(f"Отладка: Статус бронирования клиента {client_id} изменен на 'отменено' и статус комнаты {room_number} изменен на 'свободен'")

def res_check_in(client_id, room_number):
    """Функция для регистрации заезда (Check-in)"""
    update_statuses(client_id, ReservationStatus.ЗАЕЗД.value)  # Используем Enum для статуса бронирования
    update_room_status(room_number, RoomStatus.ЗАНЯТО.value)  # Используем Enum для статуса комнаты