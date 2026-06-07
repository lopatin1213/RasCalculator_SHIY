import addings
from schislen import *
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox, QMessageBox, \
    QTabWidget, QVBoxLayout, QGridLayout, QHBoxLayout
import sys
from PyQt6.QtGui import QIcon, QTextCursor, QFont
from PyQt6.QtCore import QSize, Qt
from calculate import *
from equations import *
from statistic import *
from addings import *
import logging
import sys
import traceback
import logging
import uuid
from datetime import datetime
import requests
# Твои конфиденциальные данные для Telegram
TELEGRAM_TOKEN = "8835634431:AAGqw3kmILT5ioxGVlRw0BlAjWM2iRycAFU"
TELEGRAM_CHAT_ID = "5707914157"  # личный или группы с минусом
import sys
import traceback
import logging
import uuid
from datetime import datetime
import requests


def send_critical_error_to_site(error_code: str, error_text: str):
    """Отправляет критическую ошибку на сайт (во Францию), минуя блокировки."""
    try:
        url = "https://rascalculator.alwaysdata.net/send_errors/"
        version_file = "version.txt"
        with open(version_file, "r") as file:
            installed_version = file.read().strip()

        data = [{
            "error": f"КРИТИЧЕСКАЯ [{error_code}]:\n{error_text}",
            "version": installed_version,
            "source": "Приложение (глобальный перехватчик)"
        }]

        # Твоя стандартная процедура с CSRF
        session = requests.Session()
        session.get(url)
        csrftoken = session.cookies.get('csrftoken')
        headers = {
            'Referer': url,
            'X-CSRFToken': csrftoken
        }
        # Отправка с таймаутом, чтобы не вешать приложение
        session.post(url, json=data, headers=headers, timeout=5)
    except Exception:
        # Если даже это не сработало (нет интернета) — просто идём дальше
        pass


def global_exception_handler(exc_type, exc_value, exc_traceback):
    """
    Глобальный обработчик всех необработанных исключений.
    Это последний рубеж обороны, который не даёт приложению упасть молча.
    """
    try:
        # 1. Формируем читаемый текст ошибки
        error_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        error_text = "".join(error_lines)

        # 2. Генерируем уникальный код ошибки
        error_code = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 3. Пишем в твой основной лог-файл
        logging.critical(f"НЕОБРАБОТАННАЯ ОШИБКА [{error_code}]:\n{error_text}")

        # 4. Сохраняем в историю ошибок (чтобы отправить при выходе из приложения)
        full_error = (
            f"КРИТИЧЕСКАЯ ОШИБКА [{error_code}] ({timestamp})\n"
            f"{error_text}"
        )


        # 5. Пытаемся показать диалог пользователю
        try:
            from PyQt6.QtWidgets import QMessageBox
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("Критическая ошибка")
            msg_box.setText(
                "Произошла непредвиденная ошибка.\n\n"
                f"Код ошибки: {error_code}\n\n"
                "Пожалуйста, отправьте этот код разработчику.\n"
                "Приложение будет завершено."
            )
            msg_box.setDetailedText(error_text)
            msg_box.exec()

        except Exception:
            pass

        # 6. Отправляем ошибку на сайт (а он уже перешлёт в Telegram)
        send_critical_error_to_site(error_code, error_text)
        try:
            # Пытаемся закрыть приложение "по-хорошему"
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                app.quit()
        except Exception:
            pass
        finally:
            # Если не вышло, завершаем принудительно
            sys.exit(1)
    except Exception:
        # Если ошибка в самом обработчике — просто выводим в консоль
        print("КРИТИЧЕСКАЯ ОШИБКА В ОБРАБОТЧИКЕ ОШИБОК!", file=sys.stderr)
        traceback.print_exc()


# Устанавливаем глобальный перехватчик ДО создания QApplication


