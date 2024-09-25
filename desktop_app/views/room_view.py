import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from desktop_app.models.database_manager import get_all_rooms, update_room, room_exists, get_rooms_filtered, get_room_counts
from desktop_app.controllers.room_controller import get_change_room_status



class RoomView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Создание таблицы для отображения номеров
        self.room_tree = ttk.Treeview(self, columns=("id", "Номер", "Тип", "Статус", "Стоимость", "Описание"), show="headings")

        # Определяем заголовки для таблицы
        self.room_tree.heading("id", text="ID")
        self.room_tree.heading("Номер", text="Номер комнаты")
        self.room_tree.heading("Тип", text="Тип комнаты")
        self.room_tree.heading("Статус", text="Статус комнаты")
        self.room_tree.heading("Стоимость", text="Стоимость")
        self.room_tree.heading("Описание", text="Описание")

        # Задаем размеры столбцов
        self.room_tree.column("id", width=0, stretch=tk.NO)  # Скрываем колонку ID
        self.room_tree.column("Номер", width=100)
        self.room_tree.column("Тип", width=100)
        self.room_tree.column("Статус", width=120)
        self.room_tree.column("Стоимость", width=100)
        self.room_tree.column("Описание", width=200)

        self.room_tree.pack(fill=tk.BOTH, expand=True)

        # Инициализация переменных
        self.room_id_var = tk.StringVar()
        self.room_number_var = tk.IntVar()
        self.room_type_var = tk.StringVar()
        self.room_status_var = tk.StringVar()
        self.room_price_var = tk.DoubleVar()
        self.room_description_var = tk.StringVar()
        self.search_room_type_var = tk.StringVar() # Инициализация переменной для фильтра типа комнаты
        self.search_room_status_var = tk.StringVar() # Инициализация переменной для фильтра статуса комнаты
        self.search_room_price_var = tk.DoubleVar() # Инициализация переменной для фильтра цены

        # Загрузка номеров в таблицу
        self.load_rooms()

        # Создание кнопки для изменения статуса номера
        self.create_action_buttons_room()

        # Вызов функции для создания строки поиска
        self.create_search_bar_room()

        # Добавление счетчика в интерфейс
        self.create_room_counter()

        # Загрузка списка комнат
        self.load_rooms()

    def create_room_counter(self):
        """Создает счетчик для отображения количества комнат по типам и статусам"""
        self.room_counter_frame = tk.Frame(self)
        self.room_counter_frame.pack(fill=tk.X, pady=10)

        self.room_count_label = tk.Label(self.room_counter_frame, text="")
        self.room_count_label.pack()

        # Обновляем счетчик при загрузке
        self.update_room_counter()

    def update_room_counter(self):
        """Обновляет счетчик количества комнат по типу и статусу"""
        room_counts = get_room_counts()  # Получаем данные из базы

        # Формируем текст для отображения
        count_text = ""
        for room_type, status, count in room_counts:
            count_text += f"{room_type} - {count} {status}\n"

        self.room_count_label.config(text=count_text)

    def load_rooms(self):
        """Загрузка номеров в таблицу"""
        rooms = get_all_rooms()

        # Очищаем таблицу перед добавлением новых данных
        for item in self.room_tree.get_children():
            self.room_tree.delete(item)

        for room in rooms:
            # Форматирование цены с добавлением текста " руб"
            formatted_price = f"{room[4]:,.0f} руб"  # Без дробной части
            self.room_tree.insert("", tk.END, values=(
                room[0],  # ID
                room[1],  # Номер комнаты
                room[2],  # Тип комнаты
                room[3],  # Статус комнаты
                formatted_price,  # Форматированная стоимость
                room[5]  # Описание
            ))

    def create_form(self):
        form_frame = tk.Frame(self)
        form_frame.pack(fill=tk.X, pady=10)

        tk.Label(form_frame, text="Номер комнаты").pack(side=tk.LEFT, padx=5)
        tk.Entry(form_frame, textvariable=self.room_number_var).pack(side=tk.LEFT, padx=5)

        tk.Label(form_frame, text="Тип комнаты").pack(side=tk.LEFT, padx=5)
        ttk.Combobox(form_frame, textvariable=self.room_type_var, values=["Стандарт", "Сьют", "Делюкс"]).pack(side=tk.LEFT, padx=5)

        tk.Label(form_frame, text="Статус").pack(side=tk.LEFT, padx=5)
        ttk.Combobox(form_frame, textvariable=self.room_status_var, values=["свободно", "забронировано", "занято", "на обслуживании"]).pack(side=tk.LEFT, padx=5)

        tk.Label(form_frame, text="Стоимость").pack(side=tk.LEFT, padx=5)
        tk.Entry(form_frame, textvariable=self.room_price_var).pack(side=tk.LEFT, padx=5)

        tk.Label(form_frame, text="Описание").pack(side=tk.LEFT, padx=5)
        tk.Entry(form_frame, textvariable=self.room_description_var).pack(side=tk.LEFT, padx=5)

    def create_action_buttons_room(self):
        """Кнопки для изменения статуса номеров"""
        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, pady=10)

        # Кнопка для изменения статуса номера
        update_status_button = tk.Button(button_frame, text="Изменить статус", command=self.change_room_status)
        update_status_button.pack(side=tk.LEFT, padx=5)

    def change_room_status(self):
        """Функция для изменения статуса выбранной комнаты"""
        selected_item = self.room_tree.selection()  # Получаем выбранный элемент из таблицы
        if not selected_item:
            messagebox.showwarning("Ошибка", "Выберите номер для изменения статуса.")
            return

        room_info = self.room_tree.item(selected_item)["values"]
        room_id = room_info[0]  # ID комнаты
        new_status = self.search_room_status_var.get()  # Новый статус

        print(f"Отладка: Изменение статуса для комнаты {room_info[1]} (ID: {room_id}) на {new_status}")

        if not new_status:
            messagebox.showwarning("Ошибка", "Выберите новый статус для номера.")
            return

        try:
            get_change_room_status(room_id, new_status)  # Обновляем статус в базе
            messagebox.showinfo("Успех", f"Статус номера {room_info[1]} успешно обновлен на {new_status}")
            self.load_rooms()  # Перезагружаем список комнат
            self.update_room_counter()  # Обновляем счетчик
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить статус номера: {str(e)}")
            print(f"Ошибка при изменении статуса номера: {e}")

    def create_search_bar_room(self):
        """Создает строку поиска для фильтрации номеров и изменения статуса"""
        search_frame = tk.Frame(self)
        search_frame.pack(fill=tk.X, pady=10)

        # Поле для выбора типа комнаты
        tk.Label(search_frame, text="Тип комнаты").pack(side=tk.LEFT, padx=5)
        self.search_room_type_var = tk.StringVar()
        ttk.Combobox(search_frame, textvariable=self.search_room_type_var, values=["Стандарт", "Сьют", "Делюкс"]).pack(
            side=tk.LEFT, padx=5)

        # Поле для выбора статуса комнаты
        tk.Label(search_frame, text="Статус").pack(side=tk.LEFT, padx=5)
        self.search_room_status_var = tk.StringVar()
        ttk.Combobox(search_frame, textvariable=self.search_room_status_var,
                     values=["свободно", "забронировано", "занято", "на обслуживании"]).pack(side=tk.LEFT, padx=5)

        # Поле для ввода максимальной стоимости
        tk.Label(search_frame, text="Стоимость до").pack(side=tk.LEFT, padx=5)
        self.search_room_price_var = tk.DoubleVar()
        tk.Entry(search_frame, textvariable=self.search_room_price_var).pack(side=tk.LEFT, padx=5)

        # Кнопка поиска
        search_button = tk.Button(search_frame, text="Поиск", command=self.search_rooms)
        search_button.pack(side=tk.LEFT, padx=5)

    def search_rooms(self):
        """Фильтрация списка номеров по введенным критериям"""
        room_type = self.search_room_type_var.get()
        room_status = self.search_room_status_var.get()
        price_max = self.search_room_price_var.get()

        # Получаем фильтрованные данные из базы данных
        filtered_rooms = get_rooms_filtered(room_type, room_status, price_max)

        # Очищаем таблицу перед добавлением отфильтрованных данных
        for item in self.room_tree.get_children():
            self.room_tree.delete(item)

        # Добавляем отфильтрованные данные в таблицу
        for room in filtered_rooms:
            self.room_tree.insert("", tk.END,
                                  values=(room[0], room[1], room[2], room[3], f"{room[4]:,.2f} руб", room[5]))



    def clear_form(self):
        """Очистка полей формы"""
        self.room_number_var.set("")
        self.room_type_var.set("")
        self.room_status_var.set("")
        self.room_price_var.set(0)
        self.room_description_var.set("")
