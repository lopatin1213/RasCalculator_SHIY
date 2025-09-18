from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox
import sys
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize




class MyApp(QWidget):
	def __init__(self):
		super().__init__()
		
		# Настройка окна
		self.setWindowTitle("Расширенный калькулятор")
		self.resize(1000, 1000)
		# Кнопка внутри окна
		button_settings = QPushButton(self)
		icon = QIcon("settings_icon.png")
		button_settings.setIcon(icon)
		button_settings.setIconSize(icon.actualSize(QSize(30, 30)))
		button_settings.move(955, 0)
		
		label_basic_calc_text = QLabel(self)
		label_basic_calc_text.setText("Введите числовое выражение (2+2):")
		label_basic_calc_text.move(0, 0)
		
		help_button = QPushButton(self)
		help_button.setText("Справка")
		help_button.move(930, 55)
		
		entry = QLineEdit(self)
		entry.move(0, 20)
		
		button_calc = QPushButton(self)
		
		button_calc.setText("Вычислить")
		button_calc.move(216, 15)
		
		label = QLabel(self, text="Hello World")
		label.move(0, 40)
		
		label_system_of_equations_text = QLabel(self, text="Введите систему уравнений (через пробел):")
		label_system_of_equations_text.move(0, 60)
		
		entry_system_of_equations = QLineEdit(self)
		entry_system_of_equations.move(0, 80)
		
		button_system_of_equations = QPushButton(self, text="Решить систему уравнений")
		button_system_of_equations.move(305, 80)
		entry_system_of_equations.resize(250, 20)
		
		label_system_of_equations = QLabel(self)
		label_system_of_equations.move(0, 105)
		
		label_number_entry = QLabel(self, text="Введите числа через пробел:")
		label_number_entry.move(0, 145)
		
		entry_numbers = QLineEdit(self)
		entry_numbers.resize(245, 20)
		entry_numbers.move(0, 165)
		
		button_mean = QPushButton(self, text="Среднее значение")
		button_mean.move(305, 160)
		
		button_median = QPushButton(self, text="Медиана")
		button_median.move(418, 160)
		
		button_max = QPushButton(self, text="Максимум")
		button_max.move(484, 160)
		
		button_min = QPushButton(self, text="Минимум")
		button_min.move(556, 160)
		
		button_range = QPushButton(self, text="Размах")
		button_range.move(624, 160)
		
		button_variance = QPushButton(self, text="Дисперсия")
		button_variance.move(690, 160)
		
		
		
		label_stat_result = QLabel(self, text="Hello World")
		label_stat_result.move(0, 200)
		
		button_exit = QPushButton(self, text="Выход")
		button_exit.move(930, 85)
		
		error_text = QTextEdit(self, )
		error_text.setReadOnly(True)
		error_text.resize(500,300)
		error_text.move(0, 400)
		error_text.setText("Hello World")
		button_cor = QPushButton(self, text='√')
		button_cor.move(296, 15)
		label_fractions_text = QLabel(self, text="Арифметика дробей:")
		label_fractions_text.move(0, 290)
		
		entry_first_fraction = QLineEdit(self)
		entry_first_fraction.move(0, 310)
		
		entry_second_fraction = QLineEdit(self)
		entry_second_fraction.move(185, 310)
		
		operator_variable = QComboBox(self)
		operator_variable.addItems(["+", "-", "*", "/"])
		operator_variable.move(125, 310)
		
		button_fractions_calculate = QPushButton(self, text="Выполнить операцию")
		button_fractions_calculate.move(0, 338)
		
		label_fractions_result = QLabel(self, text="Hello World")
		label_fractions_result.move(0, 363)
		
		history_text = QTextEdit(self)
		history_text.move(0, 540)
		history_text.resize(600, 300)
		label_of_errors = QLabel(self, text='Поле с ошибками при вычислении:')
		label_of_errors.move(0, 380)
		
		cl_b = QPushButton(self, text="Очистить историю")
		cl_b.move(680, 530)
		cord_x = 0
		cord_y = 220
		label_trig_text = QLabel(self, text="Введите угол синус, косинус или тангенс которого вы хотите найти:")
		label_trig_text.move(cord_x, cord_y)
		
		trig_input = QLineEdit(self)
		trig_input.move(cord_x, cord_y + 20)
		
		sin_button = QPushButton(self, text="sin")
		sin_button.move(cord_x, cord_y + 40)
		
		cos_button = QPushButton(self, text="cos")
		cos_button.move(cord_x + 100, cord_y + 40)
		
		tan_button = QPushButton(self, text="tan")
		tan_button.move(cord_x + 200, cord_y + 40)
		
		trig_output = QLabel(self, text="Hello World")
		trig_output.move(cord_x + 135, cord_y + 20)
		
		tgb = QPushButton(self, text='Перейти в официальный тгк Калькулятора')
		tgb.move(750, 115)
		
		form_btn = QPushButton(self, text='Собщить об ошибке')
		form_btn.move(870, 150)
		

if __name__ == '__main__':
	app = QApplication(sys.argv)
	
	app.setWindowIcon(QIcon("calculator.ico"))
	window = MyApp()
	window.show()
	sys.exit(app.exec())