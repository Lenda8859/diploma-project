import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from desktop_app.models.database_manager import DATABASE
from desktop_app.models.database_manager import get_all_rooms, update_room, room_exists, get_rooms_filtered, get_room_counts
import sqlite3
from desktop_app.controllers.room_controller import get_change_room_status, add_new_room


class RoomView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Создание таблицы для отображения номеров
        self.room_tree = ttk.Treeview(self, columns=("id", "Номер", "Тип", "Статус", "Стоимость", "Описание", "Вместимость", "Площадь", "Удобства"), show="headings")

        # Изменяем цвет основного окна
        self.parent.configure(bg="#e6e6e6")

        # Настройка стиля заголовка
        style = ttk.Style()
        style.configure("Treeview.Heading", background="#c0c0c0", foreground="black", font=("Arial", 10, "bold"))

        # Определяем заголовки для таблицы
        self.room_tree.heading("id", text="ID")
        self.room_tree.heading("Номер", text="Номер комнаты")
        self.room_tree.heading("Тип", text="Тип комнаты")
        self.room_tree.heading("Статус", text="Статус комнаты")
        self.room_tree.heading("Стоимость", text="Стоимость")
        self.room_tree.heading("Описание", text="Описание")
        self.room_tree.heading("Вместимость", text="Вместимость")
        self.room_tree.heading("Площадь", text="Площадь")
        self.room_tree.heading("Удобства", text="Удобства")


        # Задаем размеры столбцов
        self.room_tree.column("id", width=0, stretch=tk.NO)  # Скрываем колонку ID
        self.room_tree.column("Номер", width=100)
        self.room_tree.column("Тип", width=100)
        self.room_tree.column("Статус", width=120)
        self.room_tree.column("Стоимость", width=100, anchor="center")
        self.room_tree.column("Описание", width=200)
        self.room_tree.column("Вместимость", width=20, anchor="center")
        self.room_tree.column("Площадь", width=20, anchor="center")
        self.room_tree.column("Удобства", width=100)


        self.room_tree.pack(fill=tk.BOTH, expand=True)

        # Инициализация переменных
        self.room_id_var = tk.StringVar()
        self.room_number_var = tk.IntVar()
        self.room_type_var = tk.StringVar()
        self.room_status_var = tk.StringVar()
        self.room_price_var = tk.DoubleVar()
        self.room_description_var = tk.StringVar()
        self.search_room_type_var = tk.StringVar()
        self.search_room_status_var = tk.StringVar()
        self.search_room_price_var = tk.DoubleVar()
        self.room_capacity_var = tk.StringVar()
        self.room_area_var = tk.StringVar()
        self.room_amenities_var = tk.StringVar()


        # Загрузка номеров в таблицу
        self.load_rooms()

        # Создание кнопки для изменения статуса номера
        self.create_action_buttons_room()

        # Вызов функции для создания строки поиска
        self.create_search_bar_room()


        # Загрузка списка комнат
        self.load_rooms()

        self.create_listboxes()

        # Добавление счетчика в интерфейс
        self.create_room_counter()

        self.room_tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def create_listboxes(self):
        """Создание горизонтальных виджетов для многострочного отображения данных"""
        self.listbox_frame = tk.Frame(self)
        self.listbox_frame.pack(pady=10, side=tk.LEFT)  # Убедитесь, что Listbox находится слева

        # Создание кнопки "Сохранить изменения"
        self.save_button = tk.Button(self.listbox_frame, text="Сохранить изменения", command=self.save_changes, bg="#c0c0c0")
        self.save_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Описание
        self.description_label = tk.Label(self.listbox_frame, text="Описание:")
        self.description_label.grid(row=1, column=0, padx=5, sticky="w")
        self.description_text = tk.Text(self.listbox_frame, height=4, width=30, wrap=tk.WORD)
        self.description_text.grid(row=2, column=0, padx=5, pady=5)

        # Удобства
        self.amenities_label = tk.Label(self.listbox_frame, text="Удобства:")
        self.amenities_label.grid(row=1, column=1, padx=5, sticky="w")
        self.amenities_text = tk.Text(self.listbox_frame, height=4, width=30, wrap=tk.WORD)
        self.amenities_text.grid(row=2, column=1, padx=5, pady=5)

    def on_tree_select(self, event):
        """Обновление данных при выборе строки"""
        selected_item = self.room_tree.selection()[0]
        room_data = self.room_tree.item(selected_item, 'values')

        # Описание
        self.description_text.config(state=tk.NORMAL)  # Разрешить редактирование
        self.description_text.delete("1.0", tk.END)
        self.description_text.insert(tk.END, room_data[5])

        # Удобства
        self.amenities_text.config(state=tk.NORMAL)  # Разрешить редактирование
        self.amenities_text.delete("1.0", tk.END)
        self.amenities_text.insert(tk.END, room_data[8])

    def save_changes(self):
        """Сохранение изменений из виджетов в базу данных"""
        selected_item = self.room_tree.selection()[0]
        room_id = self.room_tree.item(selected_item)['values'][0]

        # Получаем текст из всех Text виджетов
        description = self.description_text.get("1.0", tk.END).strip()
        amenities = self.amenities_text.get("1.0", tk.END).strip()

        # Обновляем данные в базе данных без Примечаний
        with sqlite3.connect(DATABASE, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Номера
                SET Описание = ?, Удобства = ?
                WHERE id = ?
            """, (description, amenities, room_id))
            conn.commit()

        print(f"Изменения сохранены для номера {room_id}")

        # Обновляем отображение данных в TreeView
        self.load_rooms()




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

        # Настройка тегов для цветов строк
        self.room_tree.tag_configure("#fffacd", background="#fffacd")
        self.room_tree.tag_configure("#d0bee4", background="#d0bee4")
        self.room_tree.tag_configure("#ffb6c1", background="#ffb6c1")
        self.room_tree.tag_configure("#f0f0f0", background="#f0f0f0")
        self.room_tree.tag_configure("#d9d9d9", background="#d9d9d9")

        for index, room in enumerate(rooms):
            # Определяем цвет строки в зависимости от статуса
            status = room[3]  # Получаем статус из данных комнаты
            if status == "на обслуживании":
                row_color = "#fffacd"
            elif status == "забронировано":
                row_color = "#d0bee4"
            elif status == "занято":
                row_color = "#ffb6c1"
            else:  # Свободно
                row_color = "#f0f0f0" if index % 2 == 0 else "#d9d9d9"

            # Форматирование цены с добавлением текста " руб"
            formatted_price = f"{room[4]:,.0f} руб"

            # Добавление строки в Treeview с указанным тегом цвета
            self.room_tree.insert("", tk.END, values=(
                room[0],  # ID
                room[1],  # Номер комнаты
                room[2],  # Тип комнаты
                room[3],  # Статус комнаты
                formatted_price,  # Форматированная стоимость
                room[5],  # Описание (без разбиения на строки)
                room[6],  # Вместимость
                room[7],  # Площадь
                room[8],  # Удобства (без разбиения на строки)
            ), tags=(row_color,))

    def create_form(self):
        form_frame = tk.Frame(self, bg="#e6e6e6")
        form_frame.pack(fill=tk.X, pady=10)

        tk.Label(form_frame, text="Номер комнаты").pack(side=tk.LEFT, padx=5)
        tk.Entry(form_frame, textvariable=self.room_number_var).pack(side=tk.LEFT, padx=5)

        tk.Label(form_frame, text="Тип комнаты").pack(side=tk.LEFT, padx=5)
        ttk.Combobox(form_frame, textvariable=self.room_type_var, values=["Стандарт", "Сьют", "Делюкс"]).pack(
            side=tk.LEFT, padx=5)

        tk.Label(form_frame, text="Статус").pack(side=tk.LEFT, padx=5)
        ttk.Combobox(form_frame, textvariable=self.room_status_var,
                     values=["свободно", "забронировано", "занято", "на обслуживании"]).pack(side=tk.LEFT, padx=5)

        tk.Label(form_frame, text="Стоимость").pack(side=tk.LEFT, padx=5)
        tk.Entry(form_frame, textvariable=self.room_price_var).pack(side=tk.LEFT, padx=5)

        tk.Label(form_frame, text="Описание").pack(side=tk.LEFT, padx=5)
        tk.Entry(form_frame, textvariable=self.room_description_var).pack(side=tk.LEFT, padx=5)

        tk.Label(form_frame, text="Вместимость").pack(side=tk.LEFT, padx=5)
        tk.Entry(form_frame, textvariable=self.room_capacity_var).pack(side=tk.LEFT, padx=5)

        tk.Label(form_frame, text="Площадь").pack(side=tk.LEFT, padx=5)
        tk.Entry(form_frame, textvariable=self.room_area_var).pack(side=tk.LEFT, padx=5)

        tk.Label(form_frame, text="Удобства").pack(side=tk.LEFT, padx=5)
        tk.Entry(form_frame, textvariable=self.room_amenities_var).pack(side=tk.LEFT, padx=5)


    def save_room_data(self):
        """
        Сохранение данных о номере, переданных из RoomView.
        """
        if not self.validate_room_data():
            return  # Прекратить сохранение, если валидация не пройдена

        room_number = self.room_number_var.get()
        room_type = self.room_type_var.get()
        room_status = self.room_status_var.get()
        price = self.room_price_var.get()
        description = self.room_description_var.get()
        capacity = self.room_capacity_var.get()
        area = self.room_area_var.get()
        amenities = self.room_amenities_var.get()


        # Вызов функции добавления или обновления комнаты
        if self.is_editing:
            update_room(self.room_id_var.get(), room_number, room_type, room_status, price, description, capacity, area,
                        amenities)
        else:
            add_new_room(room_number, room_type, room_status, price, description, capacity, area, amenities)

        messagebox.showinfo("Успех", "Данные о номере успешно сохранены.")

    def on_room_select(self, event):
        """
        Функция, вызываемая при выборе номера в таблице для редактирования.
        """
        selected_item = self.room_tree.selection()
        if selected_item:
            room_info = self.room_tree.item(selected_item)["values"]
            # Установка данных в поля формы
            self.room_id_var.set(room_info[0])
            self.room_number_var.set(room_info[1])
            self.room_type_var.set(room_info[2])
            self.room_status_var.set(room_info[3])
            self.room_price_var.set(room_info[4])
            self.room_description_var.set(room_info[5])
            self.room_capacity_var.set(room_info[6])
            self.room_area_var.set(room_info[7])
            self.room_amenities_var.set(room_info[8])


            # Устанавливаем флаг, чтобы обозначить, что идет редактирование
            self.is_editing = True

    def clear_form(self):
        """Очистка полей формы и сброс флага редактирования."""
        self.room_number_var.set("")
        self.room_type_var.set("")
        self.room_status_var.set("")
        self.room_price_var.set(0)
        self.room_description_var.set("")
        self.room_capacity_var.set(0)
        self.room_area_var.set(0)
        self.room_amenities_var.set("")


        # Сброс флага редактирования
        self.is_editing = False

    def create_action_buttons_room(self):
        """Кнопки для изменения статуса номеров"""
        button_frame = tk.Frame(self, bg="#e6e6e6")
        button_frame.pack(fill=tk.X, pady=10)

        # Кнопка для изменения статуса номера
        update_status_button = tk.Button(button_frame, text="Изменить статус", command=self.change_room_status,
                                         bg="#c0c0c0")
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

        #print(f"Отладка: Изменение статуса для комнаты {room_info[1]} (ID: {room_id}) на {new_status}")

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
        search_frame = tk.Frame(self, bg="#e6e6e6")
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
        search_button = tk.Button(search_frame, text="Поиск", command=self.search_rooms, bg="#c0c0c0")
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
                                  values=(room[0], room[1], room[2], room[3], f"{room[4]:,.2f} руб", room[5], room[6], room[7], room[8]))

    def create_room_counter(self):
        """Создает счетчик для отображения количества комнат по типам и статусам"""
        self.room_counter_frame = tk.Frame(self, bg="#e6e6e6")
        self.room_counter_frame.pack(fill=tk.X, pady=10)

        # Создаем Label для отображения количества комнат
        self.room_count_label = tk.Label(self.room_counter_frame, text="Количество номеров: 0", bg="#e6e6e6")
        #self.room_count_label.pack(side=tk.LEFT, padx=5)
        self.room_count_label.grid(row=0, column=0, padx=5, sticky="w")

        # Обновляем счетчик при загрузке
        self.update_room_counter()


    def validate_room_data(self):
        """
        Валидация данных о номере перед сохранением.
        """
        try:
            # Проверка вместимости
            capacity = int(self.room_capacity_var.get())
            if capacity <= 0:
                print("Ошибка: Вместимость должна быть положительным числом.")
                return False

            # Проверка площади
            area = float(self.room_area_var.get())
            if area <= 0:
                print("Ошибка: Площадь должна быть положительным числом.")
                return False

            # Проверка удобств
            amenities = self.room_amenities_var.get()
            if not amenities or len(amenities) > 200:
                print("Ошибка: Удобства не должны быть пустыми или превышать 200 символов.")
                return False

            # Проверка примечаний
            notes = self.room_notes_var.get()
            if len(notes) > 500:
                print("Ошибка: Примечания не должны превышать 500 символов.")
                return False

            return True
        except ValueError as ve:
            print(f"Ошибка валидации: {ve}")
            return False