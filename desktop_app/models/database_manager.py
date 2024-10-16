import sqlite3
import hashlib
import logging
from datetime import datetime, timedelta
import random
from desktop_app.models.status_enums import ReservationStatus

DATABASE = 'F:\Hotel Management System/hotel_management.db'


def create_tables():
    """Создание таблиц, если они не существуют"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()

        # Открываем SQL-файл для выполнения миграций
        with open('F:/Hotel Management System/migrations/create_tables.sql', 'r', encoding='utf-8') as sql_file:
            sql_script = sql_file.read()

        # Выполняем SQL скрипт
        cursor.executescript(sql_script)
        conn.commit()

        print("Таблицы успешно созданы.")



##************************************************ Клиенты *****************************************************************##



# Добавление нового клиента
def insert_client_in_db(last_name, first_name, phone, middle_name=None, email=None, address=None, notes=None):
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()

        # Проверяем, существует ли клиент с таким телефоном
        cursor.execute("SELECT * FROM Клиенты WHERE Телефон = ?", (phone,))
        existing_client = cursor.fetchone()

        if existing_client:
            print("Клиент с таким телефоном уже существует.")
            return False  # Возвращаем False, если клиент уже есть

        # Если клиента нет, добавляем нового
        cursor.execute("""
            INSERT INTO Клиенты (Фамилия, Имя, Отчество, Телефон, Email, Адрес, Примечания)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (last_name, first_name, middle_name, phone, email, address, notes))
        conn.commit()
        return cursor.lastrowid
        print("Клиент успешно добавлен.")
        return True  # Возвращаем True, если клиент успешно добавлен

# Получение списка всех клиентов
def get_all_clients():
    """Получение списка всех клиентов из базы данных"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ID, Фамилия, Имя, Отчество, Телефон, Email, Дата_регистрации, Адрес, Примечания
            FROM Клиенты
        """)
        clients = cursor.fetchall()
        return clients

# Поиск клиента по телефону
def find_client_by_phone(phone):
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Клиенты WHERE Телефон = ?", (phone,))
        client = cursor.fetchone()
        return client

def get_client_full_name(client_id):
    """Возвращает полное имя клиента по его client_id"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Фамилия || ' ' || Имя || ' ' || Отчество 
            FROM Клиенты 
            WHERE id = ?
        """, (client_id,))
        result = cursor.fetchone()
        return result[0] if result else "Неизвестный клиент"


# Обновление клиента
def update_client_in_db(client_id, last_name, first_name, phone, email):
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Клиенты SET Фамилия = ?, Имя = ?, Телефон = ?, Email = ?
            WHERE id = ?
        """, (last_name, first_name, phone, email, client_id))
        conn.commit()
        print(f"Клиент с id {client_id} успешно обновлен.")

#сохранения пользователя в базу данных
def add_client(first_name, last_name, middle_name, email, password):
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Клиенты (Имя, Фамилия, Отчество, email, password)
            VALUES (?, ?, ?, ?, ?)
        """, (first_name, last_name, middle_name, email, password))
        conn.commit()

