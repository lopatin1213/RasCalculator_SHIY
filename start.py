from PyQt6.QtWidgets import QMessageBox
import configparser
import logging
import requests
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename='logs.log')

def is_first_run(preferences_file="preferences.txt"):
    """Проверяет, является ли запуск приложения первым."""
    try:
        with open(preferences_file, "r") as file:
            content = file.read().strip()
            is_first = content == "True"
            logging.info(f"Файл '{preferences_file}' прочитан: {content}, интерпретировано как: {is_first}")
            return is_first
    except FileNotFoundError:
        logging.info(f"Файл '{preferences_file}' не найден.  Предполагается первый запуск.")
        return True
    except PermissionError:
        logging.error(f"Ошибка: не удается прочитать файл '{preferences_file}'. Проверьте права доступа.")
        return False
    except Exception as e:
        logging.error(f"Неожиданная ошибка при работе с файлом '{preferences_file}': {e}")
        return False


def handle_first_run(preferences_file="preferences.txt"):
    """Выполняет действия, необходимые при первом запуске."""
    show_tutorial()  # Отображение приветственного сообщения
    
     # Выбор цвета фона
    
    try:
        with open(preferences_file, "w") as file:
            file.write("False")
            logging.info(f"Файл '{preferences_file}' обновлён.")
    except PermissionError:
        logging.error(f"Ошибка: не удаётся записать в файл '{preferences_file}'. Проверьте права доступа.")
    except Exception as e:
        logging.error(f"Неожиданная ошибка при записи в файл '{preferences_file}': {e}")


def check_first_run_and_show_tutorial( preferences_file="preferences.txt"):
    """Проверяет, является ли запуск приложения первым, и выполняет соответствующие действия."""
    check_version()
    if is_first_run(preferences_file):
        handle_first_run(preferences_file)
    else:
        logging.info("Это не первый запуск.")
        


def show_tutorial(title="Добро пожаловать!", message=None):
    """Отображает обучающее сообщение пользователю."""
    if message is None:
        message = (
            "Добро пожаловать в расширенный калькулятор!\n\n"
            "Здесь вы можете решать уравнения, считать среднее арифметическое,\n"
            "медиану, минимальное и максимальное значение, и многое другое."
        )
        QMessageBox.information(None,
                         'Лицензионное соглашение',
        """
Программа "Рас. Калькулятор" распространяется бесплатно и предоставляется "как есть".
Пользователь соглашается не распространять данное программное обеспечение третьим лицам без письменного разрешения разработчика.
Если же хотите опубликовать программу где-то во-первых напишите мне чтобы я знал что вы хотите где-то опубликовать приложение
Использование программы осуществляется исключительно на риск пользователя.
Разработчики не несут ответственности за любые убытки, вызванные неправильным использованием данной программы.
Сайт разработчика: https://ras-calc-site.onrender.com
Продолжая работу с программой, вы принимаете вышеуказанное лицензионное соглашение.

        """,
        
QMessageBox.StandardButton.Ok)
    try:
        QMessageBox.information(None, title, message)
        
        logging.info("Обучающее сообщение отображено.")
    except Exception as e:
        logging.error(f"Ошибка при отображении обучающего сообщения: {e}")


import os
import webbrowser



# Настройка логирования


def has_internet_connection():
    """
    Проверяет наличие соединения с интернетом.
    """
    try:
        # Пробуем соединиться с внешним сервисом
        response = requests.head("https://www.google.com/", timeout=5)
        return response.status_code == 200
    except requests.ConnectionError:
        
        return False


def check_version():
    version_file = "version.txt"
    server_url = "https://rascalculator.alwaysdata.net/version_check/"
    curent_vers_file = "cur_version.txt"
    if not has_internet_connection():
        QMessageBox.warning(None,
            "Проблемы с интернетом",
            "Хитро придумали, отключить интернет...\n\n"
            "Но избежать проверки версии не получится",
            QMessageBox.StandardButton.Ok
        )
        with open(curent_vers_file, 'r') as f2:
            current_version = f2.read().strip()
        if not os.path.exists(version_file):
            logging.warning(f"Файл '{version_file}' не найден. Предположительно первая установка.")
            installed_version = "0.0.0.0"
        else:
            with open(version_file, "r") as file:
                installed_version = file.read().strip()
        installed_version_tuple = tuple(map(int, installed_version.split('.')))
        print(current_version)
        current_version_tuple = tuple(map(int, current_version.split('.')))
        
        if installed_version_tuple >= current_version_tuple:
            QMessageBox.information(None,
                "Все ок",
                """
Ладно живи у тебя актуальная версия :)
И больше не отключай интернет :|
                """
            )
        else:
            logging.info(f"Обнаружена новая версия: {current_version}. Текущая версия: {installed_version}.")
            
            # Диалоговое окно с выбором
            QMessageBox.warning(None,
                                "Старая версия",
                                f"Обнаружена новая версия: {current_version}. Текущая версия: {installed_version}. Пожалуйста после появления интернета скачайте",
                                QMessageBox.StandartButton.Ok)
    try:
        response = requests.get(server_url)
        print(response)
        response.raise_for_status()
        current_version = response.text.strip()
        print(current_version)
        with open(curent_vers_file, 'w') as f1:
            f1.write(current_version)
        if not os.path.exists(version_file):
            logging.warning(f"Файл '{version_file}' не найден. Предположительно первая установка.")
            installed_version = "7.0.0.0"
        else:
            with open(version_file, "r") as file:
                installed_version = file.read().strip()
        
        installed_version_tuple = tuple(map(int, installed_version.split('.')))
        current_version_tuple = tuple(map(int, current_version.split('.')))
        
        if installed_version_tuple < current_version_tuple:
            logging.info(f"Обнаружена новая версия: {current_version}. Текущая версия: {installed_version}.")
            
            # Диалоговое окно с выбором
            response = QMessageBox.question(None,
                                            'Выбор',
                                            f"Ваша версия {installed_version} устарела. Актуальная: {current_version}\n"
                f"Рекомендуется установить последнюю версию с официального сайта Расширенного Калькулятора:\n"
                f"https://rascalculator.alwaysdata.net/download\n\n"
                f"Эту страницу подтверждаю я как единственное официальное место для скачивания нашего калькулятора.\n\n"
                f"Желаете перейти на страницу загрузки?",                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if response == QMessageBox.StandardButton.Yes:
                # Открываем ссылку на скачивание
                webbrowser.open_new_tab("https://rascalculator.alwaysdata.net/download")
        else:
            logging.info("У вас установлена актуальная версия.")
    except requests.RequestException as req_err:
        logging.error(f"Ошибка при получении данных с сервера: {req_err}")
    except ValueError as val_err:
        logging.error(f"Ошибка формата версии: {val_err}")
    except OSError as os_err:
        logging.error(f"Ошибка чтения файла: {os_err}")
    except Exception as exc:
        logging.error(f"Необработанная ошибка: {exc}")











