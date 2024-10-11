from flask import Blueprint, render_template, request, redirect, url_for, session
from desktop_app.models.database_manager import  insert_user_in_db
import sqlite3
import bcrypt
import datetime
from bcrypt import hashpw, gensalt
from werkzeug.security import generate_password_hash

user_bp = Blueprint('user', __name__)

# Маршрут для регистрации
@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Получаем данные из формы регистрации
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')

        # Хешируем пароль перед сохранением
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # Проверяем, существует ли пользователь с таким email
        user_id = insert_user_in_db(first_name, last_name, email, phone, hashed_password)

        if user_id:
            session['user_id'] = user_id  # Сохраняем идентификатор пользователя в сессии
            session['user_name'] = f"{first_name} {last_name}"
            return redirect(url_for('main.index'))  # Перенаправляем на главную страницу
        else:
            error = "Пользователь с таким email уже существует."
            return render_template('register.html', error=error)

    return render_template('register.html')


# Маршрут для авторизации
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    next_page = request.args.get('next', 'main.index')  # По умолчанию главная страница

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect('F:/Hotel Management System/hotel_management.db') as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, Имя, Фамилия, Пароль FROM Пользователи WHERE email = ?
            """, (email,))
            user = cursor.fetchone()

            # Проверка пароля
            if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
                session['user_id'] = user[0]
                session['user_name'] = f"{user[1]} {user[2]}"

                # Если next_page не указывает на главную, используем его как есть, иначе перенаправляем на главную
                return redirect(next_page if next_page != 'main.index' else url_for('main.index'))

            else:
                error = "Неверный email или пароль"

    heading = "Войти в личный кабинет, чтобы забронировать номер" if next_page == 'booking' else "Войти в личный кабинет"
    return render_template('_auth_form.html', error=error, heading=heading)

@user_bp.route('/logout')
def logout():
    session.clear()  # Очищаем сессию
    return redirect(url_for('main.index'))  # Перенаправляем на главную страницу