######################################  Пользователи   ##################################################################
def insert_user_in_db(first_name, last_name, email, phone, hashed_password):
    try:
        with sqlite3.connect('F:/Hotel Management System/hotel_management.db', timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Пользователи (Имя, Фамилия, Email, Телефон, Пароль)
                VALUES (?, ?, ?, ?, ?)
            """, (first_name, last_name, email, phone, hashed_password))
            conn.commit()
            return cursor.lastrowid  # Возвращает ID нового пользователя
    except sqlite3.IntegrityError:
        return None  # Возвращает None, если пользователь с таким email уже существует
##*******************************************************  Номера  ************************************************************##

def initialize_rooms():
    """Инициализация базы данных с номерами комнат: 10 стандартных, 8 сьютов, 6 делюксов."""
    conn = sqlite3.connect(DATABASE, timeout=10)
    cursor = conn.cursor()

    # Проверяем, есть ли уже номера в базе данных
    cursor.execute("SELECT COUNT(*) FROM Номера")
    count = cursor.fetchone()[0]

    if count == 0:  # Если номера не были добавлены ранее
        rooms = []

        # Добавляем 10 стандартных комнат
        for i in range(1, 11):  # Номера с 101 по 110
            room_number = 100 + i
            rooms.append((room_number, "Стандарт", "свободно", 3000, "Стандартная комната"))

        # Добавляем 8 сьютов
        for i in range(1, 9):  # Номера с 201 по 208
            room_number = 200 + i
            rooms.append((room_number, "Сьют", "свободно", 5000, "Сьют комната"))

        # Добавляем 6 делюксов
        for i in range(1, 7):  # Номера с 301 по 306
            room_number = 300 + i
            rooms.append((room_number, "Делюкс", "свободно", 8000, "Делюкс комната"))

        # Добавляем комнаты в таблицу Номера
        cursor.executemany("INSERT INTO Номера (Номер_комнаты, Тип_комнаты, Статус_комнаты, Стоимость, Описание) VALUES (?, ?, ?, ?, ?)", rooms)
        conn.commit()

    conn.close()


# Добавление номера
def add_room(room_number, room_type, room_status, price, description, capacity, area, amenities, notes):
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Номера (Номер_комнаты, Тип_комнаты, Статус_комнаты, Стоимость, Описание, Вместимость, Площадь, Удобства, Примечания)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (room_number, room_type, room_status, price, description, capacity, area, amenities, notes))
        conn.commit()
        print(f"Номер {room_number} успешно добавлен.")

# Получение всех номеров
def get_all_rooms():
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
             SELECT id, Номер_комнаты, Тип_комнаты, Статус_комнаты, Стоимость, Описание, Вместимость, Площадь, Удобства FROM Номера
        """)
        rooms = cursor.fetchall()
        return rooms

# Изменение статуса номера
def update_room(room_id, room_number, room_type, room_status, price, description, capacity, area, amenities, notes):
    """
    Обновление данных существующего номера.
    """
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Номера
            SET Номер_комнаты = ?, Тип_комнаты = ?, Статус_комнаты = ?, Стоимость = ?, Описание = ?, Вместимость = ?, Площадь = ?, Удобства = ?
            WHERE id = ?
        """, (room_number, room_type, room_status, price, description, capacity, area, amenities, room_id))
        conn.commit()
        print(f"Номер с ID {room_id} успешно обновлен.")

def update_room_status(room_number, new_status):
    """Обновление статуса комнаты"""
    try:
        print(f"Отладка: Попытка обновить статус комнаты {room_number} на {new_status}")
        with sqlite3.connect(DATABASE, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Номера SET Статус_комнаты = ? WHERE Номер_комнаты = ?
            """, (new_status, room_number))
            conn.commit()
            print(f"Статус комнаты {room_number} успешно обновлен на {new_status}")
    except Exception as e:
        print(f"Ошибка при обновлении статуса комнаты: {e}")


