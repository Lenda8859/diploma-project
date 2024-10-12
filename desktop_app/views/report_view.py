import tkinter as tk
from tkinter import ttk
import logging
import sqlite3
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from datetime import datetime
from tkcalendar import DateEntry
import pandas as pd
from desktop_app.models.database_manager import get_daily_room_status, DATABASE

class ReportView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Создаем фрейм для элементов меню
        menu_frame = tk.Frame(self)
        menu_frame.pack(pady=10, padx=10)

        # Добавляем Combobox для выбора периода
        tk.Label(menu_frame, text="Выберите тип периода:").pack(side=tk.LEFT, padx=5)
        self.period_type = tk.StringVar()
        # Добавляем опции "По месяцам" и "По годам" в список
        self.period_combo = ttk.Combobox(menu_frame, textvariable=self.period_type,
                                         values=["По дням", "По неделям", "По месяцам", "По годам"])
        self.period_combo.pack(side=tk.LEFT, padx=5)
        self.period_combo.current(0)  # Устанавливаем значение по умолчанию

        # Добавляем виджеты для выбора дат
        tk.Label(menu_frame, text="Выберите начальную дату:").pack(side=tk.LEFT, padx=5)
        self.start_date = DateEntry(menu_frame, date_pattern='dd/mm/yyyy')
        self.start_date.pack(side=tk.LEFT, padx=5)

        tk.Label(menu_frame, text="Выберите конечную дату:").pack(side=tk.LEFT, padx=5)
        self.end_date = DateEntry(menu_frame, date_pattern='dd/mm/yyyy')
        self.end_date.pack(side=tk.LEFT, padx=5)

        # Кнопка для генерации отчета
        self.generate_report_button = tk.Button(menu_frame, text="Сформировать отчет", command=self.generate_report)
        self.generate_report_button.pack(side=tk.LEFT, padx=5)

        # Кнопка для отображения графика
        self.show_graph_button = tk.Button(menu_frame, text="Показать график", command=self.show_graph)
        self.show_graph_button.pack(side=tk.LEFT, padx=5)

        # Кнопка для экспорта в Excel
        self.export_excel_button = tk.Button(menu_frame, text="Экспорт в Excel", command=self.export_to_excel)
        self.export_excel_button.pack(side=tk.LEFT, padx=5)

        # Фрейм для таблицы отчета (Treeview)
        report_frame = tk.Frame(self)
        report_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Создаем Treeview в report_frame
        self.report_tree = ttk.Treeview(report_frame, columns=(
        "Дата/Период", "Свободные", "Занятые", "На обслуживании", "Загрузка (%)"), show='headings')
        self.report_tree.pack(fill=tk.BOTH, expand=True)

        # Определение заголовков столбцов
        self.report_tree.heading("Дата/Период", text="Дата/Период")
        self.report_tree.heading("Свободные", text="Свободные")
        self.report_tree.heading("Занятые", text="Занятые")
        self.report_tree.heading("На обслуживании", text="На обслуживании")
        self.report_tree.heading("Загрузка (%)", text="Загрузка (%)")

        # Определение ширины столбцов
        self.report_tree.column("Дата/Период", width=100)
        self.report_tree.column("Свободные", width=100)
        self.report_tree.column("Занятые", width=100)
        self.report_tree.column("На обслуживании", width=150)
        self.report_tree.column("Загрузка (%)", width=100)

    def generate_report(self):
        """Генерация отчета по загрузке номеров"""
        period_type = self.period_type.get()
        start_date = self.start_date.get_date().strftime('%Y-%m-%d')
        end_date = self.end_date.get_date().strftime('%Y-%m-%d')

        # Логика для сбора и обработки данных в зависимости от периода
        if period_type == "По дням":
            self.generate_daily_report(start_date, end_date)
        elif period_type == "По неделям":
            self.generate_weekly_report(start_date, end_date)
        elif period_type == "По месяцам":
            self.generate_monthly_report(start_date, end_date)
        elif period_type == "По годам":
            self.generate_yearly_report(start_date, end_date)

    def generate_daily_report(self, start_date, end_date):
        """Генерация отчета по дням"""
        try:
            data = get_daily_room_status(start_date, end_date)

            # Очистка таблицы перед заполнением
            for row in self.report_tree.get_children():
                self.report_tree.delete(row)

            for row in data:
                # Распаковываем данные
                date_str, свободные, занятые, на_обслуживании, загрузка_str = row

                # Преобразуем date_str в объект datetime
                date = datetime.strptime(date_str, '%Y-%m-%d')
                # Форматируем дату в 'ДД.ММ.ГГ'
                formatted_date = date.strftime('%d.%m.%y')

                # Преобразуем загрузка в float (убираем символ '%', если есть)
                загрузка = float(загрузка_str.replace('%', ''))

                total_rooms = свободные + занятые + на_обслуживании

                # Добавляем тег для цветного форматирования строки
                tag = ''
                if загрузка < 30:
                    tag = 'low_load'
                elif загрузка < 70:
                    tag = 'medium_load'
                else:
                    tag = 'high_load'

                # Заполнение Treeview строками по дням
                self.report_tree.insert("", "end",
                                        values=(
                                        formatted_date, свободные, занятые, на_обслуживании, f"{загрузка:.2f}%"),
                                        tags=(tag,))

            # Определяем цвет для каждого тега
            self.report_tree.tag_configure('low_load', background='grey')
            self.report_tree.tag_configure('medium_load', background='yellow')
            self.report_tree.tag_configure('high_load', background='red')

        except Exception as e:
            logging.error(f"Ошибка при генерации отчета по дням: {e}")

    def generate_weekly_report(self, start_date, end_date):
        """Генерация отчета по неделям"""
        try:
            # Получаем данные по неделям из базы данных
            data = self.get_weekly_room_status(start_date, end_date)

            # Очистка Treeview перед заполнением новыми данными
            for row in self.report_tree.get_children():
                self.report_tree.delete(row)

            for row in data:
                # Получаем данные строки
                week_start_str, week_end_str, свободные, занятые, на_обслуживании, загрузка = row

                # Преобразуем week_start и week_end в объекты datetime
                week_start = datetime.strptime(week_start_str, '%Y-%m-%d')
                week_end = datetime.strptime(week_end_str, '%Y-%m-%d')

                total_rooms = свободные + занятые + на_обслуживании

                # Добавляем тег для цветного форматирования строки
                tag = ''
                if загрузка < 30:
                    tag = 'low_load'
                elif загрузка < 70:
                    tag = 'medium_load'
                else:
                    tag = 'high_load'

                # Заполнение Treeview строками по неделям
                self.report_tree.insert("", "end",
                                        values=(f"{week_start.strftime('%d.%m.%y')} - {week_end.strftime('%d.%m.%y')}",
                                                свободные, занятые, на_обслуживании, f"{загрузка:.2f}%"),
                                        tags=(tag,))

            # Определяем цвет для каждого тега
            self.report_tree.tag_configure('low_load', background='#d3d3d3')
            self.report_tree.tag_configure('medium_load', background='yellow')
            self.report_tree.tag_configure('high_load', background='red')

            print(f"Генерация отчета по неделям с {start_date} по {end_date}")

        except Exception as e:
            logging.error(f"Ошибка при генерации отчета по неделям: {e}")

    def get_monthly_room_status(self, start_date, end_date):
        """Получение данных о статусах номеров за указанный период по месяцам"""
        with sqlite3.connect(DATABASE, timeout=10) as conn:
            cursor = conn.cursor()

            # Выполняем запрос для группировки данных по месяцам
            cursor.execute("""
                SELECT
                    strftime('%Y-%m', Дата_заезда) AS month,
                    MIN(date(Дата_заезда)) AS month_start,
                    SUM(CASE WHEN Статус_бронирования IN ('Заезд', 'Подтверждено') THEN 1 ELSE 0 END) AS занятые,
                    SUM(CASE WHEN Статус_бронирования = 'Выезд' THEN 1 ELSE 0 END) AS на_обслуживании
                FROM Бронирования
                WHERE date(Дата_заезда) BETWEEN ? AND ?
                GROUP BY month
            """, (start_date, end_date))

            result = cursor.fetchall()

            report_data = []
            total_rooms = self.get_total_room_count()  # Получить общее количество комнат в отеле

            for row in result:
                month_start = row[1]  # Дата начала месяца
                occupied = row[2]
                service = row[3]
                свободные = total_rooms - occupied - service
                загрузка = (occupied / total_rooms) * 100 if total_rooms > 0 else 0

                # Добавляем только начало месяца в report_data
                report_data.append((month_start, свободные, occupied, service, загрузка))

            return report_data

    def generate_monthly_report(self, start_date, end_date):
        """Генерация отчета по месяцам"""
        try:
            # Получаем данные по месяцам из базы данных
            data = self.get_monthly_room_status(start_date, end_date)

            # Очистка Treeview перед заполнением новыми данными
            for row in self.report_tree.get_children():
                self.report_tree.delete(row)

            for row in data:
                # Распаковываем строку из 5 значений
                month_start_str, свободные, занятые, на_обслуживании, загрузка = row

                # Преобразуем строку даты в объект datetime
                month_start = datetime.strptime(month_start_str, '%Y-%m-%d')

                # Заполнение Treeview строками по месяцам
                self.report_tree.insert("", "end",
                                        values=(month_start.strftime('%d.%m.%y'),
                                                свободные, занятые, на_обслуживании, f"{загрузка:.2f}%"))

            print(f"Генерация отчета по месяцам с {start_date} по {end_date}")

        except Exception as e:
            logging.error(f"Ошибка при генерации отчета по месяцам: {e}")

    def get_yearly_room_status(self, start_date, end_date):
        """Получение данных о статусах номеров за указанный период по годам"""
        with sqlite3.connect(DATABASE, timeout=10) as conn:
            cursor = conn.cursor()

            # Выполняем запрос для группировки данных по годам
            cursor.execute("""
                SELECT
                    strftime('%Y', Дата_заезда) AS year,
                    MIN(date(Дата_заезда)) AS year_start,
                    SUM(CASE WHEN Статус_бронирования IN ('Заезд', 'Подтверждено') THEN 1 ELSE 0 END) AS занятые,
                    SUM(CASE WHEN Статус_бронирования = 'Выезд' THEN 1 ELSE 0 END) AS на_обслуживании
                FROM Бронирования
                WHERE date(Дата_заезда) BETWEEN ? AND ?
                GROUP BY year
            """, (start_date, end_date))

            result = cursor.fetchall()

            report_data = []
            total_rooms = self.get_total_room_count()  # Получить общее количество комнат в отеле

            for row in result:
                year_start = row[1]  # Дата начала года
                occupied = row[2]
                service = row[3]
                свободные = total_rooms - occupied - service
                загрузка = (occupied / total_rooms) * 100 if total_rooms > 0 else 0

                # Добавляем только начало года в report_data
                report_data.append((year_start, свободные, occupied, service, загрузка))

            return report_data

    def generate_yearly_report(self, start_date, end_date):
        """Генерация отчета по годам"""
        try:
            # Получаем данные по годам из базы данных
            data = self.get_yearly_room_status(start_date, end_date)

            # Очистка Treeview перед заполнением новыми данными
            for row in self.report_tree.get_children():
                self.report_tree.delete(row)

            for row in data:
                # Распаковываем строку из 5 значений
                year_start_str, свободные, занятые, на_обслуживании, загрузка = row

                # Преобразуем строку даты в объект datetime
                year_start = datetime.strptime(year_start_str, '%Y-%m-%d')

                # Заполнение Treeview строками по годам
                self.report_tree.insert("", "end",
                                        values=(year_start.strftime('%d.%m.%y'),
                                                свободные, занятые, на_обслуживании, f"{загрузка:.2f}%"))

            print(f"Генерация отчета по годам с {start_date} по {end_date}")

        except Exception as e:
            logging.error(f"Ошибка при генерации отчета по годам: {e}")

    def get_total_room_count(self):
        """Возвращает общее количество номеров в отеле"""
        with sqlite3.connect(DATABASE, timeout=10) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Номера")
            total_rooms = cursor.fetchone()[0]
            return total_rooms

    def get_weekly_room_status(self, start_date, end_date):
        """Получение данных о статусах номеров за указанный период по неделям"""
        with sqlite3.connect(DATABASE, timeout=10) as conn:
            cursor = conn.cursor()

            # Выполняем запрос для группировки данных по неделям
            cursor.execute("""
                SELECT
                    strftime('%Y-%W', Дата_заезда) AS week_number,
                    MIN(date(Дата_заезда)) AS week_start,
                    MAX(date(Дата_заезда)) AS week_end,
                    SUM(CASE WHEN Статус_бронирования IN ('Заезд', 'Подтверждено') THEN 1 ELSE 0 END) AS занятые,
                    SUM(CASE WHEN Статус_бронирования = 'Выезд' THEN 1 ELSE 0 END) AS на_обслуживании
                FROM Бронирования
                WHERE date(Дата_заезда) BETWEEN ? AND ?
                GROUP BY week_number
            """, (start_date, end_date))

            result = cursor.fetchall()

            report_data = []
            total_rooms = self.get_total_room_count()  # Получить общее количество комнат в отеле

            for row in result:
                week_start, week_end, occupied, service = row[1], row[2], row[3], row[4]
                свободные = total_rooms - occupied - service
                загрузка = (occupied / total_rooms) * 100 if total_rooms > 0 else 0

                report_data.append((week_start, week_end, свободные, occupied, service, загрузка))

            return report_data

    def export_to_excel(self):
        """Экспорт данных отчета в Excel"""
        try:

            #print("Экспорт данных в Excel...")  # Для отладки

            # Собираем данные из Treeview
            data = []
            columns = ["Дата/Период", "Свободные", "Занятые", "На обслуживании", "Загрузка (%)"]

            for row in self.report_tree.get_children():
                values = self.report_tree.item(row)['values']
                data.append(values)

            # Создаем DataFrame
            df = pd.DataFrame(data, columns=columns)

            # Получаем текущую дату в формате ДД.ММ.ГГ
            current_date = datetime.now().strftime('%d.%m.%y')

            # Указываем путь для сохранения файла на русском с датой
            file_path = f'F:/Hotel Management System/Отчеты/отчет от {current_date}.xlsx'
            df.to_excel(file_path, index=False)

            print(f"Данные успешно экспортированы в файл: {file_path}")
        except Exception as e:
            print(f"Ошибка при экспорте отчета в Excel: {e}")

    def show_graph(self):
        """Построение графика загрузки номеров"""
        try:
            logging.info("Начало построения графика загрузки номеров.")

            # Собираем данные из Treeview
            dates = []
            occupied_rooms = []

            for row in self.report_tree.get_children():
                values = self.report_tree.item(row)['values']
                # Для отчетов по месяцам и годам используем только начало периода
                date_str = values[0].split(' - ')[0].strip()
                date = datetime.strptime(date_str, '%d.%m.%y')
                occupied = int(values[2])  # Количество занятых номеров
                dates.append(date)
                occupied_rooms.append(occupied)

            plt.figure(figsize=(10, 5))

            # Добавление линии и точек с мягкими цветами
            plt.plot(dates, occupied_rooms, marker='o', color='#6c757d', linestyle='-', linewidth=2)  # Серый оттенок
            plt.fill_between(dates, occupied_rooms, color='#d3d3d3',
                             alpha=0.2)  # Светло-серый оттенок для области под линией
            plt.xlabel('Дата')
            plt.ylabel('Количество занятых номеров')
            plt.title('Загрузка номеров по датам')
            plt.xticks(rotation=45)

            # Форматирование оси x для отображения дат в формате ДД.ММ.ГГ
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y'))

            # Определяем интервал для отметок на оси X в зависимости от типа периода
            period_type = self.period_type.get()

            if period_type == "По дням":
                locator = mdates.DayLocator(interval=1)
            elif period_type == "По неделям":
                locator = mdates.WeekdayLocator(interval=1)
            elif period_type == "По месяцам":
                locator = mdates.MonthLocator(interval=1)
            elif period_type == "По годам":
                locator = mdates.YearLocator()

            plt.gca().xaxis.set_major_locator(locator)

            # Ограничиваем максимальное количество отметок на оси X
            plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(nbins=8))

            plt.tight_layout()
            plt.show()

        except Exception as e:
            logging.error(f"Ошибка при построении графика: {e}")