import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from desktop_app.models.database_manager import add_task, get_all_tasks, update_task_status, get_employees_brief
from desktop_app.models.database_manager import delete_task_bd, get_tasks_by_employee, get_filtered_tasks, get_employee_id_by_name
from tkinter import simpledialog



class TaskView(tk.Frame):
    def __init__(self, parent, user_role, user_id=None):
        super().__init__(parent)
        print("Инициализация TaskView")

        # Сохраняем user_role и user_id как атрибуты класса
        self.user_role = user_role
        self.user_id = user_id

        # Инициализация таблицы задач
        self.task_tree = ttk.Treeview(self, columns=(
            "ID", "Тип задачи", "Описание", "Исполнитель", "Срок", "Статус"), show="headings")
        self.task_tree.pack(fill=tk.BOTH, expand=True)

        # Определение заголовков столбцов
        self.task_tree.heading("ID", text="ID")
        self.task_tree.heading("Тип задачи", text="Тип задачи")
        self.task_tree.heading("Описание", text="Описание")
        self.task_tree.heading("Исполнитель", text="Исполнитель")
        self.task_tree.heading("Срок", text="Срок")
        self.task_tree.heading("Статус", text="Статус")

        # Задание размеров столбцов
        self.task_tree.column("ID", width=50)
        self.task_tree.column("Тип задачи", width=150)
        self.task_tree.column("Описание", width=200)
        self.task_tree.column("Исполнитель", width=150)
        self.task_tree.column("Срок", width=120)
        self.task_tree.column("Статус", width=100)

        self.task_tree.pack(fill=tk.BOTH, expand=True)


        # Загружаем задачи
        print("Загрузка задач")
        self.load_tasks(user_role, user_id)

        # Создаем форму для добавления/редактирования задач
        print("Создание формы задач")
        self.create_task_form()

        # Кнопки для добавления, редактирования, удаления задач
        print("Создание кнопок задач")
        self.create_action_buttons()

    def load_tasks(self, user_role, user_id=None):
        """Загружает задачи в таблицу с учетом роли пользователя и его ID"""
        print(f"Загрузка задач для роли: {user_role}, ID пользователя: {user_id}")
        tasks = []  # Инициализируем пустым списком, чтобы избежать ошибок

        if user_role == 'менеджер':
            tasks = get_all_tasks()  # Менеджер видит все задачи
        elif user_role == 'администратор' and user_id:
            tasks = get_tasks_by_employee(user_id)  # Администратор видит только свои задачи

        print(f"Загруженные задачи: {tasks}")

        # Очищаем таблицу перед добавлением новых данных
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        for task in tasks:
            task_id = task[0]  # ID задачи
            task_type = task[1] or "Не указан"  # Тип задачи (новое поле), если None, используем "Не указан"
            description = task[2]  # Описание задачи
            employee_name = task[3] or "Не назначен"  # Фамилия и имя сотрудника, если None, используем "Не назначен"
            status = task[4]  # Статус задачи
            due_date = task[5]  # Срок исполнения задачи

            # Проверяем, является ли due_date корректной датой
            try:
                # Форматируем дату в формате дд/мм/гг
                if due_date:
                    due_date = datetime.strptime(due_date, '%Y-%m-%d').strftime('%d/%m/%y')
            except ValueError:
                print(f"Некорректная дата: {due_date}")  # Отладочное сообщение
                due_date = "Не указано"  # Устанавливаем значение по умолчанию, если дата некорректна
                
            # Вставляем значения в таблицу task_tree
            self.task_tree.insert("", tk.END, values=(task_id, task_type, description, employee_name, due_date, status))

    def create_task_form(self):
        """Создает форму для заполнения данных задачи"""
        form_frame = tk.Frame(self)
        form_frame.pack(pady=10, fill=tk.X)

        # Переменные для хранения данных формы
        self.employee_id_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.status_var = tk.StringVar(value='ожидание')
        self.due_date_var = tk.StringVar()
        self.task_type_var = tk.StringVar()  # Новый тип задачи

        # Предустановленные типы задач
        task_types = [
            "Регистрация нового клиента",
            "Уборка номера",
            "Проверка состояния номеров",
            "Обслуживание номера",
            "Отчет по бронированиям"
        ]

        # Поле для выбора типа задачи
        tk.Label(form_frame, text="Тип задачи:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.task_type_combo = ttk.Combobox(form_frame, textvariable=self.task_type_var, values=task_types)
        self.task_type_combo.grid(row=0, column=1, padx=5, pady=5)

        # Установить значение по умолчанию для типа задачи
        self.task_type_combo.set(task_types[0])

        # Получение списка сотрудников из базы данных
        employees = self.get_employees_list()

        # Поле для выбора сотрудника (выпадающий список)
        tk.Label(form_frame, text="Сотрудник:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.employee_combo = ttk.Combobox(form_frame, textvariable=self.employee_id_var, values=employees)
        self.employee_combo.grid(row=1, column=1, padx=5, pady=5)

        # Автозаполнение первого сотрудника из списка
        if employees:
            self.employee_combo.set(employees[0])  # Установить значение по умолчанию первым элементом списка

        # Поле для описания задачи
        tk.Label(form_frame, text="Описание:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        tk.Entry(form_frame, textvariable=self.description_var, width=50).grid(row=2, column=1, padx=5, pady=5)

        # Поле для выбора статуса (выпадающий список)
        tk.Label(form_frame, text="Статус:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        status_combo = ttk.Combobox(form_frame, textvariable=self.status_var,
                                    values=['ожидание', 'в процессе', 'завершено'])
        status_combo.grid(row=3, column=1, padx=5, pady=5)

        # Поле для срока исполнения задачи (календарь)
        tk.Label(form_frame, text="Срок исполнения:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.due_date_picker = DateEntry(form_frame, textvariable=self.due_date_var, date_pattern='yyyy-mm-dd')
        self.due_date_picker.grid(row=4, column=1, padx=5, pady=5)

        # Автозаполнение текущей даты для срока исполнения
        self.due_date_picker.set_date(self.get_default_due_date())

        # Кнопки "Добавить/Обновить" и "Очистить форму"
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        tk.Button(button_frame, text="Добавить/Обновить задачу", command=self.save_task).grid(row=0, column=0, padx=10)
        tk.Button(button_frame, text="Очистить форму", command=self.clear_form).grid(row=0, column=1, padx=10)


    # def create_task_form(self):
    #     """Создает форму для заполнения данных задачи"""
    #     form_frame = tk.Frame(self)
    #     form_frame.pack(pady=10, fill=tk.X)
    #
    #     # Переменные для хранения данных формы
    #     self.employee_id_var = tk.StringVar()
    #     self.description_var = tk.StringVar()
    #     self.status_var = tk.StringVar(value='ожидание')
    #     self.due_date_var = tk.StringVar()
    #     self.task_type_var = tk.StringVar()  # Новый тип задачи
    #
    #     # Предустановленные типы задач
    #     task_types = [
    #         "Регистрация нового клиента",
    #         "Уборка номера",
    #         "Проверка состояния номеров",
    #         "Обслуживание номера",
    #         "Отчет по бронированиям"
    #     ]
    #
    #     # Поле для выбора типа задачи
    #     tk.Label(form_frame, text="Тип задачи:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    #     self.task_type_combo = ttk.Combobox(form_frame, textvariable=self.task_type_var, values=task_types)
    #     self.task_type_combo.grid(row=0, column=1, padx=5, pady=5)
    #
    #     # Установить значение по умолчанию для типа задачи
    #     self.task_type_combo.set(task_types[0])
    #
    #     # Поле для выбора сотрудника (выпадающий список)
    #     tk.Label(form_frame, text="Сотрудник:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    #     employees = self.get_employees_list()
    #     self.employee_combo = ttk.Combobox(form_frame, textvariable=self.employee_id_var, values=employees)
    #     self.employee_combo.grid(row=1, column=1, padx=5, pady=5)
    #
    #     if employees:
    #         self.employee_combo.set(employees[0])
    #
    #     # Получение списка сотрудников из базы данных
    #     employees = self.get_employees_list()
    #
    #     # Поле для выбора сотрудника (выпадающий список)
    #     tk.Label(form_frame, text="Сотрудник:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    #     self.employee_combo = ttk.Combobox(form_frame, textvariable=self.employee_id_var, values=employees)
    #     self.employee_combo.grid(row=0, column=1, padx=5, pady=5)
    #
    #     # Автозаполнение первого сотрудника из списка
    #     if employees:
    #         self.employee_combo.set(employees[0])  # Установить значение по умолчанию первым элементом списка
    #
    #     # Поле для описания задачи
    #     tk.Label(form_frame, text="Описание:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    #     tk.Entry(form_frame, textvariable=self.description_var, width=50).grid(row=1, column=1, padx=5, pady=5)
    #
    #     # Поле для выбора статуса (выпадающий список)
    #     tk.Label(form_frame, text="Статус:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
    #     status_combo = ttk.Combobox(form_frame, textvariable=self.status_var,
    #                                 values=['ожидание', 'в процессе', 'завершено'])
    #     status_combo.grid(row=2, column=1, padx=5, pady=5)
    #
    #     # Поле для срока исполнения задачи (календарь)
    #     tk.Label(form_frame, text="Срок исполнения:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
    #     self.due_date_picker = DateEntry(form_frame, textvariable=self.due_date_var, date_pattern='yyyy-mm-dd')
    #     self.due_date_picker.grid(row=3, column=1, padx=5, pady=5)
    #
    #     # Автозаполнение текущей даты для срока исполнения
    #     self.due_date_picker.set_date(self.get_default_due_date())
    #
    #     # Кнопки "Добавить/Обновить" и "Очистить форму"
    #     button_frame = tk.Frame(form_frame)
    #     button_frame.grid(row=4, column=0, columnspan=2, pady=10)
    #
    #     tk.Button(button_frame, text="Добавить/Обновить задачу", command=self.save_task).grid(row=0, column=0, padx=10)
    #     tk.Button(button_frame, text="Очистить форму", command=self.clear_form).grid(row=0, column=1, padx=10)

    def create_filter_form(self):
        """Создает форму для фильтрации задач"""
        filter_frame = tk.Frame(self)
        filter_frame.pack(pady=10, fill=tk.X)

        # Поле для выбора сотрудника
        tk.Label(filter_frame, text="Сотрудник:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.filter_employee_var = tk.StringVar()
        employees = self.get_employees_list()
        self.filter_employee_combo = ttk.Combobox(filter_frame, textvariable=self.filter_employee_var, values=employees)
        self.filter_employee_combo.grid(row=0, column=1, padx=5, pady=5)

        # # Поле для выбора статуса
        # tk.Label(filter_frame, text="Статус:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        # self.filter_status_var = tk.StringVar()
        # self.filter_status_combo = ttk.Combobox(filter_frame, textvariable=self.filter_status_var,
        #                                         values=['ожидание', 'в процессе', 'завершено'])
        # self.filter_status_combo.grid(row=1, column=1, padx=5, pady=5)

        # Поле для выбора статуса (выпадающий список)
        tk.Label(filter_frame, text="Статус:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        status_combo = ttk.Combobox(filter_frame, textvariable=self.status_var,
                                    values=['ожидание', 'в процессе', 'завершено'])
        status_combo.grid(row=3, column=1, padx=5, pady=5)

        # Поля для выбора дат
        tk.Label(filter_frame, text="Дата начала:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.start_date_picker = DateEntry(filter_frame, date_pattern='yyyy-mm-dd')
        self.start_date_picker.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="Дата окончания:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.end_date_picker = DateEntry(filter_frame, date_pattern='yyyy-mm-dd')
        self.end_date_picker.grid(row=3, column=1, padx=5, pady=5)

        # Кнопка фильтрации
        tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter).grid(row=4, column=0, columnspan=2,
                                                                                         pady=10)

    def apply_filter(self):
        """Применяет фильтр к задачам"""
        employee = self.filter_employee_var.get()
        status = self.filter_status_var.get()
        start_date = self.start_date_picker.get_date()
        end_date = self.end_date_picker.get_date()

        # Получаем отфильтрованные задачи
        tasks = get_filtered_tasks(employee, status, start_date, end_date)

        # Очищаем таблицу и добавляем отфильтрованные задачи
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        for task in tasks:
            self.task_tree.insert("", tk.END, values=task)

    def get_default_due_date(self):
        """Возвращает стандартный срок исполнения (через неделю)"""
        return datetime.now() + timedelta(days=7)

    def create_action_buttons(self):
        """Создание кнопок управления задачами"""
        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)

        tk.Button(button_frame, text="Изменить статус", command=self.change_task_status).grid(row=0, column=0, padx=10,
                                                                                              pady=5)
        tk.Button(button_frame, text="Удалить задачу", command=self.delete_task).grid(row=0, column=1, padx=10, pady=5)

    def save_task(self):
        """Сохранение задачи (добавление новой или обновление существующей)"""
        task_type = self.task_type_var.get().strip()
        employee_name = self.employee_id_var.get().strip()
        description = self.description_var.get().strip()
        status = self.status_var.get().strip()
        due_date = self.due_date_picker.get_date().strftime('%Y-%m-%d')

        # Проверка обязательных полей
        if not task_type or not employee_name or not description:
            messagebox.showwarning("Ошибка", "Пожалуйста, заполните все обязательные поля.")
            return

        # Проверка корректности статуса
        if status not in ['ожидание', 'в процессе', 'завершено']:
            messagebox.showwarning("Ошибка", "Некорректный статус. Пожалуйста, выберите один из допустимых статусов.")
            return

        # Сохранение задачи
        try:
            employee_id = get_employee_id_by_name(employee_name)
            add_task(task_type, employee_id, description, status, due_date)
            messagebox.showinfo("Успех", "Задача успешно добавлена/обновлена.")
            self.clear_form()
            self.load_tasks(self.user_role, self.user_id)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить задачу: {str(e)}")

    def change_task_status(self):
        """Изменение статуса задачи"""
        task_id = self.get_selected_task_id()
        if not task_id:
            return  # Если ID не найден, прерываем выполнение

        new_status = self.status_var.get().strip().lower()

        # Проверяем корректность статуса
        if new_status not in ['ожидание', 'в процессе', 'завершено']:
            messagebox.showerror("Ошибка",
                                 "Некорректный статус. Пожалуйста, выберите один из: 'ожидание', 'в процессе', 'завершено'.")
            return

        try:
            # Вызов функции обновления статуса с task_id
            update_task_status(task_id, new_status, self.user_id)
            messagebox.showinfo("Успех", "Статус задачи успешно обновлен.")
            self.load_tasks(self.user_role, self.user_id)  # Перезагрузка задач
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить статус задачи: {str(e)}")

    def get_selected_task_id(self):
        """Получает ID выбранной задачи из Treeview"""
        selected_item = self.task_tree.selection()
        if selected_item:
            # Получаем значения выбранного элемента
            task_values = self.task_tree.item(selected_item, 'values')
            task_id = task_values[0]  # ID задачи предположительно в первом столбце
            return task_id
        else:
            messagebox.showwarning("Ошибка", "Пожалуйста, выберите задачу для изменения статуса.")
            return None

    def ask_new_status(self):
        """Запрос нового статуса задачи у пользователя через выпадающий список"""
        new_status_var = tk.StringVar()
        status_dialog = tk.Toplevel(self)
        status_dialog.title("Изменение статуса")

        tk.Label(status_dialog, text="Выберите новый статус:").pack(pady=5)
        status_combo = ttk.Combobox(status_dialog, textvariable=new_status_var,
                                    values=['ожидание', 'в процессе', 'завершено'])
        status_combo.pack(pady=5)
        status_combo.set('ожидание')  # Значение по умолчанию

        def on_confirm():
            self.new_status = new_status_var.get().strip().lower()
            if self.new_status not in ['ожидание', 'в процессе', 'завершено']:
                messagebox.showerror("Ошибка",
                                     "Некорректный статус. Пожалуйста, выберите один из: 'ожидание', 'в процессе', 'завершено'.")
            else:
                status_dialog.destroy()

        tk.Button(status_dialog, text="Подтвердить", command=on_confirm).pack(pady=5)
        status_dialog.grab_set()
        self.wait_window(status_dialog)

        return self.new_status

    def delete_task(self):
        """Удаление выбранной задачи"""
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите задачу для удаления.")
            return

        task_id = self.task_tree.item(selected_item)["values"][0]

        # Подтверждение удаления
        confirm = messagebox.askyesno("Подтверждение удаления",
                                      f"Вы уверены, что хотите удалить задачу с ID {task_id}?")
        if not confirm:
            return

        try:
            delete_task_bd(task_id)
            messagebox.showinfo("Успех", f"Задача с ID {task_id} успешно удалена.")

            # Используем атрибуты класса
            self.load_tasks(self.user_role, self.user_id)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить задачу: {str(e)}")

    def clear_form(self):
        """Очистка формы"""
        self.employee_id_var.set("")
        self.description_var.set("")
        self.status_var.set("ожидание")
        self.due_date_var.set("")

    def get_employees_list(self):
        """Получает список всех сотрудников из базы данных"""
        try:
            employees = get_employees_brief()
            # Создаем список для отображения в формате "Фамилия Имя (ID)"
            employee_list = [f"{emp[1]} {emp[2]} ({emp[0]})" for emp in employees]
            return employee_list
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить список сотрудников: {str(e)}")
            return []

