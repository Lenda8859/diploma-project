import tkinter as tk
from tkinter import messagebox
from desktop_app.models.database_manager import add_employee
import re

class EmployeeRegistration(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(padx=20, pady=20)

        self.name_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.role_var = tk.StringVar(value="администратор")

        tk.Label(self, text="Имя:").pack(pady=5)
        tk.Entry(self, textvariable=self.name_var).pack(pady=5)

        tk.Label(self, text="Имя пользователя (логин):").pack(pady=5)
        tk.Entry(self, textvariable=self.username_var).pack(pady=5)

        tk.Label(self, text="Пароль:").pack(pady=5)
        tk.Entry(self, textvariable=self.password_var, show="*").pack(pady=5)

        tk.Label(self, text="Телефон (+7 xxx xxx xx xx):").pack(pady=5)
        tk.Entry(self, textvariable=self.phone_var).pack(pady=5)

        tk.Label(self, text="Роль:").pack(pady=5)
        role_menu = tk.OptionMenu(self, self.role_var, "администратор", "менеджер")
        role_menu.pack(pady=5)

        tk.Button(self, text="Добавить сотрудника", command=self.register_employee).pack(pady=10)


    def register_employee(self):
        name = self.name_var.get()
        username = self.username_var.get()
        password = self.password_var.get()
        phone = self.phone_var.get()
        role = self.role_var.get()

        if not name or not username or not password or not phone:
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        phone_pattern = r'^\+7 \d{3} \d{3} \d{2} \d{2}$'
        if not re.match(phone_pattern, phone):
            messagebox.showerror("Ошибка", "Номер телефона должен быть в формате +7 xxx xxx xx xx.")
            return

        try:
            add_employee(
                last_name="Фамилия",  # Вам нужно добавить ввод для фамилии в реальной версии
                first_name=name,
                middle_name=None,
                phone=phone,
                username=username,
                password=password,
                position="Сотрудник",  # Установить нужную должность
                role=role
            )
            messagebox.showinfo("Успех", f"Сотрудник {name} успешно добавлен!")
            self.parent.destroy()  # Закрыть окно после добавления
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить сотрудника: {e}")

    def main():
        # Создаем главное окно Tkinter
        root = tk.Tk()
        root.title("Управление сотрудниками")

        # Инициализируем виджет EmployeeRegistration
        app = EmployeeRegistration(root)

        root.mainloop()
