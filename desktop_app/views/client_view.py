import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from desktop_app.controllers.client_controller import get_clients, remove_client, update_client
from desktop_app.models.database_manager import get_all_clients
from desktop_app.models.database_manager import insert_client_in_db
import re


class ClientView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent,  bg="#e6e6e6")

        # Создаем таблицу (Treeview) для отображения клиентов
        self.client_tree = ttk.Treeview(self, columns=(
        "ID", "Фамилия", "Имя", "Отчество", "Телефон", "Email", "Дата регистрации", "Адрес", "Доп.инфо"), show='headings')


        # Определяем заголовки для таблицы
        self.client_tree.heading("ID", text="ID")
        self.client_tree.heading("Фамилия", text="Фамилия")
        self.client_tree.heading("Имя", text="Имя")
        self.client_tree.heading("Отчество", text="Отчество")
        self.client_tree.heading("Телефон", text="Телефон")
        self.client_tree.heading("Email", text="Email")
        self.client_tree.heading("Дата регистрации", text="Дата регистрации")
        self.client_tree.heading("Адрес", text="Адрес")
        self.client_tree.heading("Доп.инфо", text="Доп.инфо")

        # Задаем размеры столбцов
        self.client_tree.column("ID", width=0, stretch=tk.NO)
        self.client_tree.column("Фамилия", width=100)
        self.client_tree.column("Имя", width=100)
        self.client_tree.column("Отчество", width=100)  # Новый столбец
        self.client_tree.column("Телефон", width=120)
        self.client_tree.column("Email", width=150)
        self.client_tree.column("Дата регистрации", width=120)
        self.client_tree.column("Адрес", width=150)
        self.client_tree.column("Доп.инфо", width=150)

        self.client_tree.pack(fill=tk.BOTH, expand=True)
        # Инициализация переменных
        self.registration_date_var = tk.StringVar(value=self.get_current_date())
        self.last_name_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.middle_name_var = tk.StringVar()  # Отчество
        self.phone_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.address_var = tk.StringVar()
        self.notes_var = tk.StringVar()  # Дополнительные заметки
        self.search_var = tk.StringVar()
        self.selected_client_id = None

        #self.selected_client_id = None  # Для хранения ID выбранного клиента

        # Добавляем Label для предупреждений
        self.phone_warning_label = tk.Label(self, text="", fg="red")

        # Загрузка списка клиентов
        self.load_clients()
        self.create_form()
        # Поле для поиска клиента
        #self.create_search_bar()
        self.create_action_buttons()
        self.client_tree.bind("<<TreeviewSelect>>", self.on_client_select)

        self.load_clients()
        self.apply_treeview_style()

    def create_form(self):
        """Форма для добавления/редактирования клиента"""
        form_frame = tk.Frame(self, bg="#e6e6e6")
        form_frame.pack(fill=tk.X, pady=10)

        # Поле для ввода фамилии
        tk.Label(form_frame, text="Фамилия").pack(side=tk.LEFT, padx=5)
        self.last_name_entry = tk.Entry(form_frame, textvariable=self.last_name_var)
        self.last_name_entry.pack(side=tk.LEFT, padx=5)

        # Поле для ввода имени
        tk.Label(form_frame, text="Имя").pack(side=tk.LEFT, padx=5)
        self.first_name_entry = tk.Entry(form_frame, textvariable=self.name_var)
        self.first_name_entry.pack(side=tk.LEFT, padx=5)

        # Поле для ввода отчества
        tk.Label(form_frame, text="Отчество").pack(side=tk.LEFT, padx=5)
        self.middle_name_entry = tk.Entry(form_frame, textvariable=self.middle_name_var)
        self.middle_name_entry.pack(side=tk.LEFT, padx=5)

        # Поле для ввода телефона
        tk.Label(form_frame, text="Номер телефона").pack(side=tk.LEFT, padx=5)
        self.phone_entry = tk.Entry(form_frame, textvariable=self.phone_var)
        self.phone_entry.pack(side=tk.LEFT, padx=5)

        # Привязываем событие на изменение текста в поле для ввода телефона
        self.phone_var.trace_add("write", self.check_phone_format)

        # Поле для предупреждений
        self.phone_warning_label.pack()

        # Второй ряд: Электронная почта, Дата регистрации, Адрес, Дополнительные заметки
        row2_frame = tk.Frame(self)
        row2_frame.pack(fill=tk.X, pady=10)

        tk.Label(row2_frame, text="Email").pack(side=tk.LEFT, padx=5)
        self.email_entry = tk.Entry(row2_frame, textvariable=self.email_var)
        self.email_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(row2_frame, text="Дата регистрации клиента").pack(side=tk.LEFT, padx=5)
        self.registration_date_entry = tk.Entry(row2_frame, textvariable=self.registration_date_var, state='readonly')
        self.registration_date_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(row2_frame, text="Адрес").pack(side=tk.LEFT, padx=5)
        self.address_entry = tk.Entry(row2_frame, textvariable=self.address_var)
        self.address_entry.pack(side=tk.LEFT, padx=5)

        # Поле для ввода дополнительных заметок
        tk.Label(form_frame, text="Доп. заметки").pack(side=tk.LEFT, padx=5)
        self.notes_entry = tk.Entry(form_frame, textvariable=self.notes_var)
        self.notes_entry.pack(side=tk.LEFT, padx=5)

        # Поле для поиска клиента (справа от Доп. заметки)
        tk.Label(form_frame, text="Поиск клиента").pack(side=tk.LEFT, padx=5)
        search_entry = tk.Entry(form_frame, textvariable=self.search_var, width=40)  # Уменьшите ширину до 30
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<KeyRelease>", self.search_clients)

    def add_client(self):
        """Добавление нового клиента"""
        last_name = self.last_name_var.get()
        first_name = self.name_var.get()
        middle_name = self.middle_name_var.get()
        phone = self.phone_var.get()
        email = self.email_var.get()
        address = self.address_var.get()
        notes = self.notes_var.get()

        # Вставляем вывод данных перед вызовом insert_client_in_db
        print(
            f"Фамилия: {last_name}, Имя: {first_name}, Отчество: {middle_name}, Телефон: {phone}, Email: {email}, Адрес: {address}, Примечания: {notes}")

        # Проверяем, что хотя бы одно обязательное поле заполнено
        if not any([last_name, first_name, phone]):
            messagebox.showwarning("Ошибка", "Заполните хотя бы одно из обязательных полей!")
            return

        # Проверка данных и добавление клиента через функцию insert_client_in_db
        if self.validate_client_data(phone, email):
            success = insert_client_in_db(last_name, first_name, phone, middle_name, email, address, notes)

            if success:
                messagebox.showinfo("Успех", "Клиент успешно добавлен!")
                # Перезагружаем список клиентов, чтобы отобразить нового клиента
                self.load_clients()
                # Очищаем форму после добавления клиента
                self.clear_form()
            else:
                messagebox.showwarning("Ошибка", "Клиент с таким номером телефона уже существует!")

    def check_phone_format(self, *args):
        """Проверяет формат телефона во время ввода"""
        phone = self.phone_var.get()

        # Проверка на соответствие формату +7 XXX XXX XX XX
        phone_pattern = re.compile(r'^\+7 \d{3} \d{3} \d{2} \d{2}$')

        if phone_pattern.match(phone):
            self.phone_warning_label.config(text="")  # Сбрасываем предупреждение
        else:
            self.phone_warning_label.config(text="Неверный формат телефона! Пример: +7 xxx xxx xx xx")

    def create_action_buttons(self):
        """Кнопки для добавления, удаления и изменения клиента"""
        button_style = {'bg': '#c0c0c0', 'activebackground': '#c0c0c0'}

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)

        # Кнопка для добавления клиента
        add_button = tk.Button(button_frame, text="Добавить клиента", command=self.add_client, **button_style)
        add_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Кнопка для удаления клиента (справа от кнопки добавления)
        delete_button = tk.Button(button_frame, text="Удалить клиента", command=self.delete_client, **button_style)
        delete_button.pack(side=tk.LEFT, padx=10, pady=10)

        # Кнопка для изменения клиента (справа от кнопки удаления)
        update_button = tk.Button(button_frame, text="Изменить клиента", command=self.update_client, **button_style)
        update_button.pack(side=tk.LEFT, padx=10, pady=10)

    def load_clients(self):
        """Загрузка всех клиентов в словарь для использования при создании бронирований"""
        clients = get_all_clients()

        # Очищаем таблицу перед добавлением новых данных
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)

        # Отладка: Показать всех загруженных клиентов
        print(f"Отладка: Загруженные клиенты: {clients}")

        # Создаем словарь: {ФИО: ID клиента}
        self.client_dict = {f"{client[1]} {client[2]} {client[3]}".strip(): client[0] for client in clients}

        # Заполняем таблицу клиентов
        for index, client in enumerate(clients):
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.client_tree.insert("", tk.END, values=(
                client[0],  # ID
                client[1],  # Фамилия
                client[2],  # Имя
                client[3],  # Отчество
                client[4],  # Телефон
                client[5],  # Email
                client[6],  # Дата регистрации
                client[7],  # Адрес
                client[8]  # Доп.инфо
            ), tags=(tag,))

        print(f"Отладка: Словарь клиентов: {self.client_dict}")

    def search_clients(self, event):
        """Поиск клиента по фамилии, имени, отчеству, телефону или email"""
        query = self.search_var.get().lower().strip()
        clients = get_clients()  # Предполагается, что эта функция возвращает всех клиентов

        # Очищаем таблицу перед добавлением найденных данных
        for item in self.client_tree.get_children():
            self.client_tree.delete(item)

        found_clients = []

        for client in clients:
            # Проверяем, есть ли данные в клиенте (чтобы избежать ошибок с None)
            last_name = client[1].lower() if client[1] else ""
            first_name = client[2].lower() if client[2] else ""
            middle_name = client[3].lower() if client[3] else ""  # Проверяем на None
            phone = client[4].lower() if client[4] else ""
            email = client[5].lower() if client[5] else ""

            # Поиск по фамилии, имени, отчеству, телефону или email
            if (query in last_name or
                    query in first_name or
                    query in middle_name or
                    query in phone or
                    query in email):
                found_clients.append(client)

        # Добавляем найденных клиентов в таблицу
        for client in found_clients:
            self.client_tree.insert("", tk.END, values=(
                client[0],  # ID
                client[1],  # Фамилия
                client[2],  # Имя
                client[3] if client[3] else "",  # Отчество (если есть)
                client[4],  # Телефон
                client[5],  # Email
                client[6],  # Дата регистрации
                client[7],  # Адрес
                client[8]  # Доп.инфо
            ))


    def on_client_select(self, event):
        """Заполнение полей формы данными выбранного клиента для редактирования"""
        selected_item = self.client_tree.selection()  # Получаем выбранный элемент в Treeview
        if selected_item:
            client_info = self.client_tree.item(selected_item)["values"]  # Получаем данные о клиенте
            self.selected_client_id = client_info[0]  # ID клиента находится в первой колонке (скрытой)

            # Заполняем поля формы данными о выбранном клиенте
            self.last_name_var.set(client_info[1])  # Фамилия
            self.name_var.set(client_info[2])  # Имя
            self.middle_name_var.set(client_info[3])  # Отчество
            self.phone_var.set(client_info[4])  # Телефон
            self.email_var.set(client_info[5])  # Email
            self.registration_date_var.set(client_info[6])  # Дата регистрации
            self.address_var.set(client_info[7])  # Адрес
            self.notes_var.set(client_info[8])  # Доп. заметки

    def delete_client(self):
        """Удаление клиента с подтверждением"""
        selected_item = self.client_tree.selection()  # Получаем выбранный элемент в Treeview
        if selected_item:
            client_info = self.client_tree.item(selected_item)["values"]  # Получаем данные о клиенте
            client_id = client_info[0]  # ID клиента находится в первой колонке (скрытой)

            if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить клиента с ID {client_id}?"):
                try:
                    remove_client(client_id)  # Вызываем функцию удаления клиента
                    self.load_clients()  # Обновляем список клиентов
                    self.clear_form()  # Очищаем поля формы
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка при удалении клиента: {str(e)}")
        else:
            messagebox.showwarning("Ошибка", "Выберите клиента для удаления")

    def update_client(self):
        """Обновление данных клиента"""
        if self.selected_client_id:
            last_name = self.last_name_var.get()
            first_name = self.name_var.get()  # Используем self.name_var
            middle_name = self.middle_name_var.get()
            phone = self.phone_var.get()
            email = self.email_var.get()
            address = self.address_var.get()
            notes = self.notes_var.get()

            if self.validate_client_data(phone, email):
                update_client(self.selected_client_id, last_name, first_name, middle_name, phone, email, address, notes)
                messagebox.showinfo("Успех", f"Данные клиента {self.selected_client_id} успешно обновлены.")
                self.load_clients()
                self.clear_form()
            else:
                messagebox.showwarning("Ошибка", "Заполните все поля корректно")
        else:
            messagebox.showwarning("Ошибка", "Выберите клиента для изменения")

    def validate_client_data(self, phone, email):
        """Валидация данных клиента"""

        # Проверка на корректность номера телефона (если введен)
        phone_pattern = re.compile(r'^\+7 \d{3} \d{3} \d{2} \d{2}$')
        if phone and not phone_pattern.match(phone):
            messagebox.showwarning("Ошибка", "Некорректный формат телефона! Пример: +7 921 976 15 82")
            return False

        # Проверяем формат email только если он введен
        if email:
            if "@" not in email or "." not in email.split("@")[-1]:
                messagebox.showwarning("Ошибка", "Некорректный формат email!")
                return False

        return True

    def get_current_date(self):
        """Возвращает текущую дату в формате YYYY-MM-DD"""
        from datetime import datetime
        return datetime.now().strftime("%d.%m.%y") # %d.%m.%y %Y-%m-%d

    def clear_form(self):
        """Очистка полей формы"""
        self.last_name_var.set("")
        self.name_var.set("")
        self.middle_name_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.address_var.set("")
        self.notes_var.set("")

    def apply_treeview_style(self):
        """Применение стиля к строкам Treeview для чередования цветов."""
        for index, item in enumerate(self.client_tree.get_children()):
            color = '#f0f0f0' if index % 2 == 0 else '#d9d9d9'
            self.client_tree.tag_configure('evenrow', background='#f0f0f0')
            self.client_tree.tag_configure('oddrow', background='#d9d9d9')
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.client_tree.item(item, tags=(tag,))