class SistemSchileniy(QWidget):
    def __init__(self):
        super().__init__()
        label_sch_text = QLabel(parent=self, text="Арифметика систем счислений:")
        label_sch_text.move(0, 0)

        self.entry_first_num = QLineEdit(self)
        self.entry_first_num.move(0, 25)

        self.entry_second_num = QLineEdit(self)
        self.entry_second_num.move(165, 25)

        self.operator_variabl = QComboBox(self)
        self.operator_variabl.addItems(["+", "-", "*", "/"])
        self.operator_variabl.move(135, 25)

        self.button_sch_calculate = QPushButton(parent=self, text="Выполнить операцию")
        self.button_sch_calculate.move(0, 50)

        self.label_sch_result = QLineEdit(self)
        self.label_sch_result.setReadOnly(True)
        self.label_sch_result.move(0, 80)
        self.label_sch_result.resize(300, 20)
        self.ss = QLineEdit(self)

        self.box = QGridLayout(self)
        self.lbl = QLabel("с.с", self)
        
        self.box.addWidget(self.entry_first_num, 1, 0)

        self.box.addWidget(self.entry_second_num, 1, 2)
        self.box.addWidget(label_sch_text, 0, 0, 1, 4)
        self.box.addWidget(self.button_sch_calculate, 3, 0, 1, 4)
        self.box.addWidget(self.operator_variabl, 1, 1)
        self.box.addWidget(self.label_sch_result, 4, 0, 1, 4)
        self.box.addWidget(self.ss, 2, 3)
        self.box.addWidget(self.lbl, 2, 4)
        self.button_sch_calculate.clicked.connect(lambda: self.on_click())
        self.entry_first_num.returnPressed.connect(lambda: self.on_click())
        self.entry_second_num.returnPressed.connect(lambda: self.on_click())
        self.ss.returnPressed.connect(lambda: self.on_click())

    def on_click(self):
        calculate_sch(self, self.operator_variabl.currentText(), self.ss.text())

class SistemSchileniyPerevod(QWidget):
    def __init__(self):
        super().__init__()
        label_sch_text = QLabel(parent=self, text="Перевод и одной системы счисления в другую")
        label_sch_text.move(0, 0)

        self.entry_first_num = QLineEdit(self)
        self.entry_first_num.move(0, 25)

        self.ss_1 = QLineEdit(self)        

        self.button_sch_calculate = QPushButton(parent=self, text="Выполнить операцию")
        self.button_sch_calculate.move(0, 50)

        self.label_sch_result = QLineEdit(self)
        self.label_sch_result.move(0, 80)
        self.label_sch_result.resize(300, 20)
        self.ss_2 = QLineEdit(self)
        self.label_sch_result.setReadOnly(True)
        self.box = QGridLayout(self)
        self.lbl = QLabel("с.с", self)
        self.operator_variabl = QLabel(self)
        self.box.addWidget(label_sch_text, 0, 0, 1, 4)
        self.box.addWidget(self.entry_first_num, 1, 0)
        self.box.addWidget(self.ss_1, 2, 1)
        self.box.addWidget(self.operator_variabl, 2, 2)
        self.box.addWidget(self.ss_2, 2, 3)
        self.box.addWidget(self.lbl, 2, 4)
        self.box.addWidget(self.button_sch_calculate, 3, 0, 1, 4)
        self.box.addWidget(self.label_sch_result, 4, 0, 1, 4)
        self.button_sch_calculate.clicked.connect(lambda: self.on_click())
        self.entry_first_num.returnPressed.connect(lambda: self.on_click())
        self.ss_1.returnPressed.connect(lambda: self.on_click())
        self.ss_2.returnPressed.connect(lambda: self.on_click())
    def on_click(self):
        perevod_to(self, self.ss_1.text(), self.ss_2.text())
class Calculator(QWidget):

    def __init__(self):
        super().__init__()
        self.box = QVBoxLayout(self)
        label_basic_calc_text = QLabel(self)
        label_basic_calc_text.setText("Введите числовое выражение (2+2):")
        label_basic_calc_text.move(0, 0)

        self.entry = QLineEdit()
        self.entry.move(0, 20)

        self.button_calc = QPushButton()

        self.button_calc.setText("Вычислить")
        self.button_calc.move(216, 15)
        self.button = QPushButton("Функции")

        self.label = QLineEdit(self)
        self.label.move(0, 40)
        self.label.resize(1000, 16)
        self.label.setReadOnly(True)
        self.button_cor = QPushButton(text='√')
        self.button_cor.move(296, 15)
        self.box.addWidget(label_basic_calc_text)
        self.box.addWidget(self.entry)
        
        self.box.addWidget(self.button_calc)
        
        self.box.addWidget(self.button_cor)
        self.box.addWidget(self.button_calc)
        
        self.box.addWidget(self.label)
        self.box.addWidget(self.button)
        logging.info(self.button_calc)
        self.entry.returnPressed.connect(lambda: self.on_click())
        self.button_calc.clicked.connect(lambda: self.on_click())
        self.button.clicked.connect(lambda: self.functions())
        self.button_cor.clicked.connect(lambda: get_root_degree(self))
    def on_click(self):
        calculate(self)
    def functions(self):
        func = Functionsympy(self)
        func.show()
        
