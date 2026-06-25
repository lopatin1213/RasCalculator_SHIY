import logging
import sys
from decimal import Decimal, getcontext
import traceback
from PyQt6.QtWidgets import QInputDialog, QApplication
from sympy import Float, Integer
from PyQt6.uic import loadUi
# from UI import NewApp
history = []
history_of_errors = []

def get_root_degree(window):
    degree, ok_pressed = QInputDialog.getInt(window, "Корень", "Какая степень корня?")
    if ok_pressed:
        window.entry.setText(f"{degree}√")
    else:
        print("Отмена")

# def
def dynamic_precision(value):
    getcontext().prec = 30
    
    if isinstance(value, (int, float)):
        
        decimal_value = Decimal(str(value))
        order = int(decimal_value.adjusted())
        rounded_value = decimal_value.normalize()
        
        precision = max(10, -order + 10)
        logging.info(format(rounded_value, f'.{precision}f').rstrip('0').rstrip('.'))
        return format(rounded_value, f'.{precision}f').rstrip('0').rstrip('.')
    
    elif isinstance(value, complex):
        real_part = dynamic_precision(value.real)
        imag_part = dynamic_precision(value.imag)
        return complex(real_part, imag_part)
    
    elif isinstance(value, str):
        logging.info(f'Это строка {value}')
        return value
    
    elif isinstance(value, list) or isinstance(value, tuple):
        return type(value)(map(dynamic_precision, value))
    elif isinstance(value, Float):
        value = float(value)
        decimal_value = Decimal(str(value))
        order = int(decimal_value.adjusted())
        rounded_value = decimal_value.normalize()
        precision = max(6, -order + 6)
        logging.info(format(rounded_value, f'.{precision}f').rstrip('0').rstrip('.'))
        return format(rounded_value, f'.{precision}f').rstrip('0').rstrip('.')
    elif isinstance(value, Integer):
        value = float(value)
        decimal_value = Decimal(str(value))
        order = int(decimal_value.adjusted())
        rounded_value = decimal_value.normalize()
        precision = max(6, -order + 6)
        logging.info(format(rounded_value, f'.{precision}f').rstrip('0').rstrip('.'))
        return format(rounded_value, f'.{precision}f').rstrip('0').rstrip('.')
    else:
        type_of = type(value)
        logging.info(f'Не определён тип {type_of}')
        return value





def handle_error(error_message, input_data=None, function_name=None):
    """
    Функция для обработки ошибок с дополнительными параметрами.
    :param error_message: Сообщение об ошибке.
    :param input_data: Данные, введенные пользователем.
    :param function_name: Имя функции, в которой произошла ошибка.
    """
    # Вызывает ошибку
    try:
        
        error_box = loadUi("error_box.ui")


        error_box.show()
        # Добавляем дополнительную информацию в сообщение об ошибке
        full_error_message = f"{error_message}"
        if function_name:
            full_error_message += f"\nФункция: {function_name}"
        if input_data:
            full_error_message += f"\nВвод: {input_data}"
        
        # Включаем трассировку стека для получения полной картины ошибки
        stack_trace = traceback.format_exc()
        full_error_message += f"\nТрассировка стека:\n{stack_trace}"
        
        # Специальное сообщение для конкретной ошибки
        if 'деление на ноль' in error_message:
            full_error_message = 'Ошибка: Вы реально поделили на ноль? Вы не знаете правило математики?!'
        if full_error_message != 'Ошибка: Вы реально поделили на ноль? Вы не знаете правило математики?!':
            history_of_errors.append(full_error_message)
            error_box.send_error.clicked.connect(lambda: send_error_click(full_error_message))
        error_box.error_text.setText(full_error_message)
        error_box.exec()
        
        # Добавляем ошибку в историю
    except Exception as e:
        print(str(e))
import requests


def send_error_click(error: str):
    try:
        url = "https://rascalculator.alwaysdata.net/send_errors/"
        version_file = "version.txt"
        with open(version_file, "r") as file:
            installed_version = file.read().strip()

        email, ok = QInputDialog.getText(None, "Ваш E-mail", "Введите E-mail:")
        if ok:
            data = [{
                "error": error,
                "version": installed_version,
                "source": email
            }]
        else:
            data = [{
                "error": error,
                "version": installed_version,
                "source": "Не указан, Приложение"
            }]

        # ШАГ 1: Предварительно получаем CSRF-куки
        session = requests.Session()
        session.get(url)
        csrftoken = session.cookies.get('csrftoken')  # Получаем CSRF-tокен
        print(csrftoken)
        # ШАГ 2: Отправляем POST-запрос с установленным CSRF-токеном
        headers = {
            'Referer': url,  # Устанавливаем Referer
            'X-CSRFToken': csrftoken  # Добавляем CSRF-токен
        }

        response = session.post(url, json=data, headers=headers)
        print(response.status_code)
    except Exception as e:
        print(e)
def add_to_history(expression, result):
    if str(result).startswith("Ошибка:"):
        # Очищаем запись об ошибке
        history.append((expression, str(result).split(":")[0]))
    else:
        # Формируем правильную запись с результатом
        history.append((expression, str(result)))


def update_history():
    # Временное разрешение редактирования
    # history_ui = NewApp()
    
    # print(history_ui)
    # print(history_ui.history_text)
    # history_ui.history_text.clear()# Очищаем текущее содержимое
    for i, (expr, res) in enumerate(history):
        if str(res).startswith("Ошибка:"):
            # history_ui.history_text.insertPlainText(f"{i + 1}. {expr} = {res}\n")
            print(f"{i + 1}. {expr} = {res}\n")
        else:
            # history_ui.history_text.setText(f"{i + 1}. {expr} = {res}\n")
            print(f"{i + 1}. {expr} = {res}\n")


def format_number(num):
    try:
        # Проверяем условие вывода числа в экспоненциальной форме
        num = float(num)
        if (abs(num) >= 1000000000 or abs(num) <= 0.00001) and num != 0:
            # Переводим число в научную нотацию
            scientific_str = "{:.9E}".format(num)
            mantissa, exponent = scientific_str.split("E")
            return "{}*10^{}".format(float(mantissa), int(exponent))
        else:
            # Просто возвращаем само число
            return str(num)
    except Exception as e:
        return num


def clear_errors(window):
    """Очищает поле ошибок."""
    history_ui = HistoryandError()
    history_ui.error_text.clear()


def clear_history():
    """Очищает историю вычислений."""
    history.clear()
    update_history()


if __name__ == '__main__':
    try:
        
        handle_error("Hello")
    except Exception as e:
        print(e)
