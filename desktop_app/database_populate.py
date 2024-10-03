import sqlite3
from datetime import datetime, timedelta
import random

DATABASE = 'F:/Hotel Management System/hotel_management.db'  # Проверьте правильный путь к вашей базе данных


def add_test_data():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Добавление клиентов
        print("Добавляем клиентов...")
        for i in range(1, 21):  # Создаем 20 клиентов
            cursor.execute("""
                INSERT INTO Клиенты (Фамилия, Имя, Отчество, Телефон, Email, Адрес, Примечания)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (f'Фамилия_{i}', f'Имя_{i}', f'Отчество_{i}', f'+790000000{i}', f'email_{i}@example.com', f'Адрес_{i}',
                  f'Заметка_{i}'))
        conn.commit()

        # Получаем ID всех клиентов
        cursor.execute("SELECT id FROM Клиенты")
        client_ids = [row[0] for row in cursor.fetchall()]

        # Получить уже существующие номера комнат
        # Запрос к базе данных с учетом номеров 101-110, 201-208, 301-306
        cursor.execute("""
                   SELECT
                       Дата_заезда,
                       SUM(CASE WHEN Номера.Статус_комнаты = 'свободно' THEN 1 ELSE 0 END) AS свободные,
                       SUM(CASE WHEN Номера.Статус_комнаты = 'занято' THEN 1 ELSE 0 END) AS занятые,
                       SUM(CASE WHEN Номера.Статус_комнаты = 'на обслуживании' THEN 1 ELSE 0 END) AS на_обслуживании
                   FROM Номера
                   LEFT JOIN Бронирования ON Номера.Номер_комнаты = Бронирования.Номер_комнаты
                   WHERE Дата_заезда BETWEEN ? AND ?
                   AND Номера.Номер_комнаты IN (101, 102, ..., 110, 201, 202, ..., 208, 301, 302, ..., 306)  -- Укажите все нужные номера
                   GROUP BY Дата_заезда
               """, (start_date, end_date))

        # Добавление номеров
        print("Добавляем номера...")
        room_types = ['Стандарт', 'Сьют', 'Делюкс']
        room_status = ['свободно', 'забронировано', 'занято', 'на обслуживании']

        for room_number in range(101, 121):  # Пусть у нас будет 20 номеров
            # Проверка, существует ли уже номер комнаты
            if room_number not in existing_room_numbers:
                cursor.execute("""
                    INSERT INTO Номера (Номер_комнаты, Тип_комнаты, Статус_комнаты, Стоимость, Описание)
                    VALUES (?, ?, ?, ?, ?)
                """, (room_number, random.choice(room_types), random.choice(room_status), random.uniform(1000, 5000),
                      f'Описание номера {room_number}'))
        conn.commit()

        # Получаем ID всех номеров
        cursor.execute("SELECT Номер_комнаты FROM Номера")
        room_numbers = [row[0] for row in cursor.fetchall()]

        # Добавление тестовых бронирований на 90 дней
        print("Добавляем бронирования...")
        start_date = datetime.strptime('2024-06-01', '%Y-%m-%d')
        payment_statuses = ['Не оплачено', 'Частично оплачено', 'Оплачено']
        booking_statuses = ['Создано', 'Подтверждено', 'Заезд', 'Выезд', 'Завершено', 'Отменено']
        payment_methods = ['Наличные', 'Банковская карта', 'Онлайн-платеж', 'Безналичный расчет']

        for room_number in room_numbers:
            date = start_date
            while date < start_date + timedelta(days=90):
                client_id = random.choice(client_ids)
                stay_duration = random.randint(5, 10)  # Случайное количество дней проживания
                end_date = date + timedelta(days=stay_duration)
                status_payment = random.choice(payment_statuses)
                booking_status = random.choice(booking_statuses)
                payment_method = random.choice(payment_methods)


                cursor.execute("""
                    INSERT INTO Бронирования (client_id, Номер_комнаты, Дата_заезда, Дата_выезда, Статус_бронирования, Статус_оплаты, Способ_оплаты)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (client_id, room_number, date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), booking_status,
                      status_payment, payment_method))

                # Сдвигаем дату на случайный период, чтобы моделировать регулярные бронирования
                date = end_date + timedelta(days=random.randint(1, 3))

        conn.commit()

        # Добавление сотрудников
        print("Добавляем сотрудников...")
        employees = [
            ('Иванов', 'Иван', 'Иванович', '+7901000001', 'ivanov', 'password1', 'менеджер', 'полный день', 'менеджер'),
            ('Петров', 'Петр', 'Петрович', '+7901000002', 'petrov', 'password2', 'администратор', 'сменный',
             'администратор'),
            ('Сидорова', 'Светлана', 'Сергеевна', '+7901000003', 'sidorova', 'password3', 'сотрудник', 'гибкий',
             'администратор')
        ]
        for surname, name, patronymic, phone, username, password, position, schedule, role in employees:
            cursor.execute("""
                INSERT INTO Сотрудники (Фамилия, Имя, Отчество, Телефон, username, password, Должность, График, Роль)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (surname, name, patronymic, phone, username, password, position, schedule, role))
        conn.commit()

        # Получаем ID всех сотрудников
        cursor.execute("SELECT id FROM Сотрудники")
        employee_ids = [row[0] for row in cursor.fetchall()]

        # Добавление задач на 90 дней
        print("Добавляем задачи...")
        task_descriptions = ['Уборка комнаты', 'Ремонт оборудования', 'Проверка состояния номера',
                             'Подготовка к заселению']
        start_task_date = start_date

        for i in range(90):  # На каждый день создаем задачу
            task_date = start_task_date + timedelta(days=i)
            employee_id = random.choice(employee_ids)
            task_description = random.choice(task_descriptions)
            task_status = random.choice(['ожидание', 'в процессе', 'завершено'])

            cursor.execute("""
                INSERT INTO Задачи (Сотрудник_id, Описание, Статус, Срок_исполнения)
                VALUES (?, ?, ?, ?)
            """, (employee_id, f'{task_description} на {task_date.strftime("%Y-%m-%d")}', task_status,
                  task_date.strftime('%Y-%m-%d')))

        conn.commit()
        print("Данные успешно добавлены.")



def delete_room(room_number):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Удаление записей из связанных таблиц
        cursor.execute("DELETE FROM Бронирования WHERE Номер_комнаты = ?", (room_number,))
        cursor.execute("DELETE FROM Номера WHERE Номер_комнаты = ?", (room_number,))

        conn.commit()
        print(f"Номер комнаты {room_number} успешно удален.")


def clean_related_data(room_number):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Удаляем записи из связанных таблиц, если такие записи существуют
        cursor.execute("DELETE FROM Бронирования WHERE Номер_комнаты = ?", (room_number,))
        cursor.execute(
            "DELETE FROM Оплата WHERE Бронирование_id IN (SELECT id FROM Бронирования WHERE Номер_комнаты = ?)",
            (room_number,))
        # Добавьте очистку любых других таблиц, которые могут быть связаны с комнатой 111

        conn.commit()
        print(f"Все связанные с номером {room_number} записи успешно удалены.")


def check_rooms_status():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Проверка статусов номеров
        cursor.execute("""
            SELECT Номер_комнаты, Статус_комнаты
            FROM Номера
            WHERE Статус_комнаты NOT IN ('свободно', 'забронировано', 'занято', 'на обслуживании')
        """)
        invalid_rooms = cursor.fetchall()

        if invalid_rooms:
            print("Обнаружены некорректные статусы в таблице Номера:")
            for room in invalid_rooms:
                print(f"Номер комнаты: {room[0]}, Статус: {room[1]}")
        else:
            print("Все статусы номеров корректны.")


def check_bookings_status():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Проверка статусов бронирования
        cursor.execute("""
            SELECT id, Статус_бронирования
            FROM Бронирования
            WHERE Статус_бронирования NOT IN ('Создано', 'Подтверждено', 'Заезд', 'Выезд', 'Завершено', 'Отменено')
        """)
        invalid_bookings = cursor.fetchall()

        if invalid_bookings:
            print("Обнаружены некорректные статусы бронирований:")
            for booking in invalid_bookings:
                print(f"ID бронирования: {booking[0]}, Статус: {booking[1]}")
        else:
            print("Все статусы бронирований корректны.")

        # Проверка статусов оплаты
        cursor.execute("""
            SELECT id, Статус_оплаты
            FROM Бронирования
            WHERE Статус_оплаты NOT IN ('Не оплачено', 'Частично оплачено', 'Оплачено')
        """)
        invalid_payments = cursor.fetchall()

        if invalid_payments:
            print("Обнаружены некорректные статусы оплат:")
            for payment in invalid_payments:
                print(f"ID бронирования: {payment[0]}, Статус оплаты: {payment[1]}")
        else:
            print("Все статусы оплат корректны.")


def check_room_existence_in_bookings():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Проверка на существование номеров в таблице Бронирования
        cursor.execute("""
            SELECT DISTINCT Номер_комнаты
            FROM Бронирования
            WHERE Номер_комнаты NOT IN (SELECT Номер_комнаты FROM Номера)
        """)
        invalid_room_references = cursor.fetchall()

        if invalid_room_references:
            print("Обнаружены ссылки на несуществующие номера в таблице Бронирования:")
            for room in invalid_room_references:
                print(f"Номер комнаты: {room[0]}")
        else:
            print("Все номера в бронированиях существуют в таблице Номера.")



def clear_tables():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Очистка таблицы бронирований
        cursor.execute("DELETE FROM Бронирования")
        # Если есть другие связанные таблицы, такие как Оплата, История_задач, их тоже можно очистить
        #cursor.execute("DELETE FROM Оплата")
        #cursor.execute("DELETE FROM Клиенты")
        cursor.execute("DELETE FROM Задачи")

        # Подтверждаем изменения
        conn.commit()
        print("Таблицы Бронирования, Оплата и Задачи, Клиенты успешно очищены.")


def add_test_numer():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Получаем ID всех существующих номеров
        cursor.execute("SELECT Номер_комнаты FROM Номера")
        room_numbers = [row[0] for row in cursor.fetchall()]

        # Проверка на существование номеров
        if not room_numbers:
            print("Не найдено номеров для создания бронирований.")
            return

        # Получаем ID всех клиентов
        cursor.execute("SELECT id FROM Клиенты")
        client_ids = [row[0] for row in cursor.fetchall()]

        # Проверка на существование клиентов
        if not client_ids:
            print("Не найдено клиентов для создания бронирований.")
            return

        # Добавление корректных бронирований
        print("Добавляем бронирования...")
        start_date = datetime.strptime('01.06.24', "%d.%m.%y")
        end_period = start_date + timedelta(days=90)
        statuses = ['Подтверждено', 'Завершено']
        payment_statuses = ['Оплачено', 'Не оплачено']

        # Полная загрузка гостиницы: бронирование всех номеров на весь период
        for room_number in room_numbers:
            date = start_date
            while date < end_period:
                stay_duration = random.randint(5, 7)  # Случайное количество дней проживания
                end_date = date + timedelta(days=stay_duration)

                # Получаем случайного клиента из списка существующих
                random_client_id = random.choice(client_ids)

                cursor.execute("""
                       INSERT INTO Бронирования (Номер_комнаты, Дата_заезда, Дата_выезда, client_id, Статус_бронирования, Статус_оплаты)
                       VALUES (?, ?, ?, ?, ?, ?)
                   """, (room_number, date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), random_client_id,
                         random.choice(statuses), random.choice(payment_statuses)))

                # Следующее бронирование начинается на следующий день после предыдущего
                date = end_date + timedelta(days=1)

        conn.commit()
        print("Бронирования успешно добавлены.")

        # Получаем ID всех сотрудников
        cursor.execute("SELECT id FROM Сотрудники")
        employee_ids = [row[0] for row in cursor.fetchall()]

        # Проверка на существование сотрудников
        if not employee_ids:
            print("Не найдено сотрудников для создания задач.")
            return

        # Добавление задач на 90 дней
        print("Добавляем задачи...")
        task_descriptions = ['Регистрация нового клиента', 'Уборка номера', 'Проверка состояния номеров',
                             'Обслуживание номера', 'Отчет по бронированиям']
        start_task_date = start_date

        for i in range(90):  # На каждый день создаем задачу
            task_date = start_task_date + timedelta(days=i)
            employee_id = random.choice(employee_ids)
            task_type = random.choice(task_descriptions)
            task_status = random.choice(['ожидание', 'в процессе', 'завершено'])

            cursor.execute("""
                   INSERT INTO Задачи (Тип_задачи, Сотрудник_id, Описание, Статус, Срок_исполнения)
                   VALUES (?, ?, ?, ?, ?)
               """, (employee_id, f'{task_type} на {task_date.strftime("%d.%m.%y")}', task_type, task_status,
                     task_date.strftime('%d.%m.%y')))
        conn.commit()

        print("Задачи успешно добавлены.")

def add_test_client():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        print("Добавляем клиентов...")
        for i in range(1, 21):  # Создаем 20 клиентов
            cursor.execute("""
                INSERT INTO Клиенты (Фамилия, Имя, Отчество, Телефон, Email, Адрес, Примечания)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (f'Фамилия_{i}', f'Имя_{i}', f'Отчество_{i}', f'+7 921 00 10 2{i}', f'email_{i}@example.com', f'Адрес_{i}',
                  f'Заметка_{i}'))
        conn.commit()

        # Получаем ID всех клиентов
        cursor.execute("SELECT id FROM Клиенты")
        client_ids = [row[0] for row in cursor.fetchall()]


if __name__ == "__main__":
    clear_tables()
    #add_test_client()
    #add_test_numer()
    #delete_room(114)
    # # Удаляем связанные записи с номером 111
    # clean_related_data(117)
    # clean_related_data(118)
    # clean_related_data(119)
    # clean_related_data(120)
    # check_rooms_status()
    # check_bookings_status()
    # check_room_existence_in_bookings()