def room_exists(room_number):
    """Проверка, существует ли комната с таким номером"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Номера WHERE Номер_комнаты = ?", (room_number,))
        result = cursor.fetchone()
        return result[0] > 0  # Если количество записей больше 0, комната существует


def get_room_counts():
    """Возвращает количество комнат по типу и статусу"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Тип_комнаты, Статус_комнаты, COUNT(*)
            FROM Номера
            GROUP BY Тип_комнаты, Статус_комнаты
        """)
        room_counts = cursor.fetchall()  # Возвращаем сгруппированные данные
    return room_counts

def get_rooms_filtered(room_type=None, room_status=None, price_max=None):
    """Получение списка номеров с фильтрацией по типу, статусу и максимальной цене"""
    query = "SELECT * FROM Номера WHERE 1=1"
    params = []

    if room_type:
        query += " AND Тип_комнаты = ?"
        params.append(room_type)
    if room_status:
        query += " AND Статус_комнаты = ?"
        params.append(room_status)
    if price_max:
        query += " AND Стоимость <= ?"
        params.append(price_max)

    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

def add_new_columns_to_rooms():
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(Номера);")
        columns = [column[1] for column in cursor.fetchall()]

        if 'Вместимость' not in columns:
            cursor.execute("ALTER TABLE Номера ADD COLUMN Вместимость INTEGER;")
            print("Колонка 'Вместимость' добавлена в таблицу 'Номера'.")

        if 'Площадь' not in columns:
            cursor.execute("ALTER TABLE Номера ADD COLUMN Площадь REAL;")
            print("Колонка 'Площадь' добавлена в таблицу 'Номера'.")

        if 'Удобства' not in columns:
            cursor.execute("ALTER TABLE Номера ADD COLUMN Удобства TEXT;")
            print("Колонка 'Удобства' добавлена в таблицу 'Номера'.")

        conn.commit()





##********************************************************  Бронирование  ***************************************************##
from desktop_app.models.status_enums import ReservationStatus

# Настройка логирования
logging.basicConfig(filename='F:/Hotel Management System/logs/reservation_log.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def add_reservation(client_id, check_in_date, check_out_date, room_number, booking_status, payment_status,
                    payment_method=None, additional_info=None):
    """
    Добавляет бронирование в базу данных.

    Параметры:
    - client_id: ID клиента.
    - check_in_date: Дата заезда.
    - check_out_date: Дата выезда.
    - room_id: ID комнаты.
    - booking_status: Статус бронирования (например, "Создано", "Подтверждено").
    - payment_status: Статус оплаты (например, "Не оплачено", "Частично оплачено", "Оплачено").
    - payment_method: Способ оплаты (необязательный параметр).
    - additional_info: Дополнительная информация о бронировании (необязательный параметр).

    Логирует каждую операцию и ошибки при возникновении.
    """
    logging.debug(
        f"Попытка добавить бронирование: client_id={client_id}, check_in_date={check_in_date}, "
        f"check_out_date={check_out_date}, room_number={room_number}, booking_status={booking_status}, "
        f"payment_status={payment_status}, payment_method={payment_method}, additional_info={additional_info}"
    )

    try:
        # Преобразование строки статуса в элемент перечисления
        booking_status_enum = ReservationStatus[booking_status.upper()]
        logging.debug(f"Статус бронирования преобразован в {booking_status_enum}")
    except KeyError:
        logging.error(f"Неверный статус бронирования: {booking_status}")
        raise ValueError(f"Неверный статус бронирования: {booking_status}")

    try:
        with sqlite3.connect(DATABASE, timeout=10) as conn:
            cursor = conn.cursor()

            # Проверка, существует ли клиент с таким client_id
            cursor.execute("SELECT id FROM Клиенты WHERE id = ?", (client_id,))
            client_exists = cursor.fetchone()

            if not client_exists:
                logging.error(f"Клиент с ID {client_id} не найден.")
                raise ValueError(f"Клиент с ID {client_id} не найден.")

            # Проверка, существует ли номер комнаты с таким Номером комнаты
            cursor.execute("SELECT id FROM Номера WHERE Номер_комнаты = ?", (room_number,))
            room_exists = cursor.fetchone()

            if not room_exists:
                logging.error(f"Номер комнаты с ID {room_number} не найден.")
                raise ValueError(f"Номер комнаты с ID {room_number} не найден.")

            # Вставка нового бронирования
            cursor.execute("""
                INSERT INTO Бронирования (client_id, Дата_заезда, Дата_выезда, Номер_комнаты, Статус_бронирования, 
                Статус_оплаты, Способ_оплаты, Примечания, Дата_создания)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, date('now'))
            """, (client_id, check_in_date, check_out_date, room_number, booking_status_enum.value,
                  payment_status, payment_method, additional_info))
            conn.commit()

            logging.info(f"Бронирование для клиента с ID {client_id} успешно добавлено.")
    except sqlite3.IntegrityError as e:
        logging.error(f"Ошибка базы данных при добавлении бронирования: {e}")
        raise ValueError(f"Ошибка базы данных: {e}")
    except Exception as e:
        logging.error(f"Неизвестная ошибка при добавлении бронирования: {e}")
        raise e


# Получение всех бронирований
def get_all_reservations():
    """Получение всех бронирований из базы данных с включением данных клиента"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                Бронирования.id, 
                Клиенты.Фамилия || ' ' || Клиенты.Имя || ' ' || Клиенты.Отчество AS ФИО_клиента, 
                Бронирования.Дата_заезда, 
                Бронирования.Дата_выезда, 
                Бронирования.Номер_комнаты, 
                Бронирования.Статус_бронирования, 
                Бронирования.Статус_оплаты,
                Бронирования.Способ_оплаты,
                Бронирования.Примечания,
                Бронирования.Дата_создания
            FROM Бронирования
            JOIN Клиенты ON Бронирования.client_id = Клиенты.id
        """)
        reservations = cursor.fetchall()
    return reservations


def delete_reservation(reservation_id):
    """Удаление бронирования и обновление статуса комнаты"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()

        # Получаем номер комнаты из бронирования, которое будет удалено
        cursor.execute("SELECT Номер_комнаты FROM Бронирования WHERE id = ?", (reservation_id,))
        room_number = cursor.fetchone()

        if room_number:
            room_number = room_number[0]  # Извлекаем номер комнаты

            # Удаляем бронирование
            cursor.execute("DELETE FROM Бронирования WHERE id = ?", (reservation_id,))

            # Обновляем статус комнаты на "свободно"
            cursor.execute("UPDATE Номера SET Статус_комнаты = 'свободно' WHERE Номер_комнаты = ?", (room_number,))

            # Сохраняем изменения
            conn.commit()

            print(f"Бронирование с ID {reservation_id} удалено, комната {room_number} теперь свободна.")
        else:
            print(f"Бронирование с ID {reservation_id} не найдено.")

