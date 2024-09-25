# login_view.py
import tkinter as tk
from tkinter import messagebox
from desktop_app.models.database_manager import authenticate_employee
import sqlite3
import hashlib  # Для хеширования паролей

DATABASE = 'hotel_management.db'

class LoginView(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Авторизация")
        self.geometry("400x300")  # Устанавливаем размер окна (ширина x высота)

        # Теперь создаем элементы для ввода логина и пароля
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        tk.Label(self, text="Имя пользователя:").pack(pady=10)
        tk.Entry(self, textvariable=self.username_var).pack(pady=5)

        tk.Label(self, text="Пароль:").pack(pady=10)
        tk.Entry(self, textvariable=self.password_var, show="*").pack(pady=5)

        tk.Button(self, text="Войти", command=self.login).pack(pady=20)

    def login(self):
        username = self.username_var.get()
        password = self.password_var.get()

        if not username or not password:
            messagebox.showwarning("Ошибка", "Заполните все поля")
            return

        result = authenticate_employee(username, password)

        if result:
            employee_id, role = result
            self.grant_access(role, username)
        else:
            messagebox.showerror("Ошибка", "Неправильное имя пользователя или пароль")

    def grant_access(self, role, username):
        """Открытие основного приложения с правами сотрудника"""
        self.master.show_main_app(role, username)  # Передаем роль сотрудника в основное приложение
        self.destroy()  # Закрываем окно авторизации

