import tkinter as tk
from tkinter import messagebox
from desktop_app.models.database_manager import authenticate_employee
import hashlib  # Для хеширования паролей

DATABASE = 'hotel_management.db'

class LoginView(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        # Настройки окна
        self.parent = parent
        self.title("Авторизация")
        self.geometry("400x300")  # Устанавливаем размер окна (ширина x высота)
        self.resizable(False, False)  # Фиксируем размер окна, чтобы он не менялся

        # Элементы для ввода логина и пароля
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        tk.Label(self, text="Имя пользователя:").pack(pady=10)
        tk.Entry(self, textvariable=self.username_var).pack(pady=5)

        tk.Label(self, text="Пароль:").pack(pady=10)
        tk.Entry(self, textvariable=self.password_var, show="*").pack(pady=5)

        tk.Button(self, text="Войти", command=self.login).pack(pady=20)

    def login(self):
        """Выполняет проверку логина и пароля"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        # Проверка, что поля заполнены
        if not username or not password:
            messagebox.showwarning("Ошибка", "Заполните все поля")
            return

        # Аутентификация пользователя
        result = authenticate_employee(username, password)

        # Проверка результата аутентификации
        if result:
            employee_id, role = result
            self.grant_access(role, username)
        else:
            messagebox.showerror("Ошибка", "Неправильное имя пользователя или пароль")

    def grant_access(self, role, username):
        """Открытие основного приложения с правами сотрудника"""
        # Проверка, является ли self.master экземпляром главного приложения
        if hasattr(self.parent, 'show_main_app'):
            self.parent.show_main_app(role, username)  # Передаем роль и имя пользователя в основное приложение
            self.destroy()  # Закрываем окно авторизации
        else:
            messagebox.showerror("Ошибка", "Не удалось найти главное приложение для авторизации")