import sympy

class Functionsympy(QWidget):
    def __init__(self, window):
        try:
            super().__init__()
            self.setWindowTitle("Функции")
            box = QGridLayout(self)
            x = 0
            y = 0
            list_f = ['pi','sqrt', 'exp', 'ln', 'log', 'sin', 'cos', 'tan', 'asin', 'acos', 'atan',
            'rad', 'deg', 'sinh', 'cosh', 'tanh',
                      'Si', 'Ci', 'Ei', ]
            for func in list_f:
                
                button = QPushButton(func)
                button.clicked.connect(lambda _, f=func: self.on_click(f))
                
                box.addWidget(button, y, x)
                x += 1
                if x == 3:
                    y += 1
                    x = 0
            self.window = window
        except Exception as e:
            logging.error(str(e))
        
    def on_click(self, func):
        try:
            logging.info(func)
            
            if func != 'pi':
                self.window.entry.insert(func+'(')
            else:
                self.window.entry.insert(func)
            
        except Exception as e:
            print(e)
        
        


class EqualationUI(QWidget):
    def __init__(self):
        super().__init__()
        self.box = QVBoxLayout(self)
        label_system_of_equations_text = QLabel(parent=self, text="Введите систему уравнений (через пробел):")
        label_system_of_equations_text.move(0, 60)

        self.entry = QLineEdit(self)
        self.entry.move(0, 80)
        
        self.button_system_of_equations = QPushButton(parent=self, text="Решить систему уравнений")
        self.button_system_of_equations.move(305, 80)
        self.entry.resize(250, 20)

        self.label_system_of_equations = QLineEdit(self)
        self.label_system_of_equations.move(0, 105)
        self.label_system_of_equations.resize(1000, 40)
        self.button = QPushButton("Функции")
        self.button.clicked.connect(lambda: self.functions())
        self.label_system_of_equations.setReadOnly(True)
        self.box.addWidget(label_system_of_equations_text)
        self.box.addWidget(self.entry)
        self.box.addWidget(self.button_system_of_equations)
        self.box.addWidget(self.label_system_of_equations)
        self.entry.returnPressed.connect(lambda: self.on_click())
        self.button_system_of_equations.clicked.connect(lambda: self.on_click())
        self.box.addWidget(self.button)
    def functions(self):
        func = Functionsympy(self)
        func.show()
    def on_click(self):
        solve_system_of_equations(self)