##*********************************************  Логин Пароль  *******************************************************************##


# Проверка логина и пароля
def authenticate_employee(username, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # Хэширование пароля
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, Роль FROM Сотрудники WHERE username = ? AND password = ?
        """, (username, hashed_password))
        result = cursor.fetchone()  # Возвращаем ID и роль сотрудника
        return result  # Вернём None, если пользователь не найден или пароль неверный

# Добавление недостающих колонок (если нужно)
def add_columns_if_not_exist():
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(Сотрудники);")
        columns = [column[1] for column in cursor.fetchall()]

        if 'username' not in columns:
            cursor.execute("ALTER TABLE Сотрудники ADD COLUMN username TEXT UNIQUE;")
            print("Колонка 'username' добавлена в таблицу 'Сотрудники'.")

        if 'password' not in columns:
            cursor.execute("ALTER TABLE Сотрудники ADD COLUMN password TEXT;")
            print("Колонка 'password' добавлена в таблицу 'Сотрудники'.")

        conn.commit()

##*********************************************  Cотрудники  *****************************************************************##


# Добавление сотрудника
def add_employee_bd(last_name, first_name, middle_name, phone, username, password, position, schedule=None, role="администратор"):
    """
    Добавляет нового сотрудника в базу данных.
    :param last_name: Фамилия сотрудника
    :param first_name: Имя сотрудника
    :param middle_name: Отчество сотрудника (может быть None)
    :param phone: Телефон сотрудника
    :param username: Уникальный логин (username)
    :param password: Пароль (хэшируется перед сохранением)
    :param position: Должность сотрудника
    :param schedule: Рабочий график (опционально)
    :param role: Роль сотрудника (по умолчанию "администратор")
    """
    # Хэшируем пароль для безопасности
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Открываем соединение с базой данных
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()

        # Проверка, существует ли уже пользователь с таким username
        cursor.execute("SELECT COUNT(*) FROM Сотрудники WHERE username = ?", (username,))
        result = cursor.fetchone()

        if result[0] > 0:
            print(f"Сотрудник с username '{username}' уже существует.")
        else:
            # Добавление нового сотрудника в базу данных
            cursor.execute("""
                INSERT INTO Сотрудники (Фамилия, Имя, Отчество, Телефон, username, password, Должность, График, Роль)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (last_name, first_name, middle_name, phone, username, hashed_password, position, schedule, role))

            # Сохраняем изменения
            conn.commit()
            print("Сотрудник успешно добавлен.")

