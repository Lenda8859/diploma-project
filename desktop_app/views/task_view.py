import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from desktop_app.models.database_manager import add_task, get_all_tasks, update_task_status, get_employees_brief
from desktop_app.models.database_manager import delete_task_bd, get_tasks_by_employee, get_filtered_tasks, get_employee_id_by_name
from tkinter import simpledialog
from desktop_app.models.database_manager import update_task_details



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

        self.task_tree.bind("<<TreeviewSelect>>", self.on_task_select)
        self.task_tree.bind("<Button-1>", self.on_click_outside)

        # Загружаем задачи
        self.load_tasks(user_role, user_id)

        # Создаем форму для добавления/редактирования задач
        self.create_task_form()





    def load_tasks(self, user_role, user_id=None):
        """Загружает задачи в таблицу с учетом роли пользователя и его ID"""
        tasks = []  # Инициализируем пустым списком, чтобы избежать ошибок

        if user_role == 'менеджер':
            tasks = get_all_tasks()  # Менеджер видит все задачи
        elif user_role == 'администратор' and user_id:
            tasks = get_tasks_by_employee(user_id)  # Администратор видит только свои задачи

        # Очищаем таблицу перед добавлением новых данных
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)

        for index, task in enumerate(tasks):
            task_id = task[0]
            task_type = task[1] or "Не указан"
            description = task[2]
            employee_name = f"{task[3]} {task[4]} {task[5]}" if task[3] and task[4] and task[5] else "Не назначен"
            status = task[6]
            due_date = task[7]

            # Проверяем, является ли due_date корректной датой
            try:
                if due_date:
                    due_date = datetime.strptime(due_date, '%d.%m.%y').strftime('%d.%m.%y')
            except ValueError:
                due_date = "Не указано"

            # Чередуем цвета строк (светло-серый и чуть темнее)
            row_color = "#f0f0f0" if index % 2 == 0 else "#d9d9d9"

            # Вставляем значения в таблицу task_tree
            self.task_tree.insert("", tk.END, values=(task_id, task_type, description, employee_name, due_date, status),
                                  tags=('evenrow' if index % 2 == 0 else 'oddrow',))

            # Применяем цвета
            self.task_tree.tag_configure('evenrow', background='#f0f0f0')
            self.task_tree.tag_configure('oddrow', background='#d9d9d9')

    def create_task_form(self):
        """Создает форму для заполнения и фильтрации данных задачи"""
        form_frame = tk.Frame(self, bg="#e6e6e6")  # Задний фон формы светло-серый
        form_frame.pack(pady=10, fill=tk.X)

        # Переменные для хранения данных формы
        self.employee_id_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.status_var = tk.StringVar(value='ожидание')
        self.due_date_var = tk.StringVar()
        self.task_type_var = tk.StringVar()

        # Предустановленные типы задач
        task_types = [
            "Регистрация нового клиента",
            "Уборка номера",
            "Проверка состояния номеров",
            "Обслуживание номера",
            "Отчет по бронированиям"
        ]

        # Поле для выбора типа задачи
        tk.Label(form_frame, text="Тип задачи:", bg="#e6e6e6").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.task_type_combo = ttk.Combobox(form_frame, textvariable=self.task_type_var, values=task_types, width=30)
        self.task_type_combo.grid(row=0, column=1, padx=5, pady=5)

        # Поле для выбора сотрудника
        employees = self.get_employees_list()
        tk.Label(form_frame, text="Сотрудник:", bg="#e6e6e6").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.employee_combo = ttk.Combobox(form_frame, textvariable=self.employee_id_var, values=employees, width=30)
        self.employee_combo.grid(row=0, column=3, padx=5, pady=5)

        # Поле для описания задачи
        tk.Label(form_frame, text="Описание:", bg="#e6e6e6").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.description_text = tk.Text(form_frame, height=3, width=50, bg="#f2f2f2")  # Цвет поля светло-серый
        self.description_text.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky=tk.W)

        # Поле для выбора статуса
        tk.Label(form_frame, text="Статус:", bg="#e6e6e6").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        status_combo = ttk.Combobox(form_frame, textvariable=self.status_var,
                                    values=['ожидание', 'в процессе', 'завершено'])
        status_combo.grid(row=0, column=5, padx=5, pady=5)

        # Поле для срока исполнения задачи
        tk.Label(form_frame, text="Срок исполнения:", bg="#e6e6e6").grid(row=0, column=6, padx=5, pady=5, sticky=tk.W)
        self.due_date_picker = DateEntry(form_frame, textvariable=self.due_date_var, date_pattern='dd.MM.yy')
        self.due_date_picker.grid(row=0, column=7, padx=5, pady=5)

        # Кнопки формы
        button_frame = tk.Frame(form_frame, bg="#e6e6e6")
        button_frame.grid(row=2, column=0, columnspan=8, pady=10)

        tk.Button(button_frame, text="Добавить/Обновить задачу", command=self.save_task, bg="#c0c0c0").grid(row=0,
                                                                                                            column=0,
                                                                                                            padx=5)
        tk.Button(button_frame, text="Очистить форму", command=self.clear_form, bg="#c0c0c0").grid(row=0, column=1,
                                                                                                   padx=5)
        tk.Button(button_frame, text="Применить фильтр", command=self.apply_filter, bg="#c0c0c0").grid(row=0, column=2,
                                                                                                       padx=5)
        tk.Button(button_frame, text="Удалить задачу", command=self.delete_task, bg="#c0c0c0").grid(row=0, column=3,
                                                                                                    padx=5)

    def apply_filter(self):
        """Применяет фильтр к задачам"""
        # Используем переменные, созданные в create_task_form
        task_type = self.task_type_var.get()
        employee = self.employee_id_var.get()
        status = self.status_var.get()

        # Получаем срок исполнения из date picker
        due_date = self.due_date_var.get()

        # Получаем отфильтрованные задачи
        tasks = get_filtered_tasks(employee, status, due_date, task_type)

        # Очищаем таблицу и добавляем отфильтрованные задачи
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        for task in tasks:
            self.task_tree.insert("", tk.END, values=task)

    def get_default_due_date(self):
        """Возвращает стандартный срок исполнения (через неделю)"""
        return datetime.now() + timedelta(days=7)

    def save_task(self):
        """Добавляет новую задачу или обновляет существующую"""
        task_type = self.task_type_var.get().strip()
        employee_name = self.employee_id_var.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()  # Получаем текст из текстового поля
        status = self.status_var.get().strip()
        due_date = self.due_date_picker.get_date().strftime('%d.%m.%y')

        # Проверка обязательных полей
        if not task_type or not employee_name or not description:
            messagebox.showwarning("Ошибка", "Пожалуйста, заполните все обязательные поля.")
            return

        # Проверка корректности статуса
        if status not in ['ожидание', 'в процессе', 'завершено']:
            messagebox.showwarning("Ошибка", "Некорректный статус. Пожалуйста, выберите один из допустимых статусов.")
            return

        # Проверка на существование задачи для обновления
        task_id = self.get_selected_task_id()

        try:
            employee_id = get_employee_id_by_name(employee_name)

            if task_id:
                # Обновление существующей задачи
                try:
                    update_task_details(task_id, task_type, employee_id, description, status, due_date)
                    messagebox.showinfo("Успех", "Задача успешно обновлена.")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось обновить задачу: {str(e)}")
            else:
                # Добавление новой задачи
                try:
                    add_task(task_type, employee_id, description, status, due_date)
                    messagebox.showinfo("Успех", "Задача успешно добавлена.")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось сохранить задачу: {str(e)}")

            # Очистка формы и обновление списка задач
            self.clear_form()
            self.load_tasks(self.user_role, self.user_id)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось найти сотрудника: {str(e)}")

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
            # Создаем список для отображения в формате "Фамилия Имя Отчество (ID)"
            employee_list = [f"{emp[1]} {emp[2]} {emp[3]} ({emp[0]})" for emp in employees]
            return employee_list
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить список сотрудников: {str(e)}")
            return []

    def on_task_select(self, event):
        """Автозаполняет форму данными выбранной задачи"""
        selected_item = self.task_tree.selection()
        if selected_item:
            # Получаем значения выбранной строки
            task_values = self.task_tree.item(selected_item, 'values')
            task_id = task_values[0]
            task_type = task_values[1]
            description = task_values[2]
            employee_name = task_values[3]
            due_date = task_values[4]
            status = task_values[5]

            # Заполняем поля формы
            self.task_type_var.set(task_type)
            self.description_text.delete("1.0", tk.END)
            self.description_text.insert(tk.END, description)
            self.employee_id_var.set(employee_name)
            self.status_var.set(status)
            self.due_date_picker.set_date(datetime.strptime(due_date, '%d.%m.%y'))

    def on_click_outside(self, event):
        """Снимает выделение с Treeview, если клик на пустом месте"""
        # Проверяем, была ли строка выбрана
        if not self.task_tree.identify_row(event.y):
            # Если строка не была выбрана, то снимаем выделение
            self.task_tree.selection_remove(self.task_tree.selection())
            # Также очищаем форму, чтобы не путать добавление с редактированием
            self.clear_form()

