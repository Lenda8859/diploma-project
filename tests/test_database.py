import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Абсолютный путь к корню проекта "Hotel Management System"
project_root = r'F:\Hotel Management System'

# Добавление пути к `sys.path`
sys.path.append(project_root)
from desktop_app.views.room_view import RoomView
import sqlite3

# Use an in-memory database for testing
TEST_DATABASE = 'F:\Hotel Management System/hotel_management.db'
# Добавляем путь к корню проекта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from desktop_app.models.database_manager import (
    create_tables, add_room, update_room
)


class TestRoomValidation(unittest.TestCase):

    def setUp(self):
        # Создаем фрейм для RoomView
        self.room_view = RoomView(MagicMock())

        # Инициализируем поля с корректными значениями
        self.room_view.room_capacity_var.set("2")  # Вместимость
        self.room_view.room_area_var.set("30.5")  # Площадь
        self.room_view.room_amenities_var.set("Wi-Fi, Кондиционер")  # Удобства
        self.room_view.room_notes_var.set("Стандартный номер")  # Примечания

    def test_validate_capacity(self):
        # Проверка валидности вместимости
        self.room_view.room_capacity_var.set("2")
        self.assertTrue(self.room_view.validate_room_data())

        self.room_view.room_capacity_var.set("-5")
        self.assertFalse(self.room_view.validate_room_data())

        self.room_view.room_capacity_var.set("abc")  # Invalid non-integer input
        self.assertFalse(self.room_view.validate_room_data())

    def test_validate_area(self):
        # Проверка валидности площади
        self.room_view.room_area_var.set("30.5")
        self.assertTrue(self.room_view.validate_room_data())

        self.room_view.room_area_var.set("0")  # Zero area
        self.assertFalse(self.room_view.validate_room_data())

        self.room_view.room_area_var.set("abc")  # Invalid non-float input
        self.assertFalse(self.room_view.validate_room_data())

    def test_validate_amenities(self):
        # Проверка валидности удобств
        self.room_view.room_amenities_var.set("Wi-Fi, Air Conditioning")
        self.assertTrue(self.room_view.validate_room_data())

        self.room_view.room_amenities_var.set("")  # Пустое значение
        self.assertFalse(self.room_view.validate_room_data())

        # Проверка длины удобств (больше 200 символов)
        self.room_view.room_amenities_var.set("a" * 201)
        self.assertFalse(self.room_view.validate_room_data())

    def test_validate_notes(self):
        # Проверка валидности примечаний
        self.room_view.room_notes_var.set("Дополнительная информация о комнате.")
        self.assertTrue(self.room_view.validate_room_data())

        # Примечания превышают лимит в 500 символов
        self.room_view.room_notes_var.set("a" * 501)
        self.assertFalse(self.room_view.validate_room_data())

        # Граничный случай: ровно 500 символов
        self.room_view.room_notes_var.set("a" * 500)
        self.assertTrue(self.room_view.validate_room_data())


class TestRoomSave(unittest.TestCase):


    @patch('desktop_app.models.database_manager.add_room')
    @patch('desktop_app.models.database_manager.update_room')
    def test_save_room_data(self, mock_update_room, mock_add_new_room):
        # Проверка сохранения данных о номере (новая комната)
        self.room_view.is_editing = False
        self.room_view.room_number_var.set("101")
        self.room_view.room_type_var.set("Стандарт")
        self.room_view.room_status_var.set("свободно")
        self.room_view.room_price_var.set("3000")
        self.room_view.room_description_var.set("Описание комнаты")
        self.room_view.room_capacity_var.set("2")
        self.room_view.room_area_var.set("30.5")
        self.room_view.room_amenities_var.set("Wi-Fi, Телевизор")
        self.room_view.room_notes_var.set("Нет примечаний")

        self.room_view.save_room_data()
        mock_add_new_room.assert_called_once_with(
            "101", "Стандарт", "свободно", "3000", "Описание комнаты", "2", "30.5", "Wi-Fi, Телевизор", "Нет примечаний"
        )

        # Проверка сохранения данных о номере (редактирование существующей комнаты)
        self.room_view.is_editing = True
        self.room_view.room_id_var.set("1")
        self.room_view.save_room_data()
        mock_update_room.assert_called_once_with(
            "1", "101", "Стандарт", "свободно", "3000", "Описание комнаты", "2", "30.5", "Wi-Fi, Телевизор", "Нет примечаний"
        )



    def tearDown(self):
        # Any necessary cleanup after tests
        pass


class TestDatabaseOperations(unittest.TestCase):

    def setUp(self):
        # Connect to an in-memory database
        self.conn = sqlite3.connect(TEST_DATABASE)
        self.cursor = self.conn.cursor()
        create_tables()  # Assuming this will create necessary tables in memory

    def tearDown(self):
        # Close the connection to the in-memory database
        self.conn.close()

    def test_add_room(self):
        # Example test for adding a room
        add_room("102", "Делюкс", "свободно", 4500, "Делюкс комната", 4, 40.0, "Wi-Fi, Балкон", "Просторная комната")
        self.cursor.execute("SELECT * FROM Номера WHERE Номер_комнаты = '102'")
        room = self.cursor.fetchone()
        self.assertIsNotNone(room)
        self.assertEqual(room[1], "102")
        self.assertEqual(room[2], "Делюкс")

    def test_update_room(self):
        # Example test for updating a room
        add_room("103", "Стандарт", "свободно", 3000, "Стандартная комната", 2, 25.0, "Wi-Fi", "")
        update_room(1, "103", "Сьют", "занято", 3500, "Сьют комната", 3, 35.0, "Wi-Fi, Джакузи", "Просторный люкс")
        self.cursor.execute("SELECT * FROM Номера WHERE Номер_комнаты = '103'")
        room = self.cursor.fetchone()
        self.assertIsNotNone(room)
        self.assertEqual(room[2], "Сьют")
        self.assertEqual(room[3], "занято")

if __name__ == "__main__":
    unittest.main()