# Получение всех сотрудников
def get_employees_brief(): # get_all_employees
    """Возвращает краткий список всех сотрудников из базы данных"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, Фамилия, Имя, Отчество FROM Сотрудники
        """)
        employees = cursor.fetchall()
        return employees

def get_employees_full(): #get_all_employees_bd
    """Возвращает полный список всех сотрудников из базы данных"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        # Извлекаем все необходимые поля из таблицы Сотрудники
        cursor.execute("""
            SELECT id, Фамилия, Имя, Отчество, Телефон, username, password, Должность, График, Роль
            FROM Сотрудники
        """)
        employees = cursor.fetchall()
        return employees

# Обновление расписания сотрудника
def update_employee_schedule(employee_id, new_schedule):
    """
    Обновляет график работы сотрудника.
    :param employee_id: Уникальный идентификатор сотрудника
    :param new_schedule: Новый график работы
    """
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Сотрудники SET График = ? WHERE id = ?
        """, (new_schedule, employee_id))
        conn.commit()
        print(f"График сотрудника {employee_id} успешно обновлен.")

# Логирование действий сотрудника
def log_action(employee_id, action):
    """
    Логирует действия сотрудника в базе данных.
    :param employee_id: Уникальный идентификатор сотрудника
    :param action: Описание действия
    """
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()

        # Логирование действия в таблицу logs (предполагается, что таблица logs существует)
        cursor.execute("""
            INSERT INTO logs (employee_id, action) 
            VALUES (?, ?)
        """, (employee_id, action))

        conn.commit()
        print(f"Действие сотрудника {employee_id} успешно зафиксировано.")


def update_employee_role(employee_id, new_role):
    """
    Обновляет роль сотрудника.
    :param employee_id: Уникальный идентификатор сотрудника
    :param new_role: Новая роль ("менеджер", "администратор" или "системный администратор")
    """
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Сотрудники SET Роль = ? WHERE id = ?
        """, (new_role, employee_id))
        conn.commit()
        print(f"Роль сотрудника {employee_id} успешно обновлена.")

def get_employee_by_id(employee_id):
    """Возвращает информацию о сотруднике по ID"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Сотрудники WHERE id = ?", (employee_id,))
        return cursor.fetchone()

def update_employee_info(employee_id, new_last_name, new_first_name, new_middle_name, new_phone,
                        new_username, new_password, new_position, new_schedule, new_role):
    """Обновляет информацию о сотруднике"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Сотрудники 
            SET Фамилия = ?, Имя = ?, Отчество = ?, Телефон = ?, username = ?, password = ?, Должность = ?, График = ?, Роль = ?
            WHERE id = ?
        """, (new_last_name, new_first_name, new_middle_name, new_phone, new_username, new_password, new_position, new_schedule, new_role, employee_id))
        conn.commit()
        print(f"Информация о сотруднике {employee_id} успешно обновлена.")

def check_username_uniqueness(username, employee_id):
    """Проверяет, уникален ли логин, исключая текущего сотрудника"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM Сотрудники WHERE username = ? AND id != ?
        """, (username, employee_id))
        return cursor.fetchone()[0] == 0

