from desktop_app.models.database_manager import get_all_clients, update_client_in_db
import sqlite3

DATABASE = 'F:/hotel_management_project/hotel_management.db'
# Функция добавления клиента
def add_new_client(last_name, first_name, middle_name, phone, email):
    """Добавление клиента в базу данных"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Клиенты (Фамилия, Имя, Отчество, Телефон, Email, Дата_регистрации)
            VALUES (?, ?, ?, ?, ?, date('now'))
        """, (last_name, first_name, middle_name, phone, email))
        conn.commit()
        print("Клиент успешно добавлен.")

# Функция удаления клиента
def remove_client(client_id):
    """Удаление клиента из базы данных"""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Проверяем, существует ли клиент с таким ID
        cursor.execute("SELECT id FROM Клиенты WHERE id = ?", (client_id,))
        result = cursor.fetchone()

        if result:
            cursor.execute("DELETE FROM Клиенты WHERE id = ?", (client_id,))
            conn.commit()
            print(f"Клиент с ID {client_id} успешно удален.")
        else:
            print(f"Клиент с ID {client_id} не найден в базе данных.")

def get_clients():
    return get_all_clients()


def update_client(client_id, last_name, first_name, middle_name, phone, email, address=None, notes=None):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Клиенты 
            SET Фамилия = ?, Имя = ?, Отчество = ?, Телефон = ?, Email = ?, Адрес = ?, Примечания = ?
            WHERE id = ?
        """, (last_name, first_name, middle_name, phone, email, address, notes, client_id))
        conn.commit()
        print(f"Клиент с ID {client_id} успешно обновлен.")