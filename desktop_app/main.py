import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from tkinter import messagebox
import tkinter as tk
from desktop_app.views.room_view import RoomView # Импортируем RoomView
from desktop_app.views.client_view import ClientView  # Импортируем ClientView
from desktop_app.views.reservation_view import ReservationView
from desktop_app.views.login_view import LoginView
from desktop_app.views.employee_view import EmployeeListView
from desktop_app.models.database_manager import apply_migrations, create_tables, get_user_id
from desktop_app.views.task_view import TaskView
from desktop_app.views.report_view import ReportView

# Переменная с путём к базе данных
DATABASE = 'F:/Hotel Management System/hotel_management.db'
#

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Hotel Management System")
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

        # Меню "Отчеты"
        report_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Отчеты", menu=report_menu)
        report_menu.add_command(label="Просмотр отчетов", command=self.open_report_view)

        # Начальные значения атрибутов пользователя
        self.user_role = None
        self.user_id = None

        # Флаг, чтобы предотвратить рекурсивный вызов open_task_view
        self.task_view_opened = False

        # Удаляем инициализацию ReportView из конструктора

        # Меню "Номера"
        room_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Номера", menu=room_menu)
        room_menu.add_command(label="Номера", command=self.open_room_view)

        # Меню "Клиенты"
        client_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Клиенты", menu=client_menu)
        client_menu.add_command(label="Просмотр клиентов", command=self.open_client_view)

        # Меню "Бронирования"
        reservation_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Бронирования", menu=reservation_menu)
        reservation_menu.add_command(label="Бронирования", command=lambda: self.open_reservation_view())


    def open_task_view(self, user_role, user_id=None):
        """Открывает фрейм для задач"""
        #print("Переключение на модуль 'Задачи'")
        # Проверяем флаг, чтобы предотвратить повторное открытие
        if not self.task_view_opened:
            self.clear_frame()  # Удаляем предыдущий фрейм

            task_view = TaskView(self.container, user_role=user_role, user_id=user_id)
            task_view.pack(fill=tk.BOTH, expand=True)

            # Устанавливаем флаг после первого открытия
            self.task_view_opened = True

    def show_main_app(self, role, username, user_id=None):
        print(
            f"Метод show_main_app вызван! Роль: {role}, Пользователь: {username}, ID пользователя: {user_id}")  # Отладка
        self.user_role = role
        self.user_id = user_id
        self.username = username
        self.login_view.destroy()
        self.deiconify()
        self.update_title()

        # Вызов правильного меню в зависимости от роли
        if self.user_role == 'менеджер':
            self.create_manager_menu()
        elif self.user_role == 'администратор':
            self.create_receptionist_menu()
        elif self.user_role == 'системный администратор':
            self.create_system_admin_menu()

        # Открываем модуль задач только один раз
        if not self.task_view_opened:
            #print(f"Перед вызовом open_task_view: Роль: {self.user_role}, ID пользователя: {self.user_id}")
            self.open_task_view(self.user_role, self.user_id)

    def update_title(self):
        """Обновляет заголовок окна с именем пользователя"""
        self.title(f"Hotel Management System - Вошел: {self.username}")

    def logout(self):
        """Диалог для выхода или смены пользователя"""
        response = messagebox.askyesnocancel(
            "Выход",
            "Вы хотите сменить пользователя или закрыть приложение?\n\n"
            "Нажмите 'Да', чтобы сменить пользователя.\n"
            "Нажмите 'Нет', чтобы выйти из приложения.\n"
            "Нажмите 'Отмена', чтобы остаться в системе."
        )

        if response is None:  # Нажата кнопка "Отмена"
            return
        elif response:  # Нажата кнопка "Да" (сменить пользователя)
            self.withdraw()  # Скрываем главное окно
            self.login_view = LoginView(self)  # Показываем окно авторизации
            self.login_view.grab_set()
        else:  # Нажата кнопка "Выход" (закрыть приложение)
            self.quit()  # Закрываем приложение


    def create_manager_menu(self):
        """Создаем меню для менеджера"""
        #print("Создание меню для менеджера...")  # Отладка
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Меню "Управление номерами"
        room_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Номера", menu=room_menu)
        room_menu.add_command(label="Просмотр номеров", command=self.open_room_view)

        # Меню "Управление клиентами"
        client_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Клиенты", menu=client_menu)
        client_menu.add_command(label="Просмотр клиентов", command=self.open_client_view)

        # Меню "Управление бронированиями"
        reservation_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Бронирования", menu=reservation_menu)
        reservation_menu.add_command(label="Бронирования", command=self.open_reservation_view)

        # Меню "Управление Сотрудниками"
        employee_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Сотрудники", menu=employee_menu)
        employee_menu.add_command(label="Просмотр сотрудников", command=self.open_employee_list_view)

        # Меню "Управление задачами"
        task_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Задачи", menu=task_menu)
        task_menu.add_command(label="Просмотр задач", command=lambda: self.open_task_view(self.user_role, self.user_id))

        # Меню "Управление отчетами"
        task_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Отчет", menu=task_menu)
        # task_menu.add_command(label="Просмотр отчета", command=lambda: self.open_report_view)
        task_menu.add_command(label="Просмотр отчета", command=self.open_report_view)

        # Пункт "Выйти"t
        menubar.add_command(label="Выйти", command=self.logout)

        self.update_idletasks()  # Обновляем графический интерфейс




    def create_receptionist_menu(self):
        """Создаем меню для ресепшиониста"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # Меню "Управление номерами"
        room_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Номера", menu=room_menu)
        room_menu.add_command(label="Просмотр номеров", command=self.open_room_view)

        # Меню "Управление клиентами"
        client_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Клиены", menu=client_menu)
        client_menu.add_command(label="Просмотр клиентов", command=self.open_client_view)

        # Меню "Управление бронированиями"
        reservation_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Бронирования", menu=reservation_menu)
        reservation_menu.add_command(label="Бронирования", command=self.open_reservation_view)

        # Меню "Управление задачами"
        task_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Задачи", menu=task_menu)
        task_menu.add_command(label="Просмотр задач", command=lambda: self.open_task_view(self.user_role, self.user_id))

        # Пункт "Выйти"
        menubar.add_command(label="Выйти", command=self.logout)



    def open_employee_list_view(self):
        """Открывает фрейм для просмотра и редактирования сотрудников"""
        #print("Открытие окна просмотра сотрудников...")  # Отладка
        self.clear_frame()  # Очищает контейнер от предыдущего содержимого
        employee_list_view = EmployeeListView(self.container)  # Загружаем фрейм для сотрудников в контейнер
        employee_list_view.pack(fill=tk.BOTH, expand=True)

    def open_room_view(self):
        """Открывает фрейм для управления номерами"""
        self.clear_frame()  # Удаляем предыдущий фрейм
        room_view = RoomView(self.container)  # Открываем фрейм для номеров
        room_view.pack(fill=tk.BOTH, expand=True)

    def open_reservation_view(self):
        self.clear_frame()  # Удаляем предыдущие фреймы
        reservation_view = ReservationView(self.container)
        reservation_view.pack(fill=tk.BOTH, expand=True)
        reservation_view.load_reservations()  # Загрузка бронирований
    def open_client_view(self):
        """Открытие окна управления клиентами"""
        self.clear_frame()
        client_view = ClientView(self.container)  # Загружаем фрейм для клиентов в контейнер
        client_view.pack(fill=tk.BOTH, expand=True)

    def open_report_view(self):
        """Открывает фрейм для отчетов"""
        #print("Открывается модуль отчетов...")  # Отладочное сообщение
        self.clear_frame()  # Удаляем предыдущий фрейм
        report_view = ReportView(self.container)  # Открываем фрейм для отчетов
        report_view.pack(fill=tk.BOTH, expand=True)

    def clear_frame(self):
        """Очищает содержимое контейнера"""
        #print("Очистка контейнера!")  # Для отладки

        # Убедитесь, что task_view_opened сбрасывается при очистке
        self.task_view_opened = False

        # Убедитесь, что контейнер существует
        if self.container is not None and self.container.winfo_exists():
            for widget in self.container.winfo_children():
                widget.destroy()
        else:
            # Если контейнер не существует, пересоздайте его
            self.container = tk.Frame(self)
            self.container.pack(fill=tk.BOTH, expand=True)

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
    #print(f"Файл базы данных найден по пути: {DATABASE}")
    #create_tables()
    #apply_migrations()

    # Запуск основного приложения
    app = MainApp()

    # Запуск основного цикла приложения
    app.mainloop()