def delete_employee_by_id(employee_id):
    """Удаляет сотрудника из базы данных по ID"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Сотрудники WHERE id = ?", (employee_id,))
        conn.commit()
        print(f"Сотрудник с ID {employee_id} успешно удален.")

def get_user_id(username):
    """Получить user_id по имени пользователя"""
    with sqlite3.connect('F:/Hotel Management System/hotel_management.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM Сотрудники WHERE username = ?", (username,))
        result = cursor.fetchone()
        return result[0] if result else None


def get_employee_id_by_name(employee_name):
    """Возвращает ID сотрудника по его полному имени"""
    print(f"Поиск ID для сотрудника: {employee_name}")

    # Удаляем идентификатор в скобках, если он есть
    if "(" in employee_name and ")" in employee_name:
        employee_name = employee_name.split(" (")[0].strip()

    print(f"Отформатированное имя сотрудника: {employee_name}")

    # Разбиваем имя на фамилию, имя и отчество
    parts = employee_name.split(" ")
    print(f"Разделено на: {parts}")  # Отладочная информация

    # Проверка корректности разделения
    if len(parts) != 3:
        print("Некорректный формат имени: ожидалось три части (фамилия, имя, отчество)")
        return None

    last_name, first_name, middle_name = parts  # Фамилия, имя и отчество

    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM Сотрудники WHERE Фамилия = ? AND Имя = ? AND Отчество = ?
        """, (last_name, first_name, middle_name))
        result = cursor.fetchone()
        print(f"Найден результат: {result}")  # Отладочная информация

        return result[0] if result else None

##******************************************************  Задачи  ************************************************************##

# Добавление новой задачи
def add_task(task_type, employee_id, description, status, due_date):
    """Добавление новой задачи в базу данных"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Задачи (Тип_задачи, Сотрудник_id, Описание, Статус, Срок_исполнения)
            VALUES (?, ?, ?, ?, ?)
        """, (task_type, employee_id, description, status, due_date))
        conn.commit()


def get_all_tasks():
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                Задачи.id,
                Задачи.Тип_задачи,
                Задачи.Описание,
                Сотрудники.Фамилия,
                Сотрудники.Имя,
                Сотрудники.Отчество,  -- Включить отчество сотрудника
                Задачи.Статус,
                Задачи.Срок_исполнения
            FROM Задачи
            LEFT JOIN Сотрудники ON Задачи.Сотрудник_id = Сотрудники.id
        """)
        tasks = cursor.fetchall()
        print(tasks)  # Временно выводим данные в консоль для проверки
        return tasks

# Обновление статуса задачи
def update_task_status(task_id, new_status, user_id):
    """Обновление статуса задачи и запись в историю"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()

        # Обновление статуса задачи
        cursor.execute("""
            UPDATE Задачи SET Статус = ? WHERE id = ?
        """, (new_status, task_id))

        # Добавление записи в историю
        cursor.execute("""
            INSERT INTO История_задач (Задача_id, Сотрудник_id, Статус, Дата_изменения)
            VALUES (?, ?, ?, datetime('now'))
        """, (task_id, user_id, new_status))

        conn.commit()

# Удаление задачи
def delete_task_bd(task_id):
    """Удаление задачи из базы данных"""
    try:
        with sqlite3.connect(DATABASE, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Задачи WHERE id = ?", (task_id,))
            conn.commit()
            print(f"Задача с ID {task_id} успешно удалена.")
    except sqlite3.Error as e:
        print(f"Ошибка при удалении задачи: {e}")
        raise e  # Поднять ошибку для обработки в вызывающей функции


def get_filtered_tasks(employee=None, status=None, start_date=None, end_date=None, task_type=None):
    query = "SELECT * FROM Задачи WHERE 1=1"
    params = []

    if employee:
        query += " AND Сотрудник_id = ?"
        params.append(employee.split("(")[-1].replace(")", ""))  # Извлечение ID сотрудника из строки

    if status:
        query += " AND Статус = ?"
        params.append(status)

    if task_type:
        query += " AND Тип_задачи = ?"
        params.append(task_type)

    if start_date and end_date:
        query += " AND Дата_создания BETWEEN ? AND ?"
        params.append(start_date)
        params.append(end_date)

    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

def get_tasks_by_employee(employee_id):
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM Задачи WHERE Сотрудник_id = ?
        """, (employee_id,))
        return cursor.fetchall()

def get_filtered_tasks(employee=None, status=None, start_date=None, end_date=None):
    query = "SELECT * FROM Задачи WHERE 1=1"
    params = []

    if employee:
        query += " AND Сотрудник_id = ?"
        params.append(employee.split("(")[-1].replace(")", ""))  # Извлечение ID сотрудника из строки

    if status:
        query += " AND Статус = ?"
        params.append(status)

    if start_date and end_date:
        query += " AND Дата_создания BETWEEN ? AND ?"
        params.append(start_date)
        params.append(end_date)

    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

def update_task_details(task_id, task_type, employee_id, description, status, due_date):
    """Обновляет все данные задачи по ID"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Задачи
            SET Тип_задачи = ?, Сотрудник_id = ?, Описание = ?, Статус = ?, Срок_исполнения = ?
            WHERE id = ?
        """, (task_type, employee_id, description, status, due_date, task_id))
        conn.commit()


##*********************************************  Отчеты  ***************************************************************##

def add_report(employee_id, description, report_type):
    """Добавление нового отчета в таблицу Отчеты"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Отчеты (Сотрудник_id, Описание, Тип_отчета)
            VALUES (?, ?, ?)
        """, (employee_id, description, report_type))
        conn.commit()
        print("Отчет успешно добавлен.")

def get_all_reports():
    """Получение всех отчетов из таблицы Отчеты"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Отчеты")
        reports = cursor.fetchall()
        return reports


