import tkinter as tk
from tkinter import ttk, messagebox
from desktop_app.models.database_manager import add_employee, get_employees_full


class EmployeeListView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Фрейм для таблицы
        table_frame = tk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Создаем таблицу сотрудников
        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Фамилия", "Имя", "Отчество", "Телефон", "Логин", "Пароль", "Должность", "График", "Роль"),
            show="headings"
        )

        # Определение заголовков
        self.tree.heading("ID", text="ID")
        self.tree.heading("Фамилия", text="Фамилия")
        self.tree.heading("Имя", text="Имя")
        self.tree.heading("Отчество", text="Отчество")
        self.tree.heading("Телефон", text="Телефон")
        self.tree.heading("Логин", text="Логин")
        self.tree.heading("Пароль", text="Пароль")
        self.tree.heading("Должность", text="Должность")
        self.tree.heading("График", text="График")
        self.tree.heading("Роль", text="Роль")

        # Устанавливаем ширину столбцов
        self.tree.column("ID", width=50, anchor=tk.CENTER, stretch=False)  # ID скрыт (узкая ширина)
        self.tree.column("Фамилия", width=150, anchor=tk.W)
        self.tree.column("Имя", width=150, anchor=tk.W)
        self.tree.column("Отчество", width=150, anchor=tk.W)
        self.tree.column("Телефон", width=120, anchor=tk.W)
        self.tree.column("Логин", width=120, anchor=tk.W)
        self.tree.column("Пароль", width=120, anchor=tk.W)
        self.tree.column("Должность", width=150, anchor=tk.W)
        self.tree.column("График", width=150, anchor=tk.W)
        self.tree.column("Роль", width=100, anchor=tk.W)

        # Добавляем таблицу на скроллинг
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Кнопки для управления сотрудниками
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Обновить", command=self.load_employees).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Редактировать", command=self.edit_employee).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Удалить", command=self.delete_employee).pack(side=tk.LEFT, padx=5)

        # Загрузка данных в таблицу
        self.load_employees()

        # Форма для добавления нового сотрудника
        self.create_employee_form()
        self.tree.bind("<<TreeviewSelect>>", self.on_employee_select)

    def create_employee_form(self):
        """Создает форму для добавления нового сотрудника"""
        form_frame = tk.Frame(self)
        form_frame.pack(pady=20, fill=tk.X)

        self.last_name_var = tk.StringVar()
        self.first_name_var = tk.StringVar()
        self.middle_name_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.position_var = tk.StringVar()
        self.schedule_var = tk.StringVar()
        self.role_var = tk.StringVar(value="администратор")

        tk.Label(form_frame, text="Фамилия:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        tk.Entry(form_frame, textvariable=self.last_name_var).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Имя:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        tk.Entry(form_frame, textvariable=self.first_name_var).grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Отчество:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        tk.Entry(form_frame, textvariable=self.middle_name_var).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Логин:").grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        tk.Entry(form_frame, textvariable=self.username_var).grid(row=1, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Пароль:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        tk.Entry(form_frame, textvariable=self.password_var, show="*").grid(row=2, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Телефон:").grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        tk.Entry(form_frame, textvariable=self.phone_var).grid(row=2, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Должность:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        tk.Entry(form_frame, textvariable=self.position_var).grid(row=3, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="График:").grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)
        tk.Entry(form_frame, textvariable=self.schedule_var).grid(row=3, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="Роль:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        role_menu = ttk.OptionMenu(form_frame, self.role_var, "администратор", "администратор", "менеджер")
        role_menu.grid(row=4, column=1, padx=5, pady=5)

        # Кнопка добавления сотрудника
        tk.Button(form_frame, text="Добавить сотрудника", command=self.add_employee).grid(row=5, column=0, columnspan=4,
                                                                                          pady=10)

    def load_employees(self):
        """Загружает список сотрудников из базы данных в таблицу"""
        self.tree.delete(*self.tree.get_children())  # Очищаем текущие данные в таблице

        employees = get_employees_full()
        for emp in employees:
            # ID, Фамилия, Имя, Отчество, Телефон, Логин, Пароль, Должность, График, Роль
            self.tree.insert("", "end",
                             values=(emp[0], emp[1], emp[2], emp[3], emp[4], emp[5], emp[6], emp[7], emp[8], emp[9]))

    def add_employee(self):
        """Добавляет нового сотрудника в базу данных и обновляет таблицу"""
        last_name = self.last_name_var.get().strip()
        first_name = self.first_name_var.get().strip()
        middle_name = self.middle_name_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        phone = self.phone_var.get().strip()
        position = self.position_var.get().strip()
        schedule = self.schedule_var.get().strip()
        role = self.role_var.get()

        if not all([last_name, first_name, username, password, phone, position, role]):
            messagebox.showwarning("Ошибка", "Все поля должны быть заполнены")
            return

        try:
            add_employee(last_name, first_name, middle_name, phone, username, password, position, schedule, role)
            messagebox.showinfo("Успех", "Сотрудник успешно добавлен")
            self.load_employees()  # Обновляем таблицу
            # Очищаем поля формы после добавления
            self.last_name_var.set("")
            self.first_name_var.set("")
            self.middle_name_var.set("")
            self.username_var.set("")
            self.password_var.set("")
            self.phone_var.set("")
            self.position_var.set("")
            self.schedule_var.set("")
            self.role_var.set("администратор")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить сотрудника: {e}")

    def edit_employee(self):
        """Редактирование выбранного сотрудника"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите сотрудника для редактирования")
            return

        employee_data = self.tree.item(selected_item)["values"]
        employee_id = employee_data[0]

        # TODO: Реализовать логику редактирования сотрудника (открытие окна для редактирования и сохранение изменений)
        messagebox.showinfo("Редактировать", f"Окно редактирования сотрудника с ID {employee_id}")

    def delete_employee(self):
        """Удаление выбранного сотрудника"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите сотрудника для удаления")
            return

        employee_data = self.tree.item(selected_item)["values"]
        employee_id = employee_data[0]

        response = messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого сотрудника?")
        if response:
            try:
                from desktop_app.models.database_manager import delete_employee_by_id  # Импорт функции для удаления
                delete_employee_by_id(employee_id)
                messagebox.showinfo("Успех", "Сотрудник успешно удален")
                self.load_employees()  # Обновляем таблицу после удаления
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить сотрудника: {e}")

    def on_employee_select(self, event):
        """Заполнение полей формы данными выбранного сотрудника для редактирования"""
        selected_item = self.tree.selection()  # Получаем выбранный элемент в Treeview
        if selected_item:
            employee_info = self.tree.item(selected_item)["values"]  # Получаем данные о сотруднике

            # Заполняем поля формы данными о выбранном сотруднике
            self.last_name_var.set(employee_info[1])  # Фамилия
            self.first_name_var.set(employee_info[2])  # Имя
            self.middle_name_var.set(employee_info[3])  # Отчество
            self.phone_var.set(employee_info[4])  # Телефон
            self.username_var.set(employee_info[5])  # Логин
            self.password_var.set(employee_info[6])  # Пароль
            self.position_var.set(employee_info[7])  # Должность
            self.schedule_var.set(employee_info[8])  # График
            self.role_var.set(employee_info[9])  # Роль
