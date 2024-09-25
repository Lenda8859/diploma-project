import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from tkinter import messagebox

import tkinter as tk
from desktop_app.views.room_view import RoomView # Импортируем RoomView
from desktop_app.views.client_view import ClientView  # Импортируем ClientView
from desktop_app.views.reservation_view import ReservationView
from desktop_app.views.login_view import LoginView
from desktop_app.views.employee_view import EmployeeRegistration
from desktop_app.models.database_manager import apply_migrations, generate_clients, generate_reservations, initialize_rooms, create_tables
from desktop_app.models.database_manager import add_employee




# Переменная с путём к базе данных
DATABASE = 'F:/hotel_management_project/hotel_management.db'
#

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Управление гостиницей")
        self.geometry("1750x720")

        # Скрываем основное окно до авторизации
        self.withdraw()

        # Показываем окно авторизации при запуске
        self.login_view = LoginView(self)
        self.login_view.grab_set()

        # Фрейм для отображения содержимого
        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Меню
        menubar = tk.Menu(self)
        self.config(menu=menubar)



        # Меню "Номера"
        room_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Номера", menu=room_menu)
        room_menu.add_command(label="Управление номерами", command=self.open_room_view)

        # Добавь рядом пункт для управления клиентами
        client_menu = tk.Menu(menubar, tearoff=0)  # Используем правильное имя 'menubar'
        menubar.add_cascade(label="Управление клиентами", menu=client_menu)
        client_menu.add_command(label="Просмотр клиентов", command=self.open_client_view)

        # Меню "Бронирования"
        reservation_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Бронирования", menu=reservation_menu)
        #reservation_menu.add_command(label="Управление бронированиями", command=self.open_reservation_view)
        reservation_menu.add_command(label="Управление бронированиями", command=lambda: print("Пункт меню выбран!") or self.open_reservation_view())


        # Меню "Выход"
        menubar.add_command(label="Выход", command=self.quit)

    def show_main_app(self, role, username):
        """Показываем основное приложение в зависимости от роли сотрудника и выводим имя пользователя"""
        self.role = role
        self.username = username  # Сохраняем имя пользователя
        print(f"Вошел пользователь с ролью: {self.role}")  # Отладка
        self.login_view.destroy()  # Закрываем окно авторизации
        self.deiconify()  # Показываем главное окно

        # Устанавливаем заголовок окна с указанием имени пользователя
        self.update_title()
        self.create_manager_menu()  # Создаем меню для менеджера

        if self.role == 'manager':
            self.create_manager_menu()  # Меню для менеджера
        elif self.role == 'receptionist':
            self.create_receptionist_menu()  # Меню для ресепшиониста

    def update_title(self):
        """Обновляет заголовок окна с именем пользователя"""
        self.title(f"Управление гостиницей - Вошел: {self.username}")

    def logout(self):
        """Диалог для выхода или смены пользователя"""
        response = messagebox.askyesnocancel(
            "Выход",
            "Вы хотите сменить пользователя или закрыть приложение?\n\n"
            "Нажмите 'Да', чтобы сменить пользователя.\n"
            "Нажмите 'Нет', чтобы закрыть приложение.\n"
            "Нажмите 'Отмена', чтобы остаться в системе."
        )

        if response is None:  # Нажата кнопка "Отмена"
            return
        elif response:  # Нажата кнопка "Да" (сменить пользователя)
            self.withdraw()  # Скрываем главное окно
            self.login_view = LoginView(self)  # Показываем окно авторизации
            self.login_view.grab_set()
        else:  # Нажата кнопка "Нет" (закрыть приложение)
            self.quit()  # Закрываем приложение

    def create_manager_menu(self):
        """Создаем меню для менеджера"""
        print("Создание меню для менеджера...")  # Отладка
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # # Устанавливаем заголовок окна с указанием имени пользователя
        # self.update_title()

        # Меню "Управление номерами"
        room_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Управление номерами", menu=room_menu)
        room_menu.add_command(label="Просмотр номеров", command=self.open_room_view)

        # Меню "Управление клиентами"
        client_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Управление клиентами", menu=client_menu)
        client_menu.add_command(label="Просмотр клиентов", command=self.open_client_view)

        # Меню "Управление бронированиями"
        reservation_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Управление бронированиями", menu=reservation_menu)
        reservation_menu.add_command(label="Управление бронированиями", command=self.open_reservation_view)

        # Меню "Управление сотрудниками"
        print("Добавление пункта 'Управление сотрудниками' в меню")  # Отладка
        employee_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Управление сотрудниками", menu=employee_menu)
        employee_menu.add_command(label="Добавить сотрудника", command=self.open_employee_registration)

        # Пункт "Выйти"
        menubar.add_command(label="Выйти", command=self.logout)

        self.update_idletasks()  # Обновляем графический интерфейс



    def create_receptionist_menu(self):
        """Создаем меню для ресепшиониста"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Меню "Управление номерами"
        room_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Управление номерами", menu=room_menu)
        room_menu.add_command(label="Просмотр номеров", command=self.open_room_view)

        # Меню "Управление клиентами"
        client_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Управление клиентами", menu=client_menu)
        client_menu.add_command(label="Просмотр клиентов", command=self.open_client_view)

        # Меню "Управление бронированиями"
        reservation_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Управление бронированиями", menu=reservation_menu)
        reservation_menu.add_command(label="Управление бронированиями", command=self.open_reservation_view)

        # Пункт "Выйти"
        menubar.add_command(label="Выйти", command=self.logout)

    def open_employee_registration(self):
        """Открывает фрейм для управления сотрудниками"""
        print("Открытие окна регистрации сотрудников...")  # Отладка
        self.clear_frame()  # Очищает контейнер от предыдущего содержимого
        employee_registration = EmployeeRegistration(self.container)  # Загружаем фрейм для сотрудников в контейнер
        employee_registration.pack(fill=tk.BOTH, expand=True)

    def open_room_view(self):
        """Открывает фрейм для управления номерами"""
        self.clear_frame()  # Удаляем предыдущий фрейм
        room_view = RoomView(self.container)  # Открываем фрейм для номеров
        room_view.pack(fill=tk.BOTH, expand=True)

    def open_reservation_view(self):
        print("Модуль бронирований открыт!")  # Отладочное сообщение
        self.clear_frame()  # Удаляем предыдущие фреймы
        reservation_view = ReservationView(self.container)
        reservation_view.pack(fill=tk.BOTH, expand=True)
        reservation_view.load_reservations()  # Загрузка бронирований
    def open_client_view(self):
        """Открытие окна управления клиентами"""
        self.clear_frame()
        client_view = ClientView(self.container)  # Загружаем фрейм для клиентов в контейнер
        client_view.pack(fill=tk.BOTH, expand=True)

    def clear_frame(self):
        """Очищает содержимое контейнера"""
        print("Очистка контейнера!")  # Для отладки
        for widget in self.container.winfo_children():
            widget.destroy()

    def save_state(self):
        """Сохраняет состояние формы"""
        self.saved_client_name = self.client_name_var.get()
        self.saved_room_id = self.room_id_var.get()
        # Сохраняем другие данные формы

    def restore_state(self):
        """Восстанавливает состояние формы при возвращении в модуль"""
        self.client_name_var.set(self.saved_client_name)
        self.room_id_var.set(self.saved_room_id)
        # Восстанавливаем другие данные формы



if __name__ == "__main__":
    print(f"Файл базы данных найден по пути: {DATABASE}")
    create_tables()
    apply_migrations()
    initialize_rooms()


    # generate_clients()
    # generate_reservations()

    # Добавляем сотрудника с проверкой уникальности username
    add_employee('SuperUser', 'admin', None, '+7 999 258 66 33', 'admin', '000', 'Менеджер', role='менеджер')

    # Запуск основного приложения
    app = MainApp()
    app.mainloop()