def get_daily_room_status(start_date, end_date):
    """Получение данных о статусах номеров за указанный период по дням"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()

        # Получаем все номера отеля
        cursor.execute("SELECT Номер_комнаты FROM Номера")
        room_numbers = [row[0] for row in cursor.fetchall()]
        total_rooms = len(room_numbers)  # Общее количество комнат в отеле

        # Запрос для получения занятых и свободных номеров на каждый день
        cursor.execute("""
            SELECT
                date(Дата_заезда) AS date,
                SUM(CASE WHEN Статус_бронирования IN ('Заезд', 'Подтверждено') THEN 1 ELSE 0 END) AS занятые,
                SUM(CASE WHEN Статус_бронирования = 'Выезд' THEN 1 ELSE 0 END) AS на_обслуживании
            FROM Бронирования
            WHERE date(Дата_заезда) BETWEEN ? AND ?
            GROUP BY date(Дата_заезда)
        """, (start_date, end_date))

        result = cursor.fetchall()

        # Отладочный вывод для всех строк
        for row in result:
            print(f"Row: {row}, Length: {len(row)}")

        report_data = []

        for row in result:
            # Проверяем, что в строке ровно три значения
            if len(row) == 3:
                date, occupied, service = row

                free_rooms = total_rooms - occupied - service
                load_percentage = (occupied / total_rooms) * 100 if total_rooms > 0 else 0

                # Добавляем отладочные сообщения
                print(
                    f"Дата: {date}, Занятые: {occupied}, На обслуживании: {service}, Свободные: {free_rooms}, Загрузка: {load_percentage:.2f}%")

                report_data.append((date, free_rooms, occupied, service, f"{load_percentage:.2f}%"))
            else:
                # Логируем ошибку, если количество значений не совпадает
                print(f"Ошибка данных: ожидалось 3 значения, но получено {len(row)} - {row}")

        # Проверка данных после заполнения report_data
        for row in report_data:
            print(f"Отчет: {row}")
            # Распаковка должна совпадать с количеством значений в report_data (ожидается 5)
            if len(row) == 5:
                date, free_rooms, occupied, service, load_percentage = row
            else:
                print(f"Неверное количество значений: {row}")

        return report_data

##**********************************************  Логтрование  **********************************************************##

def create_logs_table():
    """Создает таблицу logs, если она не существует"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES Сотрудники(id)
            )
        """)
        conn.commit()

# Вызов функции создания таблицы
create_logs_table()

def get_logs():
    """Получение всех записей логов"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM logs")
        logs = cursor.fetchall()
        return logs

# Вызов функции и вывод логов
logs = get_logs()
for log in logs:
    print(log)

##**********************************************************************************************************************##

