// Получаем элементы модального окна и кнопок
var modal = document.getElementById("authModal");
var btn = document.getElementById("openModal");
var closeBtn = document.getElementsByClassName("close")[0];

// Переключение между вкладками
var loginTab = document.getElementById('login-tab');
var registerTab = document.getElementById('register-tab');
var loginForm = document.getElementById('login-form');
var registerForm = document.getElementById('register-form');

// Открытие модального окна по клику на кнопку
btn.onclick = function() {
    modal.style.display = "flex";
}

// Закрытие модального окна по клику на кнопку закрытия (X)
closeBtn.onclick = function() {
    modal.style.display = "none";
}

// Закрытие модального окна по клику вне его области
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// Переключение на вкладку "Войти"
loginTab.onclick = function() {
    loginForm.classList.remove('hidden');
    registerForm.classList.add('hidden');
    loginTab.classList.add('active');
    registerTab.classList.remove('active');
}

// Переключение на вкладку "Зарегистрироваться"
registerTab.onclick = function() {
    registerForm.classList.remove('hidden');
    loginForm.classList.add('hidden');
    registerTab.classList.add('active');
    loginTab.classList.remove('active');
}