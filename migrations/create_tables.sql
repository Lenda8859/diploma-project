-- Создание таблицы клиентов
CREATE TABLE IF NOT EXISTS Клиенты (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Уникальный идентификатор клиента
    Фамилия TEXT NOT NULL, -- Фамилия клиента
    Имя TEXT NOT NULL, -- Имя клиента
    Отчество TEXT, -- Отчество клиента (опционально)
    Телефон TEXT NOT NULL, -- Номер телефона
    Email TEXT NOT NULL, -- Электронная почта
    Адрес TEXT, -- Адрес проживания клиента (опционально)
    Примечания TEXT, -- Дополнительные заметки о клиенте (опционально)
    Дата_регистрации DATE DEFAULT (date('now')) -- Дата регистрации клиента
);

-- Создание таблицы номеров
CREATE TABLE IF NOT EXISTS Номера (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Уникальный идентификатор
    Номер_комнаты INTEGER NOT NULL UNIQUE,  -- Номер комнаты
    Тип_комнаты TEXT NOT NULL,  -- Тип комнаты (например, Стандарт, Сьют, Делюкс)
    Статус_комнаты TEXT CHECK(Статус_комнаты IN ('свободно', 'забронировано', 'занято', 'на обслуживании')) NOT NULL DEFAULT 'свободно',  -- Статус комнаты
    Стоимость REAL NOT NULL,  -- Цена за сутки
    Описание TEXT  -- Дополнительная информация
);

-- Создание таблицы бронирований
CREATE TABLE IF NOT EXISTS Бронирования (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Уникальный идентификатор бронирования
    client_id INTEGER NOT NULL, -- Ссылка на таблицу клиентов
    Номер_комнаты INTEGER NOT NULL, -- Номер комнаты
    Дата_заезда DATE NOT NULL, -- Дата заезда
    Дата_выезда DATE NOT NULL, -- Дата выезда
    Статус_бронирования TEXT CHECK(Статус_бронирования IN ('Создано', 'Подтверждено', 'Заезд', 'Выезд', 'Завершено', 'Отменено')) NOT NULL, -- Статус бронирования
    Статус_оплаты TEXT CHECK(Статус_оплаты IN ('Не оплачено', 'Частично оплачено', 'Оплачено')) NOT NULL, -- Статус оплаты
    Способ_оплаты TEXT CHECK(Способ_оплаты IN ('Наличные', 'Банковская карта', 'Онлайн-платеж', 'Безналичный расчет')), -- Способ оплаты
    Дата_создания DATE DEFAULT (date('now')), -- Дата создания бронирования
    Примечания TEXT, -- Дополнительные заметки о брони (опционально)
    FOREIGN KEY (client_id) REFERENCES Клиенты(id), -- Связь с таблицей клиентов
    FOREIGN KEY (Номер_комнаты) REFERENCES Номера(id) -- Связь с таблицей номеров
);

-- Создание таблицы оплаты
CREATE TABLE IF NOT EXISTS Оплата (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Уникальный идентификатор оплаты
    Бронирование_id INTEGER NOT NULL, -- Ссылка на таблицу бронирований
    Сумма REAL NOT NULL, -- Сумма оплаты
    Дата_оплаты DATE DEFAULT (date('now')), -- Дата оплаты
    Статус_платежа TEXT CHECK(Статус_платежа IN ('Не оплачено', 'Частично оплачено', 'Оплачено')) NOT NULL, -- Статус платежа
    FOREIGN KEY (Бронирование_id) REFERENCES Бронирования(id) -- Связь с таблицей бронирований
);

-- Создание таблицы сотрудников
CREATE TABLE IF NOT EXISTS Сотрудники (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Уникальный идентификатор сотрудника
    Фамилия TEXT NOT NULL, -- Фамилия
    Имя TEXT NOT NULL, -- Имя
    Отчество TEXT, -- Отчество (опционально)
    Телефон TEXT NOT NULL, -- Номер телефона
    username TEXT UNIQUE NOT NULL, -- Уникальный логин сотрудника
    password TEXT NOT NULL, -- Пароль сотрудника
    Должность TEXT NOT NULL, -- Должность сотрудника
    График TEXT, -- График работы сотрудника (опционально)
    Роль TEXT CHECK(Роль IN ('менеджер', 'администратор')) NOT NULL -- Роль сотрудника
);

--ALTER TABLE Задачи ADD COLUMN Тип_задачи TEXT;

-- Создание таблицы задач
CREATE TABLE IF NOT EXISTS Задачи (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Уникальный идентификатор задачи
    Сотрудник_id INTEGER NOT NULL, -- Ссылка на таблицу сотрудников
    Описание TEXT NOT NULL, -- Описание задачи
    Статус TEXT CHECK(Статус IN ('ожидание', 'в процессе', 'завершено')) NOT NULL DEFAULT 'ожидание', -- Статус задачи
    Срок_исполнения DATE, -- Срок выполнения задачи (опционально)
    FOREIGN KEY (Сотрудник_id) REFERENCES Сотрудники(id) -- Связь с таблицей сотрудников
);



-- Создание таблицы История_задач
CREATE TABLE IF NOT EXISTS История_задач (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Задача_id INTEGER,
    Сотрудник_id INTEGER,
    Статус TEXT,
    Дата_изменения DATETIME,
    FOREIGN KEY (Задача_id) REFERENCES Задачи(id),
    FOREIGN KEY (Сотрудник_id) REFERENCES Сотрудники(id)
);

--INSERT INTO История_задач (Задача_id, Сотрудник_id, Статус, Дата_изменения)
--VALUES (?, ?, ?, datetime('now'))

-- Создание таблицы отчетов
CREATE TABLE IF NOT EXISTS Отчеты (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Уникальный идентификатор отчета
    Сотрудник_id INTEGER NOT NULL, -- Ссылка на таблицу сотрудников
    Описание TEXT, -- Описание отчета (опционально)
    Дата_создания DATE DEFAULT (date('now')), -- Дата создания отчета
    Тип_отчета TEXT CHECK(Тип_отчета IN ('Финансовый', 'По задачам', 'По бронированиям')) NOT NULL, -- Тип отчета
    FOREIGN KEY (Сотрудник_id) REFERENCES Сотрудники(id) -- Связь с таблицей сотрудников
);

--Создание таблицы для логгирования действий
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES Сотрудники(id)
);