from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QFileDialog, QDialogButtonBox
import json
import csv
import pandas as pd
from PyQt6 import QtWidgets
class StatisticUI(QWidget):
    def __init__(self):
        super().__init__()

        label_number_entry = QLabel(parent=self, text="Введите числа через пробел:")
        label_number_entry.move(0, 145)

        self.entry_numbers = QLineEdit(self)
        self.entry_numbers.resize(245, 20)
        self.entry_numbers.move(0, 165)
        
        self.button_mean = QPushButton(parent=self, text="Среднее значение")
        self.button_mean.move(305, 160)

        self.button_median = QPushButton(parent=self, text="Медиана")
        self.button_median.move(418, 160)

        self.button_max = QPushButton(parent=self, text="Максимум")
        self.button_max.move(484, 160)

        self.button_min = QPushButton(parent=self, text="Минимум")
        self.button_min.move(556, 160)

        self.button_range = QPushButton(parent=self, text="Размах")
        self.button_range.move(624, 160)

        self.button_variance = QPushButton(parent=self, text="Дисперсия")
        self.button_variance.move(690, 160)

        self.label_stat_result =QLineEdit(self)
        self.label_stat_result.move(0, 200)
        self.label_stat_result.resize(1000, 30)
        self.import_data_btn = QPushButton("Импортировать данные")
        self.box = QVBoxLayout(self)
        self.label_stat_result.setReadOnly(True)
        self.box.addWidget(label_number_entry)
        self.box.addWidget(self.entry_numbers)
        self.box.addWidget(self.button_mean)
        self.box.addWidget(self.button_median)
        self.box.addWidget(self.button_max)
        self.box.addWidget(self.button_min)
        self.box.addWidget(self.button_range)
        self.box.addWidget(self.button_variance)
        self.box.addWidget(self.label_stat_result)
        self.box.addWidget(self.import_data_btn)
        self.import_data_btn.clicked.connect(lambda: self.import_data())
        self.button_mean.clicked.connect(lambda: self.on_click('mean'))
        self.button_median.clicked.connect(lambda: self.on_click('median'))
        self.button_max.clicked.connect(lambda: self.on_click('max'))
        self.button_min.clicked.connect(lambda: self.on_click('min'))
        self.button_range.clicked.connect(lambda: self.on_click('range'))
        self.button_variance.clicked.connect(lambda: self.on_click('variance'))
    def on_click(self, stat_type):
        calculate_statistics(self, stat_type)
    def import_data(self):
        try:
            self.dialog = loadUi("import_data.ui")
            
            self.dialog.pushButton.clicked.connect(lambda: self.get_file())
            
            
            self.dialog.show()
            self.dialog.exec()
        except Exception as e:
            print(e)
    def get_file(self):
        try:
            self.dialog.lineEdit_2.setEnabled(False)
            self.dialog.lineEdit_3.setEnabled(False)
            self.file_name, _ = QFileDialog.getOpenFileName(None,
                                                   'Выберите файл',
                                                   '',
                                                   'Файлы TXT (*.txt);;Файлы JSON (*.json);;Файлы CSV (*.csv);;Файлы XLSX (*.xlsx)')
            self.dialog.Cancel.clicked.connect(lambda: self.dialog.close())
            if self.file_name:
                print(f'Выбран файл: {self.file_name}')
                if _ == 'Файлы XLSX (*.xlsx)':
                    
                    self.dialog.lineEdit_3.setEnabled(True)
                    
                    
                    self.dialog.Ok.clicked.connect(lambda: self.test_file())
                    
                elif _ == "Файлы JSON (*.json)":
                    self.dialog.Ok.clicked.connect(lambda: self.json_file())
                elif _ == "Файлы CSV (*.csv)":
                    self.dialog.lineEdit_3.setEnabled(True)
                    
                    self.dialog.Ok.clicked.connect(lambda: self.csv_file())
                elif _ == "Файлы TXT (*.txt)":
                    self.dialog.lineEdit_2.setEnabled(True)
                    self.dialog.Ok.clicked.connect(lambda: self.txt_file())
        except Exception as e:
            print(e)
    def test_file(self):
        try:
            df = pd.read_excel(self.file_name)
            columns = self.dialog.lineEdit_3.text()
            # Преобразуем столбец 'Price' в список
            prices = df[f'{columns}'].tolist()
            prices = list(map(str, prices))
            print(prices)
            self.entry_numbers.setText(f'{" ".join(prices)}')
        except Exception as e:
            logging.error(f"{e}")
            addings.handle_error(str(e), None, "test_file from UI")
    def json_file(self):
        try:
            data = []
            with open(self.file_name, "r", encoding="UTF-8") as file:
                dic = json.load(file)
                print(dic, type(dic))
            if type(dic) == dict:
                for dat in dic.keys():
                    
                    dat = dic[dat]
                    if type(dat) == list:
                        print("Сработало")
                        for dat_1 in dat:
                            data.append(dat_1)
                    else:
                        dat = dic[dat]
                        data.append(dat)
            elif type(dic) == list:
                for dat in dic:
                    data.append(dat)
            else:
                pass
            print(data)
            self.entry_numbers.setText(f"{" ".join(list(map(str, data)))}")
        except Exception as e:
            logging.error(f"{e}")
            addings.handle_error(str(e), None, "json_file from UI")
    def csv_file(self):
        try:
            data = []
            
            with open(self.file_name, "r", newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    columns = self.dialog.lineEdit_3.text()
                    data.append(row[columns])
                print(data)
            self.entry_numbers.setText(" ".join(data))
        except Exception as e:
            logging.error(f"{e}")
            addings.handle_error(str(e), None, "csv_file from UI")
    def txt_file(self):
        try:
            data = []
            c = []
            with open(self.file_name, "r") as file:
                text = file.read().split("\n")
                for row in text:
                    separ = self.dialog.lineEdit_2.text()
                    i = row.split(separ)
                    c.append(i)
            for b in c:
                for a in b:
                    data.append(a)
            print(data)
            self.entry_numbers.setText(" ".join(data))
        except Exception as e:
            logging.error(f"{e}")
            addings.handle_error(str(e), None, "txt_file from UI")
            
        
from trinogremetric import *
class TrigonometryUI(QWidget):
    
    def __init__(self):
        try:
            super().__init__()

            cord_x = 0
            cord_y = 220
            self.label_trig_text = QLabel(parent=self, text="Введите угол синус, косинус или тангенс которого вы хотите найти:")
            self.label_trig_text.move(cord_x, cord_y)

            self.trig_input = QLineEdit(self)
            self.trig_input.move(cord_x, cord_y + 20)

            self.sin_button = QPushButton(parent=self, text="sin")
            self.sin_button.move(cord_x, cord_y + 40)

            self.cos_button = QPushButton(parent=self, text="cos")
            self.cos_button.move(cord_x + 100, cord_y + 40)

            self.tan_button = QPushButton(parent=self, text="tan")
            self.tan_button.move(cord_x + 200, cord_y + 40)
            self.arcsin_button = QPushButton(parent=self, text="arcsin")
            self.arcsin_button.move(cord_x + 200, cord_y + 60)
            self.arccos_button = QPushButton(parent=self, text="arccos")
            self.arccos_button.move(cord_x + 200, cord_y + 80)
            self.arctan_button = QPushButton(parent=self, text='arctan')
            self.trig_output = QLineEdit(self)
            self.trig_output.setReadOnly(True)
            self.trig_output.move(cord_x + 135, cord_y + 20)
            self.trig_output.resize(1000, 30)
            self.ctg_button = QPushButton(parent=self, text='ctg')
            self.box = QVBoxLayout(self)
            self.box.addWidget(self.label_trig_text)
            self.box.addWidget(self.trig_input)
            self.box.addWidget(self.sin_button)
            self.box.addWidget(self.cos_button)
            self.box.addWidget(self.tan_button)
            self.box.addWidget(self.ctg_button)
            self.box.addWidget(self.arcsin_button)
            self.box.addWidget(self.arccos_button)
            self.box.addWidget(self.arctan_button)
            self.box.addWidget(self.trig_output)
            self.sin_button.clicked.connect(lambda: self.on_click('sin'))
            self.cos_button.clicked.connect(lambda: self.on_click('cos'))
            self.tan_button.clicked.connect(lambda: self.on_click('tan'))
            self.ctg_button.clicked.connect(lambda: self.on_click('ctg'))
            self.arcsin_button.clicked.connect(lambda: self.on_click('arcsin'))
            self.arccos_button.clicked.connect(lambda: self.on_click('arccos'))
            self.arctan_button.clicked.connect(lambda: self.on_click('arctan'))
        except Exception as e:
            print(e)
    def on_click(self, type):
        process_trigonometric_function(self, type)


class FractionUI(QWidget):
    def __init__(self):
        super().__init__()

        label_fractions_text = QLabel("Арифметика дробей:", self)
        label_fractions_text.move(0, 0)

        self.entry_first_fraction = QLineEdit(self)
        self.entry_first_fraction.move(0, 25)

        self.entry_second_fraction = QLineEdit(self)
        self.entry_second_fraction.move(165, 25)

        self.operator_variable = QComboBox(self)
        self.operator_variable.addItems(["+", "-", "*", "/"])
        self.operator_variable.move(135, 25)

        self.button_fractions_calculate = QPushButton("Выполнить операцию", self)
        self.button_fractions_calculate.move(0, 50)

        self.label_fractions_result = QLineEdit(self)
        self.label_fractions_result.move(0, 80)
        self.label_fractions_result.resize(300, 20)
        self.label_fractions_result.setReadOnly(True)
        self.box = QGridLayout(self)

        self.box.addWidget(self.entry_first_fraction, 1, 0)

        self.box.addWidget(self.entry_second_fraction, 1, 2)
        self.box.addWidget(label_fractions_text, 0, 0, 1, 3)
        self.box.addWidget(self.button_fractions_calculate, 2, 0, 1, 3)
        self.box.addWidget(self.operator_variable, 1, 1)
        self.box.addWidget(self.label_fractions_result, 3, 0, 1, 3)
        self.button_fractions_calculate.clicked.connect(lambda: self.on_click())
        self.entry_first_fraction.returnPressed.connect(lambda: self.on_click())
        self.entry_second_fraction.returnPressed.connect(lambda: self.on_click())
    def on_click(self):
        arithmetic_operation_fractions(self, self.entry_first_fraction.text(), self.entry_second_fraction.text(), self.operator_variable.currentText())

class NewApp(QWidget):
    def __init__(self):
        super().__init__()
        tab = QTabWidget(self)
        self.page = QWidget(tab)
        self.box = QGridLayout(self)
        self.setWindowTitle("Расширенный калькулятор")
        calculator = Calculator()
        self.page.setLayout(calculator.box)
        tab.addTab(self.page, 'Калькулятор')
        page2 = QWidget(tab)
        equate = EqualationUI()
        page2.setLayout(equate.box)
        tab.addTab(page2, 'Решение уравнений')

        stati = StatisticUI()
        page3 = QWidget(tab)
        page3.setLayout(stati.box)
        tab.addTab(page3, 'Статистика')
        tab.setGeometry(0, 0, 800, 300)

        page4 = QWidget(tab)
        trigo = TrigonometryUI()
        page4.setLayout(trigo.box)
        tab.addTab(page4, "Тригонометрия")

        page5 = QWidget(tab)
        frac = FractionUI()
        page5.setLayout(frac.box)
        tab.addTab(page5, "Арифметика дробей")
        page6 = QWidget(tab)

        sch = SistemSchileniy()
        page6.setLayout(sch.box)
        tab.addTab(page6, "Системы счисления")
        # self.history_text = QTextEdit(self)
        self.box.addWidget(tab, 0, 0, 3, 1)
        # self.box.addWidget(self.history_text)
        self.setGeometry(30, 30, 1000, 300)
        page7 = QWidget(tab)
        schp = SistemSchileniyPerevod()
        page7.setLayout(schp.box)
        tab.addTab(page7, "Перевод в сс")
        self.reklam = QPushButton("Калькулятор по формулам", self)
        self.box.addWidget(self.reklam, 1, 1)
        self.tg = QPushButton("Телеграм канал", self)
        self.tg.clicked.connect(lambda: self.on_click("https://t.me/Ras_Kakulator_official"))
        self.box.addWidget(self.tg, 0, 1)
        self.reklam.clicked.connect(lambda: self.on_click("https://kostyaramensky.pythonanywhere.com/"))
        self.send_error = QPushButton("Сообщить об ошибке", self)
        self.box.addWidget(self.send_error, 2, 1)
        self.send_error.clicked.connect(lambda: self.on_click("https://forms.yandex.ru/u/6861698d84227cbab5e787ba"))
    def on_click(self, link):
        #c = 2/0
        webbrowser.open_new_tab(link)
from addings import history_of_errors
def quit_from_app():

    try:
        url = "https://rascalculator.alwaysdata.net/send_errors/"
        version_file = "version.txt"
        with open(version_file, "r") as file:
            installed_version = file.read().strip()

        
        data = []
        
        
        
        for error in history_of_errors:
            data.append({
                "error": error,
                "version": installed_version,
                "source": "Не указан, Приложение"
            })

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
        print(data)
        response = session.post(url, json=data, headers=headers)
        print(response.status_code)
    except Exception as e:
        print(e)
if __name__ == '__main__':
    with open("logs.log", "w") as f:
        f.write("")
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename='logs.log', encoding="UTF-8")
    from start import *

    sys.excepthook = global_exception_handler
    app = QApplication(sys.argv)

    logging.info(sys.argv)
    check_first_run_and_show_tutorial()
    app.setWindowIcon(QIcon("calculator.ico"))
    window = NewApp()
    window.show()
    print("Hello")
    app.aboutToQuit.connect(quit_from_app)
    sys.exit(app.exec())