## Миграции
def apply_migrations():
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()

        # Проверяем, существует ли таблица 'Бронирования'
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='Бронирования';
        """)
        if cursor.fetchone() is None:
            with open('migrations/create_tables.sql', 'r', encoding='utf-8') as f:
                sql_script = f.read()
                cursor.executescript(sql_script)
            print("Миграция применена.")
        else:
            print("Таблица 'Бронирования' уже существует. Миграция пропущена.")

    """Проверка наличия таблицы 'Задачи' и создание ее при необходимости"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()
        cursor.execute("""
                SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Задачи'
            """)
        if cursor.fetchone()[0] == 0:
            print("Таблица 'Задачи' не найдена. Создание таблицы...")
            # Если таблица не найдена, выполнить SQL-скрипт для создания
            create_tables()
        else:
            print("Таблица 'Задачи' уже существует.")



##*******************************************   Временные функции   ***********************************************************##



def generate_clients():
    """Генерация 25 клиентов с данными"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()

        # Фиксированные данные для клиентов
        last_names = ["Иванов", "Петров", "Сидоров", "Морозов", "Федоров", "Кузнецов", "Смирнов", "Васильев", "Попов", "Новиков"]
        first_names = ["Алексей", "Иван", "Петр", "Михаил", "Андрей", "Дмитрий", "Сергей", "Александр", "Максим", "Антон"]
        middle_names = ["Алексеевич", "Иванович", "Петрович", "Михайлович", "Андреевич", "Дмитриевич", "Сергеевич", "Александрович", "Максимович", "Антонович"]

        start_date = datetime(2024, 1, 1)

        for i in range(25):
            last_name = random.choice(last_names)
            first_name = random.choice(first_names)
            middle_name = random.choice(middle_names)
            phone = f"+7 9{random.randint(100, 999)} {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"
            email = f"{first_name.lower()}.{last_name.lower()}@gmail.com"
            address = f"Город {last_name} дом {i+1}"
            notes = "Примечание клиента"
            registration_date = (start_date + timedelta(days=i*3)).strftime("%Y-%m-%d")

            cursor.execute("""
                INSERT INTO Клиенты (Фамилия, Имя, Отчество, Телефон, Email, Дата_регистрации, Адрес, Примечания)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (last_name, first_name, middle_name, phone, email, registration_date, address, notes))

        conn.commit()
        print("25 клиентов успешно добавлены.")

def generate_reservations():
    """Генерация 30 бронирований для созданных клиентов"""
    with sqlite3.connect(DATABASE, timeout=10) as conn:
        cursor = conn.cursor()

        # Статусы бронирования и оплаты
        booking_statuses = ['Создано', 'Подтверждено', 'Заезд', 'Выезд', 'Завершено', 'Отменено']
        payment_statuses = ["Не оплачено", "Частично оплачено", "Оплачено"]
        payment_methods = ["Наличными", "Банковская карта", "Онлайн-платеж", "Безналичный расчет"]

        start_date = datetime(2024, 1, 10)

        for i in range(30):
            client_id = random.randint(1, 25)  # ID клиентов от 1 до 25
            room_number = random.randint(101, 120)  # Номера комнат от 101 до 120
            check_in_date = (start_date + timedelta(days=i*2)).strftime("%Y-%m-%d")
            check_out_date = (start_date + timedelta(days=i*2 + 3)).strftime("%Y-%m-%d")
            booking_status = random.choice(booking_statuses)
            payment_status = random.choice(payment_statuses)
            payment_method = random.choice(payment_methods)
            additional_info = "Дополнительная информация о бронировании"

            cursor.execute("""
                INSERT INTO Бронирования (ФИО_клиента, Дата_заезда, Дата_выезда, Номер_комнаты, Статус_бронирования, Статус_оплаты, Способ_оплаты, Примечания, Дата_создания)
                VALUES ((SELECT Фамилия || ' ' || Имя || ' ' || Отчество FROM Клиенты WHERE id = ?), ?, ?, ?, ?, ?, ?, ?, date('now'))
            """, (client_id, check_in_date, check_out_date, room_number, booking_status, payment_status, payment_method, additional_info))

        conn.commit()
        print("30 бронирований успешно добавлены.")