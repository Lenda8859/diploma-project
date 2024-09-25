import sys
import os
import sqlite3
DATABASE = 'F:/hotel_management_project/hotel_management.db'
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from desktop_app.models.database_manager import (
    create_tables,
    get_all_rooms, update_room_status,
    add_reservation, get_all_reservations, update_reservation_status,
    add_employee, get_all_employees, update_employee_schedule,
    add_task, get_all_tasks, update_task_status,
    insert_client_in_db, update_client_in_db, get_all_clients,
    log_action, add_report, get_all_reports
)
from desktop_app.models.status_enums import RoomStatus, ReservationStatus


"""Пояснение к тесту:
Создание клиента:

Создаем клиента с помощью функции insert_client_in_db.
Проверяем, что клиент был добавлен в базу.
Изменяем данные клиента и проверяем, что изменения применились.
Работа с комнатами:


Изменяем статус номера (например, на "Забронировано").
Прохождение всех статусов бронирования и статусов номера:

Создаем бронирование для ранее созданного клиента и комнаты.
Проходим через все возможные статусы бронирования (Создано, Подтверждено, Заезд, Выезд, Завершено) и синхронно изменяем статусы номера.
Работа с сотрудниками и задачами:

Создаем сотрудника, обновляем его график, и добавляем задачи для выполнения. Также проверяем обновление статусов задач.

Таблица Задачи:

Создаём задачу для сотрудника и проверяем её добавление.
Обновляем статус задачи на "в процессе" и "завершено", проверяя изменения на каждом этапе.
Таблица logs:

Логируем действие сотрудника (например, создание бронирования).
Проверяем, что запись добавлена в таблицу logs.
Таблица Отчеты:

Создаем отчет по задачам для сотрудника.
Получаем список всех отчетов и проверяем их данные.

Проверка статусов бронирования:

После создания бронирования проверяем, что статус установлен в "Создано".
По мере изменения статусов бронирования, с помощью assert проверяем, что они изменяются на ожидаемые.
Проверка статусов номеров:

При изменении статусов номеров также добавлены проверки с использованием assert, чтобы убедиться, что статус изменился на ожидаемый (например, "Забронировано", "Занято", и т.д.).
Использование assert:

Если значение не соответствует ожиданиям, assert вызовет ошибку, и тест завершится с сообщением об ошибке.


"""

if __name__ == "__main__":
    # Создаем таблицы (если они ещё не созданы)
    create_tables()

    # === Тестирование работы с таблицей Клиентов ===
    print("\n=== Тестирование создания клиента ===")
    insert_client_in_db(last_name="Иванов", first_name="Алексей", phone="+7 999 123 45 67", email="ivanov@test.com")

    clients = get_all_clients()
    print("Все клиенты после добавления:")
    print(clients)

    print("Изменение данных клиента:")
    client_id = clients[0][0]  # Предполагаем, что ID первого клиента равен 1
    update_client_in_db(client_id, "Иванов", "Петр", "+7 999 765 43 21", "peter.ivanov@test.com")

    clients = get_all_clients()
    print("Обновленные данные клиента:")
    print(clients)

    # === Тестирование работы с номерами ===
    print("\n=== Тестирование изменения статусов номеров ===")
    rooms = get_all_rooms()
    print("Все номера по умолчанию:")
    print(rooms)

    room_number = 101  # Используем номер комнаты 101 (или другой существующий)

    print(f"Изменение статуса номера {room_number} на 'Забронировано'")
    update_room_status(room_number, RoomStatus.ЗАБРОНИРОВАНО.value)

    rooms = get_all_rooms()
    print("Обновленные данные номеров после изменения статуса:")
    print(rooms)

    # === Тестирование работы с бронированиями ===
    print("\n=== Тестирование работы с бронированиями ===")
    print(f"Создание бронирования для клиента и комнаты {room_number}")

    client_id = clients[0][0]  # ID клиента, созданного выше
    add_reservation(client_id, "2024-09-16", "2024-09-20", room_number, ReservationStatus.СОЗДАНО.value, "Не оплачено")

    reservations = get_all_reservations()
    print("Все бронирования после создания:")
    print(reservations)

    # Получаем ID только что созданного бронирования
    reservation_id = reservations[-1][0]  # Получаем ID последней записи

    # Проверяем, что бронирование создано с правильным статусом
    assert reservations[-1][5] == ReservationStatus.СОЗДАНО.value, "Статус бронирования должен быть 'Создано'"

    # Проходим все статусы бронирования и обновляем статусы номера
    status_flow = [
        (ReservationStatus.ПОДТВЕРЖДЕНО, RoomStatus.ЗАБРОНИРОВАНО),
        (ReservationStatus.ЗАЕЗД, RoomStatus.ЗАНЯТО),
        (ReservationStatus.ВЫЕЗД, RoomStatus.НА_ОБСЛУЖИВАНИИ),
        (ReservationStatus.ЗАВЕРШЕНО, RoomStatus.СВОБОДНО),
    ]

    for res_status, room_status in status_flow:
        print(f"Обновление статуса бронирования на '{res_status.value}' и комнаты на '{room_status.value}'")
        update_reservation_status(reservation_id, res_status.value)
        update_room_status(room_number, room_status.value)

        # Получаем обновленные данные бронирования и номера
        reservations = get_all_reservations()
        rooms = get_all_rooms()

        # Ищем бронирование по его ID
        reservation = next(res for res in reservations if res[0] == reservation_id)

        # Проверяем, что статус бронирования изменился
        assert reservation[5] == res_status.value, f"Ожидался статус бронирования '{res_status.value}'"

        # Проверяем, что статус комнаты изменился
        room = next(room for room in rooms if room[1] == room_number)  # Находим нужную комнату по номеру
        assert room[3] == room_status.value, f"Ожидался статус комнаты '{room_status.value}'"




    # === Тестирование работы с сотрудниками ===
    print("\n=== Тестирование работы с сотрудниками ===")
    add_employee("Коваль", "Сергей", None, "+7 999 123 45 67", "koval", "password", "Менеджер")

    employees = get_all_employees()
    print("Все сотрудники после добавления:")
    print(employees)

    update_employee_schedule(employees[0][0], "10:00-19:00")
    employees = get_all_employees()
    print("Обновленное расписание сотрудников:")
    print(employees)

    # === Тестирование работы с задачами ===
    print("\n=== Тестирование работы с задачами ===")
    add_task(employees[0][0], "Проверить чистоту номеров", "2024-09-17")

    tasks = get_all_tasks()
    print("Все задачи после добавления:")
    print(tasks)

    update_task_status(tasks[0][0], "в процессе")
    tasks = get_all_tasks()
    print("Обновленные задачи:")
    print(tasks)

    update_task_status(tasks[0][0], "завершено")
    tasks = get_all_tasks()
    print("Задачи после завершения:")
    print(tasks)

    # === Тестирование работы с логами ===
    print("\n=== Тестирование логирования действий ===")
    log_action(employees[0][0], "Создание бронирования")

    logs = []
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM logs")
        logs = cursor.fetchall()

    print("Все логи:")
    print(logs)

    # === Тестирование работы с отчетами ===
    print("\n=== Тестирование создания отчетов ===")
    add_report(employees[0][0], "Отчет по задачам", "По задачам")

    reports = get_all_reports()
    print("Все отчеты после добавления:")
    print(reports)