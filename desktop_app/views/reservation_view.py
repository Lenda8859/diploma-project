import tkinter as tk
from tkinter import ttk, messagebox
# Изменение статуса бронирования
from desktop_app.controllers.reservation_controller import res_check_out, res_check_in, create_reservation
from desktop_app.controllers.reservation_controller import update_statuses
from desktop_app.models.database_manager import delete_reservation
from tkcalendar import DateEntry
from datetime import datetime
from desktop_app.models.status_enums import ReservationStatus
import sqlite3
DATABASE = 'F:/Hotel Management System/hotel_management.db'
class ReservationView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Словарь для хранения связи между ФИО клиента и его ID
        self.client_dict = {}


        # Таблица бронирований
        self.reservation_treeview = ttk.Treeview(self, columns=(
            "ID", "ФИО_клиента", "Дата_заезда", "Дата_выезда", "Номер_комнаты", "Статус_бронирования",
            "Статус_оплаты", "Способ_оплаты", "Примечания", "Дата создания"), show="headings")

        # Изменяем цвет основного окна
        self.parent.configure(bg="#e6e6e6")

        # Настройка стиля заголовка
        style = ttk.Style()
        style.configure("Treeview.Heading", background="#c0c0c0", foreground="black", font=("Arial", 10, "bold"))

        # Изменяем цвет фона самого фрейма
        self.configure(bg="#e6e6e6")

        # Устанавливаем заголовки для столбцов
        self.reservation_treeview.heading("ID", text="ID")
        self.reservation_treeview.heading("ФИО_клиента", text="ФИО клиента")
        self.reservation_treeview.heading("Дата_заезда", text="Дата заезда")
        self.reservation_treeview.heading("Дата_выезда", text="Дата выезда")
        self.reservation_treeview.heading("Номер_комнаты", text="Номер комнаты")
        self.reservation_treeview.heading("Статус_бронирования", text="Статус бронирования")
        self.reservation_treeview.heading("Статус_оплаты", text="Статус оплаты")
        self.reservation_treeview.heading("Способ_оплаты", text="Способ оплаты")
        self.reservation_treeview.heading("Примечания", text="Примечания")
        self.reservation_treeview.heading("Дата создания", text="Дата создания")

        self.reservation_treeview.column("Способ_оплаты", width=120)
        self.reservation_treeview.column("Примечания", width=200)
        self.reservation_treeview.column("Дата создания", width=120)

        # Добавляем таблицу в виджет
        self.reservation_treeview.column("ID", width=0, stretch=tk.NO)  # Скрываем колонку ID
        self.reservation_treeview.pack(fill=tk.BOTH, expand=True)

        # Инициализация переменных
        self.client_name_var = tk.StringVar()
        self.check_in_date_var = tk.StringVar()
        self.check_out_date_var = tk.StringVar()
        self.room_id_var = tk.IntVar()
        self.reservation_status_var = tk.StringVar()
        self.payment_status_var = tk.StringVar()


        # Переменные для поиска по Фамилии, Имени и Отчеству
        self.search_last_name_var = tk.StringVar()
        self.search_first_name_var = tk.StringVar()
        self.search_middle_name_var = tk.StringVar()

        # Создаем форму для поиска клиента
        self.create_client_search_bar()

        # Загрузка всех бронирований в таблицу
        self.load_reservations()

        # Форма для создания/изменения бронирований
        self.create_form()

        # Кнопки для управления бронированиями
        self.create_action_buttons()

        self.reservation_treeview.bind("<<TreeviewSelect>>", self.on_reservation_select)

    def create_form(self):
        """Создает форму для добавления и редактирования бронирований"""
        form_frame = tk.Frame(self)
        form_frame.pack(fill=tk.X, pady=10)


        tk.Label(form_frame, text="Дата заезда").pack(side=tk.LEFT, padx=5)
        self.check_in_date_var = DateEntry(form_frame, date_pattern='dd/mm/yyyy')
        self.check_in_date_var.pack(side=tk.LEFT, padx=5)

        tk.Label(form_frame, text="Дата выезда").pack(side=tk.LEFT, padx=5)
        self.check_out_date_var = DateEntry(form_frame, date_pattern='dd/mm/yyyy')
        self.check_out_date_var.pack(side=tk.LEFT, padx=5)

        tk.Label(form_frame, text="Номер комнаты").pack(side=tk.LEFT, padx=5)
        tk.Entry(form_frame, textvariable=self.room_id_var).pack(side=tk.LEFT, padx=5)

        tk.Label(form_frame, text="Статус бронирования").pack(side=tk.LEFT, padx=5)
        ttk.Combobox(form_frame, textvariable=self.reservation_status_var,
                     values=['Создано', 'Подтверждено', 'Заезд', 'Выезд', 'Завершено', 'Отменено']).pack(side=tk.LEFT, padx=5)

        tk.Label(form_frame, text="Статус оплаты").pack(side=tk.LEFT, padx=5)
        ttk.Combobox(form_frame, textvariable=self.payment_status_var,
                     values=['Не оплачено', 'Частично оплачено', 'Оплачено']).pack(side=tk.LEFT, padx=5)

        # Поле для ввода "Способ оплаты"
        tk.Label(form_frame, text="Способ оплаты").pack(side=tk.LEFT, padx=5)
        self.payment_method_var = tk.StringVar()
        ttk.Combobox(form_frame, textvariable=self.payment_method_var,
                     values=["Наличные", "Банковская карта", "Онлайн-платеж", "Безналичный расчет"]).pack(side=tk.LEFT,
                                                                                                          padx=5)

        # Поле для ввода "Примечания"
        tk.Label(form_frame, text="Примечания").pack(side=tk.LEFT, padx=5)
        self.notes_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.notes_var).pack(side=tk.LEFT, padx=5)


    def create_client_search_bar(self):
        """Создаем форму для поиска клиента по фамилии, имени и отчеству"""
        search_frame = tk.Frame(self)
        search_frame.pack(fill=tk.X, pady=5)

        # Поле для поиска по Фамилии
        tk.Label(search_frame, text="Фамилия").pack(side=tk.LEFT, padx=5)
        tk.Entry(search_frame, textvariable=self.search_last_name_var).pack(side=tk.LEFT, padx=5)

        # Поле для поиска по Имени
        tk.Label(search_frame, text="Имя").pack(side=tk.LEFT, padx=5)
        tk.Entry(search_frame, textvariable=self.search_first_name_var).pack(side=tk.LEFT, padx=5)

        # Поле для поиска по Отчеству
        tk.Label(search_frame, text="Отчество").pack(side=tk.LEFT, padx=5)
        tk.Entry(search_frame, textvariable=self.search_middle_name_var).pack(side=tk.LEFT, padx=5)

        # Кнопка для поиска
        search_button = tk.Button(search_frame, text="Поиск клиента", command=self.search_client)
        search_button.pack(side=tk.LEFT, padx=5)

        # Устанавливаем фиксированный размер для Listbox
        listbox_frame = tk.Frame(self)
        listbox_frame.pack(fill=tk.X, padx=5, pady=5)

        self.client_listbox = tk.Listbox(listbox_frame, height=4, width=120)
        self.client_listbox.grid(row=0, column=0, sticky="nsw")  # Используем grid для более точного контроля

        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=self.client_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.client_listbox.configure(yscrollcommand=scrollbar.set)
        self.client_listbox.bind('<<ListboxSelect>>', self.on_client_select)

    def search_client(self):
        """Поиск клиентов по фамилии, имени и отчеству и отображение результатов"""
        last_name = self.search_last_name_var.get().strip()
        first_name = self.search_first_name_var.get().strip()
        middle_name = self.search_middle_name_var.get().strip()

        # SQL-запрос для фильтрации клиентов по введенным критериям
        query = "SELECT * FROM Клиенты WHERE 1=1"
        params = []

        if last_name:
            query += " AND Фамилия LIKE ?"
            params.append(f"%{last_name}%")
        if first_name:
            query += " AND Имя LIKE ?"
            params.append(f"%{first_name}%")
        if middle_name:
            query += " AND Отчество LIKE ?"
            params.append(f"%{middle_name}%")

        # Выполняем запрос к базе данных
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            clients = cursor.fetchall()

        # Очистка Listbox
        self.client_listbox.delete(0, tk.END)

        # Очищаем словарь для связи ФИО клиента с ID
        self.client_dict.clear()

        # Отображение найденных клиентов в Listbox
        if clients:
            for index, client in enumerate(clients):
                # Формируем полное имя клиента
                full_name = f"{client[1]} {client[2]} {client[3]}"
                # Добавляем клиента в Listbox
                self.client_listbox.insert(tk.END, full_name)
                # Связываем полное имя с его client_id
                self.client_dict[full_name] = client[0]

                color = '#f0f0f0' if index % 2 == 0 else '#d9d9d9'
                self.client_listbox.itemconfig(index, bg=color)
        else:
            messagebox.showwarning("Результат", "Клиенты не найдены.")

    def is_room_available(self, room_number):
        """Проверяет, доступен ли номер для бронирования (не забронирован, не занят и не на обслуживании)."""
        try:
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT Статус_комнаты FROM Номера WHERE Номер_комнаты = ?
                """, (room_number,))
                room_status = cursor.fetchone()[0]

                # Если статус комнаты не «свободно», она занята, забронирована или на обслуживании
                if room_status in ['забронировано', 'занято', 'на обслуживании']:
                    #print(f"Отладка: Комната {room_number} недоступна для нового бронирования, статус: {room_status}")
                    return False
                #print(f"Отладка: Комната {room_number} доступна для бронирования, статус: {room_status}")
                return True
        except Exception as e:
            #print(f"Ошибка при проверке доступности комнаты: {e}")
            return False


    def handle_create_reservation(self):
        """Создание нового бронирования на основе данных из интерфейса"""
        client_name = self.client_name_var.get().strip()
        #print(f"Отладка: Выбранный клиент - {client_name}")

        # Получаем ID клиента по имени
        client_id = self.client_dict.get(client_name)
        #print(f"Отладка: Найденный ID клиента - {client_id}")

        if not client_id:
            print("Ошибка: Клиент не найден.")
            messagebox.showwarning("Ошибка", "Выберите существующего клиента!")
            return

        try:
            # Преобразуем даты из интерфейса в формат "YYYY-MM-DD"
            check_in_date = datetime.strptime(self.check_in_date_var.get(), "%d/%m/%Y").strftime("%Y-%m-%d")
            check_out_date = datetime.strptime(self.check_out_date_var.get(), "%d/%m/%Y").strftime("%Y-%m-%d")
            #print(f"Отладка: Дата заезда - {check_in_date}, Дата выезда - {check_out_date}")
        except ValueError:
            #print("Ошибка: Неверный формат даты.")
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте формат ДД-ММ-ГГГГ.")
            return

        room_id = self.room_id_var.get()  # Получаем номер комнаты из интерфейса
        #print(f"Отладка: Выбранный номер комнаты - {room_id}")
        reservation_status = self.reservation_status_var.get()  # Статус бронирования
        payment_status = self.payment_status_var.get()  # Статус оплаты
        payment_method = self.payment_method_var.get()  # Способ оплаты
        notes = self.notes_var.get()  # Примечания

        #print(f"Отладка: Статус бронирования - {reservation_status}, Статус оплаты - {payment_status}")

        # Проверка, можно ли забронировать номер
        if not self.is_room_available(room_id):
            messagebox.showwarning("Ошибка", f"Номер {room_id} не доступен для бронирования.")
            return

        # Создание бронирования
        create_reservation(client_id, check_in_date, check_out_date, room_id, reservation_status, payment_status,
                           payment_method, notes)
        self.load_reservations()


    def on_client_select(self, event):
        """Обработчик выбора клиента из Listbox"""
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            selected_client = self.client_listbox.get(index)

            # Извлекаем ID клиента через словарь self.client_dict
            client_name = selected_client.strip()
            client_id = self.client_dict.get(client_name)
            #print(f"Отладка: Выбран клиент {client_name}, ID: {client_id}")

            # Проверяем, что ID клиента найден
            if client_id:
                self.client_name_var.set(client_name)
                self.selected_client_id = client_id  # Сохраняем ID клиента для создания бронирования
            else:
                messagebox.showerror("Ошибка", "Клиент не найден в базе данных.")

    def create_action_buttons(self):
        """Создает кнопки для управления бронированиями"""
        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)

        button_style = {'bg': '#c0c0c0', 'activebackground': '#c0c0c0'}

        # Кнопка для создания бронирования
        add_button = tk.Button(button_frame, text="Создать бронирование", command=self.handle_create_reservation,
                               **button_style)
        add_button.pack(side=tk.LEFT, padx=5)

        # Кнопка для обновления статуса бронирования
        update_button = tk.Button(button_frame, text="Обновить статус", command=self.update_reservation, **button_style)
        update_button.pack(side=tk.LEFT, padx=5)


        # Кнопка для удаления бронирования
        delete_button = tk.Button(button_frame, text="Удалить бронирование", command=self.get_delete_reservation,
                                  **button_style)
        delete_button.pack(side=tk.LEFT, padx=5)

    def load_reservations(self):
        """Загружает все бронирования в таблицу"""
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()

            # Выполняем запрос с использованием JOIN для получения имени клиента по client_id
            cursor.execute("""
                SELECT Бронирования.id, Клиенты.Фамилия, Клиенты.Имя, Клиенты.Отчество, 
                       Бронирования.Дата_заезда, Бронирования.Дата_выезда, Бронирования.Номер_комнаты, 
                       Бронирования.Статус_бронирования, Бронирования.Статус_оплаты, Бронирования.Способ_оплаты, 
                       Бронирования.Примечания, Бронирования.Дата_создания
                FROM Бронирования
                JOIN Клиенты ON Бронирования.client_id = Клиенты.id
            """)

            reservations = cursor.fetchall()

        # Очищаем таблицу перед загрузкой данных
        self.reservation_treeview.delete(*self.reservation_treeview.get_children())

        # Настраиваем стили для чередующихся строк
        self.reservation_treeview.tag_configure('row_even', background='#f0f0f0')
        self.reservation_treeview.tag_configure('row_odd', background='#d9d9d9')

        # Отображаем бронирования с ФИО клиента
        for index, reservation in enumerate(reservations):
            # Формируем строку ФИО клиента
            client_name = f"{reservation[1]} {reservation[2]} {reservation[3]}"

            # Форматируем даты в формате день/месяц/год
            formatted_check_in = datetime.strptime(reservation[4], "%Y-%m-%d").strftime("%d/%m/%Y")
            formatted_check_out = datetime.strptime(reservation[5], "%Y-%m-%d").strftime("%d/%m/%Y")

            # Проверяем, есть ли время в дате создания
            try:
                # Попробуем преобразовать строку с датой и временем
                date_created = datetime.strptime(reservation[11], "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%Y %H:%M:%S")
            except ValueError:
                # Если времени нет, то просто отображаем дату
                date_created = datetime.strptime(reservation[11], "%Y-%m-%d").strftime("%d/%m/%Y")

            # Определяем тег строки для чередования цветов
            tag = 'row_even' if index % 2 == 0 else 'row_odd'

            # Добавляем данные в таблицу с соответствующим тегом
            self.reservation_treeview.insert("", tk.END, values=(
                reservation[0], client_name, formatted_check_in, formatted_check_out, reservation[6],
                reservation[7], reservation[8], reservation[9], reservation[10], date_created
            ), tags=(tag,))




    def get_client_name_by_id(self, client_id):
        """Получает ФИО клиента по его ID"""
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Фамилия, Имя FROM Клиенты WHERE id = ?", (client_id,))
            client = cursor.fetchone()
            return f"{client[0]} {client[1]}" if client else "Неизвестный клиент"



    def update_reservation(self):
        """Обновление статуса бронирования и дат"""
        selected_item = self.reservation_treeview.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите бронирование для изменения статуса.")
            return

        reservation_id = self.reservation_treeview.item(selected_item)["values"][0]
        new_status_str = self.reservation_status_var.get()  # Получаем строку статуса

        try:
            # Преобразуем строковый статус в объект ReservationStatus
            new_status = ReservationStatus[new_status_str.upper()]
        except KeyError:
            messagebox.showerror("Ошибка", f"Неверный статус бронирования: {new_status_str}")
            return

        payment_status = self.payment_status_var.get() if self.payment_status_var.get() else None
        payment_method = self.payment_method_var.get() if self.payment_method_var.get() else None

        if not new_status:
            messagebox.showwarning("Ошибка", "Выберите новый статус для бронирования.")
            return

        # Получаем даты заезда и выезда из интерфейса
        try:
            check_in_date = datetime.strptime(self.check_in_date_var.get(), "%d/%m/%Y").strftime("%Y-%m-%d")
            check_out_date = datetime.strptime(self.check_out_date_var.get(), "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте формат ДД-ММ-ГГГГ.")
            return

        # Вызываем функцию обновления статусов и дат
        update_statuses(reservation_id, new_status, room_number=self.room_id_var.get(), payment_status=payment_status,
                        payment_method=payment_method, check_in_date=check_in_date, check_out_date=check_out_date)

        self.load_reservations()

    def get_delete_reservation(self):
        """Удаление бронирования"""
        selected_item = self.reservation_treeview.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите бронирование для удаления.")
            return

        reservation_id = self.reservation_treeview.item(selected_item)["values"][0]
        delete_reservation(reservation_id) # Вызов функции из database_manager.py
        self.load_reservations() # Обновляем список бронирований

    def check_in(self):
        """Заезд клиента (изменение статуса на 'заезд')"""
        selected_item = self.reservation_treeview.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите бронирование для заезда.")
            return

        reservation_id = self.reservation_treeview.item(selected_item)["values"][0]
        room_number = self.reservation_treeview.item(selected_item)["values"][4]  # Номер комнаты

        # Отладочное сообщение для проверки данных
        #print(f"Отладка: Заезд для бронирования ID {reservation_id}, номер комнаты {room_number}")

        if room_number == 0:
            #print("Ошибка: Номер комнаты установлен в 0, что недопустимо.")
            return

        res_check_in(reservation_id, room_number)  # Передаем reservation_id и room_number
        self.load_reservations()

    def check_out(self):
        """Выезд клиента (изменение статуса на 'выезд')"""
        selected_item = self.reservation_treeview.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите бронирование для выезда.")
            return

        reservation_id = self.reservation_treeview.item(selected_item)["values"][0]
        room_number = self.reservation_treeview.item(selected_item)["values"][4]  # Номер комнаты

        # Отладочное сообщение для проверки данных
        #print(f"Отладка: Выезд для бронирования ID {reservation_id}, номер комнаты {room_number}")

        if room_number == 0:
            #print("Ошибка: Номер комнаты установлен в 0, что недопустимо.")
            return

        res_check_out(reservation_id, room_number)  # Передаем reservation_id и room_number
        self.load_reservations()

    def on_reservation_select(self, event):
        """Заполнение полей формы данными выбранного бронирования для редактирования"""
        selected_item = self.reservation_treeview.selection()  # Получаем выбранный элемент в Treeview
        if selected_item:
            reservation_info = self.reservation_treeview.item(selected_item)["values"]  # Получаем данные о бронировании

            # Заполняем поля формы данными о выбранном бронировании
            self.client_name_var.set(reservation_info[1])  # ФИО клиента
            self.check_in_date_var.set_date(reservation_info[2])  # Дата заезда
            self.check_out_date_var.set_date(reservation_info[3])  # Дата выезда
            self.room_id_var.set(reservation_info[4])  # Номер комнаты
            self.reservation_status_var.set(reservation_info[5])  # Статус бронирования
            self.payment_status_var.set(reservation_info[6])  # Статус оплаты
            self.payment_method_var.set(reservation_info[7])  # Способ оплаты
            self.notes_var.set(reservation_info[8])  # Примечания

    def on_client_click(self, event):
        """Обработчик клика мыши по элементу в Listbox"""
        selection = self.client_listbox.curselection()
        if selection:
            index = selection[0]
            selected_client = self.client_listbox.get(index)
            messagebox.showinfo("Клиент выбран", f"Выбран клиент: {selected_client}")




