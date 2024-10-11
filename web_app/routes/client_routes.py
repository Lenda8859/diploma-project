from flask import Blueprint, request


client_bp = Blueprint('client', __name__)

@client_bp.route('/create_client', methods=['POST'])
def create_client_route():
    # Получение данных клиента из запроса
    name = request.form['name']
    email = request.form['email']
    create_client(name, email)
    return 'Клиент успешно создан!'