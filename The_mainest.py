import traceback
import requests
# Библиотеки для математики и вычислений
import math
from decimal import Decimal, getcontext
from fractions import Fraction
from sympy import *
import numpy as np

# Графический интерфейс (Tkinter)
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
from tkinter import colorchooser as tkcolorchooser

# Работа с изображениями
from PIL import Image, ImageTk

# Библиотека для графиков
import matplotlib.pyplot as plt

# Конфигурационные инструменты
import configparser

# Логирование
import logging

# Модули внешних пакетов
from settings_panel import SettingsPanel

# Настройка уровня логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename='logs.log')

# Глобальные переменные
previous_result = None
history = []

# Основные константы
DEFAULT_BG_COLOR = '#FFFFFF'

# Цветовая палитра
CONTRAST_BLACK = '#000000'
CONTRAST_WHITE = '#FFFFFF'


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
	create_config_file('config.ini')  # Создание файла конфигурации
	choose_color()  # Выбор цвета фона
	
	try:
		with open(preferences_file, "w") as file:
			file.write("False")
			logging.info(f"Файл '{preferences_file}' обновлён.")
	except PermissionError:
		logging.error(f"Ошибка: не удаётся записать в файл '{preferences_file}'. Проверьте права доступа.")
	except Exception as e:
		logging.error(f"Неожиданная ошибка при записи в файл '{preferences_file}': {e}")


def check_first_run_and_show_tutorial(root, preferences_file="preferences.txt"):
	"""Проверяет, является ли запуск приложения первым, и выполняет соответствующие действия."""
	check_version()
	if is_first_run(preferences_file):
		handle_first_run(preferences_file)
	else:
		logging.info("Это не первый запуск.")
		ensure_config_file_exists(root)


def show_tutorial(title="Добро пожаловать!", message=None):
	"""Отображает обучающее сообщение пользователю."""
	if message is None:
		message = (
			"Добро пожаловать в расширенный калькулятор!\n\n"
			"Здесь вы можете решать уравнения, считать среднее арифметическое,\n"
			"медиану, минимальное и максимальное значение, и многое другое."
		)
		messagebox.showinfo(title='Лицензионное соглашение', message=
		"""
Программа "Рас. Калькулятор" распространяется бесплатно и предоставляется "как есть".
Пользователь соглашается не распространять данное программное обеспечение третьим лицам без письменного разрешения разработчика.
Если же хотите опубликовать программу где-то во-первых напишите мне чтобы я знал что вы хотите где-то опубликовать приложение
Использование программы осуществляется исключительно на риск пользователя.
Разработчики не несут ответственности за любые убытки, вызванные неправильным использованием данной программы.
Сайт разработчика: https://rascalculator.pythonanywhere.com
Продолжая работу с программой, вы принимаете вышеуказанное лицензионное соглашение.

		""")
	try:
		messagebox.showinfo(title=title, message=message)
		
		logging.info("Обучающее сообщение отображено.")
	except Exception as e:
		logging.error(f"Ошибка при отображении обучающего сообщения: {e}")


import os
import webbrowser
from tkinter import messagebox


# Настройка логирования


def has_internet_connection():
	"""
	Проверяет наличие соединения с интернетом.
	"""
	try:
		# Пробуем соединиться с внешним сервисом
		response = requests.head("http://www.google.com/", timeout=5)
		return response.status_code == 200
	except requests.ConnectionError:
		
		return False


def check_version():
	version_file = "version.txt"
	server_url = "https://rascalck.pythonanywhere.com/version/"
	curent_vers_file = "cur_version.txt"
	if not has_internet_connection():
		messagebox.showwarning(
			"Проблемы с интернетом",
			"Хитро придумали, отключить интернет...\n\n"
			"Но избежать проверки версии не получится"
		)
		with open(curent_vers_file, 'r') as f2:
			current_version = f2.read().strip()
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
			choice = messagebox.showwarning(
				"Доступна новая версия",
				f"Ваша версия {installed_version} устарела.\n"
				f"Рекомендуется установить последнюю версию с официального сайта FreeSoft:\n"
			)
		else:
			messagebox.showinfo(
				"Все ок",
				"""
Ладно живи у тебя актуальная версия :)
И больше не отключай интернет :|
				"""
			)
	try:
		response = requests.get(server_url)
		response.raise_for_status()
		current_version = response.text.strip()
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
			choice = messagebox.askyesno(
				"Доступна новая версия",
				f"Ваша версия {installed_version} устарела.\n"
				f"Рекомендуется установить последнюю версию с официального сайта Расширенного Калькулятора:\n"
				f"https://rascalculator.pythonanywhere.com/download\n\n"
				f"Эту страницу подтверждаю я как единственное официальное место для скачивания нашего калькулятора.\n\n"
				f"Желаете перейти на страницу загрузки?"
			)
			
			if choice:
				# Открываем ссылку на скачивание
				webbrowser.open_new_tab("https://rascalculator.pythonanywhere.com/download")
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


def create_config_file(filename):
	"""Создаёт файл конфигурации при его отсутствии."""
	try:
		with open(filename, 'r') as config_file:
			logging.info(f"Файл конфигурации '{filename}' успешно открыт.")
	except FileNotFoundError:
		config = configparser.ConfigParser()
		config['UserSettings'] = {'SelectedColor': DEFAULT_BG_COLOR}
		with open(filename, 'w') as config_file:
			config.write(config_file)
			logging.info(f"Файл конфигурации '{filename}' успешно создан.")
	except PermissionError as e:
		logging.error(f"Ошибка при создании файла конфигурации '{filename}': {e}")
	except Exception as e:
		logging.error(f"Неожиданная ошибка при работе с файлом конфигурации '{filename}': {e}")


def choose_color():
	"""Позволяет пользователю выбрать цвет фона и сохраняет его в настройках."""
	color = tkcolorchooser.askcolor(initialcolor=read_config())[1]
	if color:
		write_config(color)
		root.config(bg=color)
		apply_theme(root, color)


def write_config(selected_color):
	"""Записывает выбранный цвет в файл конфигурации."""
	config = configparser.ConfigParser()
	config['PerviousSettings'] = {'SelectedColor': selected_color}
	with open('config.ini', 'w') as configfile:
		config.write(configfile)


def read_config():
	"""Читает ранее сохранённый цвет из файла конфигурации."""
	config = configparser.ConfigParser()
	config.read('config.ini')
	try:
		selected_color = config['PerviousSettings']['SelectedColor']
		return selected_color
	except KeyError:
		return DEFAULT_BG_COLOR


def ensure_config_file_exists(root, filename='config.ini'):
	"""Гарантирует существование файла конфигурации."""
	try:
		with open(filename, 'r') as config_file:
			logging.info(f"Файл конфигурации '{filename}' успешно открыт.")
	except FileNotFoundError:
		create_config_file(filename)
		choose_color()
	except PermissionError as e:
		logging.error(f"Ошибка при чтении файла конфигурации '{filename}': {e}")
	except Exception as e:
		logging.error(f"Неожиданная ошибка при открытии файла конфигурации '{filename}': {e}")


def contrast_color(hex_color):
	"""Возвращает контрастный цвет для заданного HEX-цвета."""
	try:
		if not isinstance(hex_color, str):
			raise ValueError("hex_color должен быть строкой")
		if not hex_color.startswith("#") or len(hex_color) != 7:
			raise ValueError("Недопустимый формат HEX-кода")
		
		red = int(hex_color[1:3], 16)
		green = int(hex_color[3:5], 16)
		blue = int(hex_color[5:], 16)
		
		# Инвертирование каждого компонента RGB
		inverted_red = 255 - red
		inverted_green = 255 - green
		inverted_blue = 255 - blue
		
		# Преобразование обратно в HEX-код
		contrast_hex = "#{:02X}{:02X}{:02X}".format(inverted_red, inverted_green, inverted_blue)
		return contrast_hex
	except (ValueError, TypeError) as e:
		logging.error(f"Ошибка при вычислении контрастного цвета: {e}")
		return CONTRAST_BLACK


def analogous_colors(hex_color, shift_angle=30):
	"""Генерация аналоговых цветов для заданного HEX-цвета."""
	import colorsys
	rgb_color = tuple(int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
	hsv_color = colorsys.rgb_to_hsv(*rgb_color)
	hue, sat, val = hsv_color
	
	# Определение левого и правого соседних оттенков
	left_hue = (hue - shift_angle / 360) % 1
	right_hue = (hue + shift_angle / 360) % 1
	
	# Преобразование HSV обратно в RGB
	left_rgb = colorsys.hsv_to_rgb(left_hue, sat, val)
	right_rgb = colorsys.hsv_to_rgb(right_hue, sat, val)
	
	# Преобразование обратно в HEX
	left_hex = "#{:02X}{:02X}{:02X}".format(*(int(c * 255) for c in left_rgb))
	right_hex = "#{:02X}{:02X}{:02X}".format(*(int(c * 255) for c in right_rgb))
	return left_hex


def apply_theme(root, bg_color):
	"""Применяет тему оформления к главному окну и элементам интерфейса."""
	root.config(bg=bg_color)
	style = ttk.Style()
	style.configure('.', background=bg_color, foreground=contrast_color(bg_color))
	style.configure('TLabel', background=bg_color, foreground=contrast_color(bg_color))
	style.configure('TButton', background=analogous_colors(bg_color),
	                foreground=contrast_color(analogous_colors(bg_color)))
	style.configure('TEntry', foreground=contrast_color(analogous_colors(bg_color)),
	                fieldbackground=analogous_colors(bg_color), insertbackground='black',
	                selectforeground=contrast_color(bg_color), selectbackground='gray')
	style.configure('Text', background=bg_color, foreground=contrast_color(bg_color))


def replace_caret_with_power(expression):
	"""Заменяет символ ^ на оператор возведения в степень (**)."""
	return expression.replace('^', '**')


def replace_z_t(expression):
	"""Заменяет запятую на точку в числе."""
	return expression.replace(',', '.')


import asyncio
import math
from decimal import Decimal


def custom_factorial(n):
	"""Вычисляет факториал натурального числа."""
	if n < 0:
		raise ValueError("Факториал отрицательного числа не определен")
	elif n == 0 or n == 1:
		return 1
	else:
		result = 1
		for i in range(2, n + 1):
			result *= i
		
		return result


def nth_root(number, n):
	"""Вычисляет корень n-й степени из числа."""
	if number < 0 and n % 2 == 0:
		raise ValueError("Корень четной степени из отрицательного числа невозможен.")
	return number ** (1 / n)


def calculate(event):
	try:
		expression = entry.get()
		expression = replace_z_t(expression)
		expression = replace_caret_with_power(expression)
		print(expression)
		if expression == "":
			return
		if '0' in expression and '/' in expression:
			parts = expression.split('/')
			if parts[1].strip() == '0':
				raise ZeroDivisionError
		if '!' in expression:
			expression = expression.replace('!', '')
			result = factorial_scientific(int(expression))
			final_result = dynamic_precision(result)
			mantissa, exponent = final_result.split("E")
			final_result = "{}*10^{}".format(float(mantissa), int(exponent))
			add_to_history(expression, final_result)
			update_history()
			label.config(text=f"Результат: {final_result}")
			clear_errors()
			clear_labels(label)
			return
		elif '√' in expression:
			parts = expression.split('√')
			if len(parts) != 2:
				raise ValueError("Неверный формат корня")
			n = int(parts[0])
			x = int(parts[1])
			result = nth_root(x, n)
		else:
			result = sympify(expression).evalf()
			logging.info(result)
			result = float(result)
		
		# Применение динамической точности
		final_result = format_number(dynamic_precision(result))
		add_to_history(expression, final_result)
		update_history()
		label.config(text=f"Результат: {final_result}")
		clear_errors()
		clear_labels(label)
	
	except ZeroDivisionError:
		handle_error("Ошибка: деление на ноль.", input_data=expression, function_name='calculate', lb=label)
	except ValueError as ve:
		handle_error(f"Ошибка: {ve}", input_data=expression, function_name='calculate', lb=label)
	except SyntaxError:
		handle_error("Ошибка: синтаксическая ошибка в выражении.", input_data=expression, function_name='calculate',
		             lb=label)
	except Exception as e:
		handle_error(f"Ошибка: {e}", input_data=expression, function_name='calculate', lb=label)


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


def parse_numbers(numbers_str):
	"""Парсит строку чисел, введённых пользователем."""
	if ',' in numbers_str:
		response = messagebox.askyesno(
			"Интерпретация запятой",
			"Вы ввели запятую. Как её интерпретировать?\n"
			"Да - как десятичную точку (например, 1,5 -> 1.5)\n"
			"Нет - как разделитель чисел (например, 1,5 -> 1 5)"
		)
		if response:
			numbers_str = numbers_str.replace(',', '.')
		else:
			numbers_str = numbers_str.replace(',', ' ')
	numbers = [float(num.strip()) for num in numbers_str.split()]
	return numbers


import math

from decimal import Decimal, getcontext


def factorial_scientific(n):
	"""
	Представляет факториал числа в научной форме.

	Параметры:
	- n: Число, факториал которого нужно представить.

	Возвращает:
	Строку с представлением факториала в научной форме.
	"""
	if not isinstance(n, int) or n < 0:
		raise ValueError("Факториал определен только для неотрицательных целых чисел")
	
	# Устанавливаем высокую точность для работы с большими числами
	getcontext().prec = 100  # Можно увеличить точность при необходимости
	
	# Рассчитываем факториал
	fact = Decimal(1)
	for i in range(1, n + 1):
		fact *= Decimal(i)
	
	# Представляем в научной форме
	scientific_representation = "{:.5E}".format(fact.normalize())
	
	return scientific_representation


def plot_linear_equation(a, b, c):
	"""
	Строит график линейного уравнения ax + by + c = 0.
	"""
	# Генерируем диапазон значений x с высокой точностью
	x = np.linspace(-10000, 10000, 100000)  # 100000 точек между -10000 и 10000
	# Вычисляем соответствующие значения y
	y = (-c - a * x) / b
	# Строим график
	fig, ax = plt.subplots()
	ax.plot(x, y, label=f"{a}x + {b}y + {c} = 0")
	ax.set_xlabel('x')
	ax.set_ylabel('y')
	ax.grid(True)
	ax.legend()
	
	# Устанавливаем начальные границы оси X и Y
	ax.set_xlim([-10, 10])
	ax.set_ylim([-10, 10])
	b_str = str(b)
	# Центрируем график относительно точки (0, b)
	center_x = 0
	if not "-" in b_str:
		center_y = -c / b
	else:
		center_y = -c / b
	center_y = float(center_y)  # Убеждаемся, что center_y является числом
	center_x = float(center_x)
	ax.set_xlim(center_x - 10, center_x + 10)  # Центрирование по оси X
	ax.set_ylim(center_y - 10, center_y + 10)  # Центрирование по оси Y
	
	# Выделяем оси x и y
	ax.axhline(0, color='black', linewidth=1)  # Горизонтальная ось y=0
	ax.axvline(0, color='black', linewidth=1)  # Вертикальная ось x=0
	
	# Помещаем точку (0, b) в центр графика
	ax.scatter(center_x, center_y, s=50, color='blue', marker='o', label=f'(0, {center_y})')  # Размер точки s=50
	ax.legend()
	y_1 = 0
	if not "-" in b_str:
		x_1 = -c / a
	else:
		x_1 = -c / a
	x_1 = float(x_1)
	ax.scatter(x_1, y_1, s=50, color='red', marker='o', label=f'({x_1}, 0)')
	ax.legend()
	
	# Назначаем события мыши для динамического масштабирования
	def on_motion(event):
		if event.inaxes:
			# Получаем текущие границы оси X
			xmin, xmax = ax.get_xlim()
			# Проверяем, достигнута ли граница оси X
			if event.xdata > xmax - 0.01 * (xmax - xmin) or event.xdata < xmin + 0.01 * (xmax - xmin):
				# Расширяем границы оси X
				ax.set_xlim(xmin - 0.05 * (xmax - xmin), xmax + 0.05 * (xmax - xmin))
				fig.canvas.draw_idle()
	
	# Привязываем событие движения мыши
	fig.canvas.mpl_connect('motion_notify_event', on_motion)
	
	plt.show()


import re


def transform_equation(lhs, rhs):
	"""
	Преобразует уравнение вида y = kx + b в b = y - kx.

	Аргументы:
	- lhs: левая сторона уравнения.
	- rhs: правая сторона уравнения.

	Возвращает:
	Преобразованное уравнение.
	"""
	# Регулярное выражение для извлечения коэффициентов и переменных
	pattern = r'(?P<y>\w+)\s*=\s*((?P<k>[+-]?\d*\.*\d*)?\s*\*\s*)?(?P<x>\w+)(?:\s*[+-]?\s*(?P<b>-?\d*\.*\d*))?'
	# Объединяем левую и правую стороны в одно уравнение
	equation = f"{lhs} = {rhs}"
	
	match = re.match(pattern, equation)
	
	if not match:
		return "Неверный формат уравнения."
	
	y = match.group('y')
	k = match.group('k') or '1'  # Если коэффициент не указан, считаем его равным 1
	x = match.group('x')
	b = match.group('b') or '0'
	
	transformed_eq = f"{y}-{k}*{x}={b}"
	return transformed_eq


def solve_system_of_equations(event=None):
	try:
		# Получаем уравнения из поля ввода
		equations_str = entry_system_of_equations.get()
		logging.info(f"Полученная строка уравнений: {equations_str}")
		if equations_str == "":
			return
		# Проверяем наличие запятых в строке
		if ',' in equations_str:
			logging.info("Обнаружены запятые, уточняем интерпретацию...")
			response = messagebox.askyesno(
				"Интерпретация запятой",
				"Вы ввели запятую. Как её интерпретировать?\n"
				"Да - как разделитель дробной части (например, 1,5 -> 1.5)\n"
				"Нет - как разделитель уравнений (например, 1,5 -> 1 5)"
			)
			
			if response:
				logging.info("Замена запятых на точки.")
				equations_str = equations_str.replace(',', '.')
			else:
				logging.info("Замена запятых на пробелы.")
				equations_str = equations_str.replace(', ', ' ')
		
		# Разбиение строки на отдельные уравнения
		equations_list = equations_str.split(' ')
		logging.info(f"Разбито на уравнения: {equations_list}")
		
		# Преобразование уравнений в объекты Sympy
		expressions = []
		used_variables = set()  # Множество переменных, используемых в уравнениях
		for equation in equations_list:
			logging.info(f"Преобразование уравнения: {equation}")
			equation = equation.replace('=', '==')
			equation = re.sub(r'(\d+)([a-zA-Z])', r'\1*\2', equation)
			lhs, rhs = equation.split('==')
			print(lhs)
			print(rhs)
			expressions.append(Eq(sympify(lhs), sympify(rhs)))
			logging.info(f"Добавлено уравнение: {expressions[-1]}")
			
			# Определяем переменные, участвующие в текущем уравнении
			used_variables.update(list(expressions[-1].free_symbols))
		
		logging.info(f"Переменные, задействованные в уравнениях: {used_variables}")
		
		# Проверка на недоопределённость системы
		if len(expressions) < len(used_variables) and len(used_variables) <= 2:
			logging.info("Количество уравнений меньше количества переменных, система недоопределена.")
			response = messagebox.askyesno(
				"Бесконечное множество решений",
				"Система уравнений имеет бесконечное множество решений.\nХотите увидеть график?"
			)
			if response:
				variable = re.findall('[A-Za-zА-ЯЁа-яё]', lhs)
				print(variable)
				variables = [Symbol(name) for name in variable]
				print(variables)
				
				if len(variables) < len(used_variables):
					
					equation = transform_equation(lhs, rhs)
					print(equation)
					equation = equation.replace('=', '==')
					lhs, rhs = equation.split('==')
					print(lhs)
					print(rhs)
					equ = Eq(sympify(lhs), sympify(rhs))
					print(equ)
					variable = re.findall('[A-Za-zА-ЯЁа-яё]', lhs)
					print(variable)
					variables = [Symbol(name) for name in variable]
					print(variables)
					eq = expressions[0]
					print(variables)
					print(iter(variables))
					print(next(iter(variables)))
					first_var = next(iter(variables))
					# Автоматически определяем первые две переменные
					second_var = next(var for var in variables if var != first_var)
					print(first_var)
					print(second_var)
					# Используя все свободные символы
					collected_expr = equ.lhs.collect([first_var, second_var])
					print(collected_expr)
					collected_expr_str = str(collected_expr)
					collected_expr_str = collected_expr_str.replace(' ', '')
					if str(lhs) == collected_expr_str:
						
						a = collected_expr.coeff(first_var)  # Коэффициент при первой переменной
						b = collected_expr.coeff(second_var)  # Коэффициент при второй переменной
						c = -equ.rhs
						print(a)
						print(b)
						print(c)
					else:
						a = collected_expr.coeff(second_var)  # Коэффициент при первой переменной
						b = collected_expr.coeff(first_var)  # Коэффициент при второй переменной
						c = -equ.rhs
						print(a)
						print(b)
						print(c)
					# Строим график
					plot_linear_equation(a, b, c)
					return
				logging.info("Выбор пользователя: да, строить график.")
				eq = expressions[0]
				print(variables)
				print(iter(variables))
				print(next(iter(variables)))
				first_var = next(iter(variables))
				# Автоматически определяем первые две переменные
				second_var = next(var for var in variables if var != first_var)
				print(first_var)
				print(second_var)
				# Используя все свободные символы
				collected_expr = eq.lhs.collect([first_var, second_var])
				print(collected_expr)
				collected_expr_str = str(collected_expr)
				collected_expr_str = collected_expr_str.replace(' ', '')
				if str(lhs) == collected_expr_str:
					
					a = collected_expr.coeff(first_var)  # Коэффициент при первой переменной
					b = collected_expr.coeff(second_var)  # Коэффициент при второй переменной
					c = -eq.rhs
					print(a, b, c)
				else:
					a = collected_expr.coeff(second_var)  # Коэффициент при первой переменной
					b = collected_expr.coeff(first_var)  # Коэффициент при второй переменной
					c = -eq.rhs
					print(a, b, c)
				# Строим график
				plot_linear_equation(a, b, c)
				return
			else:
				logging.info("Выбор пользователя: нет, график не нужен.")
		
		# Решаем систему уравнений
		solution = solve(expressions, used_variables)
		logging.info(f"Решение системы уравнений: {solution}")
		
		if solution:
			# Применяем dynamic_precision к каждому значению
			
			numeric_dict = {var: dynamic_precision(sol) for var, sol in solution.items()}
			logging.info(f"Применение динамической точности: {numeric_dict}")
			
			# Форматируем результат для отображения
			formatted_result = ', '.join(f'{var}={val}' for var, val in numeric_dict.items())
			logging.info(f"Форматированный результат: {formatted_result}")
			add_to_history(equations_str, formatted_result)
			update_history()
			# Выводим решение
			label_system_of_equations.config(text=f"Решение системы уравнений:\n{formatted_result}")
		else:
			# Если решение не найдено
			label_system_of_equations.config(text="Решение не найдено.")
			update_history()
			logging.info("Решение не найдено.")
		clear_errors()
		clear_labels(label_system_of_equations)
	# Обновляем историю
	
	
	except Exception as e:
		handle_error(f"Ошибка: {e}\n", input_data=equations_str, function_name='solve_system_of_equations',
		             lb=label_system_of_equations)
		logging.error(f"Исключительная ситуация в solve_system_of_equations: {e}")


def variance(numbers):
	"""Вычисляет дисперсию списка чисел."""
	mean = sum(numbers) / len(numbers)
	squared_diffs = [(num - mean) ** 2 for num in numbers]
	return sum(squared_diffs) / len(numbers)


def calculate_statistics(stat_type):
	"""Вычисляет статистику набора чисел (среднее, медиана, минимум, максимум, размах, дисперсия)."""
	try:
		numbers = parse_numbers(entry_numbers.get())
		print(numbers)
		if not numbers:
			return
		if stat_type == "mean":
			mean = sum(numbers) / len(numbers)
			final_result = format_number(dynamic_precision(mean))
			label_stat_result.config(text=f"Среднее значение: {final_result}")
			add_to_history(", ".join(map(str, numbers)), f"Среднее значение: {final_result}")
		elif stat_type == "median":
			sorted_numbers = sorted(numbers)
			mid = len(sorted_numbers) // 2
			median = (sorted_numbers[mid] + sorted_numbers[-mid - 1]) / 2 if len(sorted_numbers) % 2 == 0 else \
				sorted_numbers[mid]
			final_result = format_number(dynamic_precision(median))
			label_stat_result.config(text=f"Медиана: {final_result}")
			add_to_history(", ".join(map(str, numbers)), f"Медиана: {final_result}")
		elif stat_type == "max":
			maximum = max(numbers)
			final_result = format_number(dynamic_precision(maximum))
			
			label_stat_result.config(text=f"Максимальное значение: {final_result}")
			add_to_history(", ".join(map(str, numbers)), f"Максимальное значение: {final_result}")
		elif stat_type == "min":
			minimum = min(numbers)
			final_result = format_number(dynamic_precision(minimum))
			
			label_stat_result.config(text=f"Минимальное значение: {final_result}")
			add_to_history(", ".join(map(str, numbers)), f"Минимальное значение: {final_result}")
		elif stat_type == "range":
			rng = max(numbers) - min(numbers)
			final_result = format_number(dynamic_precision(rng))
			
			label_stat_result.config(text=f"Размах: {final_result}")
			add_to_history(", ".join(map(str, numbers)), f"Размах: {final_result}")
		elif stat_type == "variance":
			var = variance(numbers)
			final_result = format_number(dynamic_precision(var))
			
			label_stat_result.config(text=f"Дисперсия: {final_result}")
			add_to_history(", ".join(map(str, numbers)), f"Дисперсия: {final_result}")
		else:
			raise ValueError(f"Неподдерживаемый тип статистики: {stat_type}")
		clear_errors()
		update_history()
		clear_labels(label_stat_result)
	except ValueError as ve:
		handle_error(f"Ошибка: {ve}", input_data=entry_numbers.get(), function_name='calculate_statistics')
	except Exception as e:
		handle_error(f"Ошибка: {e}", input_data=entry_numbers.get(), function_name='calculate_statistics',
		             lb=label_stat_result)


def dynamic_precision(value):
	getcontext().prec = 30
	
	if isinstance(value, (int, float)):
		decimal_value = Decimal(str(value))
		order = int(decimal_value.adjusted())
		rounded_value = decimal_value.normalize()
		precision = max(6, -order + 6)
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
		precision = max(2, -order + 2)
		logging.info(format(rounded_value, f'.{precision}f').rstrip('0').rstrip('.'))
		return format(rounded_value, f'.{precision}f').rstrip('0').rstrip('.')
	else:
		type_of = type(value)
		logging.info(f'Не опреден тип {type_of}')
		return value


def arithmetic_operation_fractions(first_fraction, second_fraction, operation):
	"""Производит арифметические операции с дробями."""
	try:
		frac1 = Fraction(first_fraction)
		frac2 = Fraction(second_fraction)
		if operation == "+":
			result = frac1 + frac2
		elif operation == "-":
			result = frac1 - frac2
		elif operation == "*":
			result = frac1 * frac2
		elif operation == "/":
			result = frac1 / frac2
		else:
			raise ValueError("Операция не поддерживается.")
		label_fractions_result.config(text=f"Результат: {result}")
		clear_errors()
		add_to_history(f"{frac1} {operation} {frac2}", result)
		update_history()
		clear_labels(label_fractions_result)
	except ZeroDivisionError:
		handle_error("Ошибка: деление на ноль.", input_data=(first_fraction, second_fraction),
		             function_name='arithmetic_operation_fractions')
	except ValueError as ve:
		handle_error(f"Ошибка: {ve}", input_data=(first_fraction, second_fraction),
		             function_name='arithmetic_operation_fractions')
	except Exception as e:
		handle_error(f"Ошибка: {e}", input_data=(first_fraction, second_fraction),
		             function_name='arithmetic_operation_fractions')


def clear_labels(lb):
	labels = [label_stat_result, trig_output, label_fractions_result, label_system_of_equations, label]
	for cll in labels:
		if cll != lb:
			cll.config(text='')


def process_trigonometric_function(function_type):
	"""Вычисляет тригонометрическую функцию указанного типа."""
	try:
		angle = float(trig_input.get())
		radians = math.radians(angle)
		if function_type == 'sin':
			result = math.sin(radians)
		elif function_type == 'cos':
			result = math.cos(radians)
		elif function_type == 'tan':
			result = math.tan(radians)
		else:
			raise ValueError(f"Неверный тип тригонометрической функции: {function_type}")
		final_result = format_number(dynamic_precision(result))
		trig_output.config(text=f"Результат: {final_result}")
		clear_errors()
		add_to_history(f"{function_type}({angle})", final_result)
		update_history()
		clear_labels(trig_output)
	except ValueError as ve:
		handle_error(f"Ошибка: {ve}", input_data=angle, function_name='process_trigonometric_function')
	except Exception as e:
		handle_error(f"Ошибка: {e}", input_data=angle, function_name='process_trigonometric_function')


def handle_error(error_message, input_data=None, function_name=None, lb=None):
	"""
	Функция для обработки ошибок с дополнительными параметрами.
	:param error_message: Сообщение об ошибке.
	:param input_data: Данные, введенные пользователем.
	:param function_name: Имя функции, в которой произошла ошибка.
	"""
	error_text.config(state="normal")
	error_text.delete(1.0, tk.END)
	
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
	if "not enough values to unpack (expected 2, got 1)" in error_message:
		full_error_message = "Ошибка: Вы не ввели знак '='. Пожалуйста, введите '=' и получите ответ."
	elif 'деление на ноль' in error_message:
		full_error_message = 'Ошибка: Вы реально поделили на ноль? Вы не знаете правило математики?!'
	elif "Sympify of expression 'could not parse" in error_message:
		full_error_message = 'Не выполняйте код'
	error_text.insert(tk.END, full_error_message)
	error_text.config(state="disabled")
	if lb:
		lb.config(text='Ошибка: взгляните на текстовое поле с ошибками')
	# Добавляем ошибку в историю
	global history
	history.append(("Ошибка:", full_error_message))
	update_history()


def add_to_history(expression, result):
	if str(result).startswith("Ошибка:"):
		# Очищаем запись об ошибке
		history.append((expression, str(result).split(":")[0]))
	else:
		# Формируем правильную запись с результатом
		history.append((expression, str(result)))


def update_history():
	history_text.config(state="normal")  # Временное разрешение редактирования
	history_text.delete(1.0, tk.END)  # Очищаем текущее содержимое
	for i, (expr, res) in enumerate(history):
		if str(res).startswith("Ошибка:"):
			history_text.insert(tk.END, f"{i + 1}. {res}\n")
		else:
			history_text.insert(tk.END, f"{i + 1}. {expr} = {res}\n")
	history_text.config(state="disabled")  # Возвращаем запрет редактирования
	history_text.see(tk.END)


def clear_errors():
	"""Очищает поле ошибок."""
	error_text.config(state="normal")
	error_text.delete(1.0, tk.END)
	error_text.config(state="disabled")


def clear_history():
	"""Очищает историю вычислений."""
	history.clear()
	label.config(text="")
	label_system_of_equations.config(text="")
	label_stat_result.config(text="")
	label_fractions_result.config(text="")
	trig_output.config(text="")
	update_history()


def check_first_run_and_show_tutorial_for_settings():
	try:
		with open("preferences2.txt", "r") as file:
			content = file.read().strip()
			is_first_run = content == "True"
			logging.info(f"Файл preferences2.txt прочитан: {content}, интерпретировано как: {is_first_run}")
	except FileNotFoundError:
		with open("preferences2.txt", "w") as file:
			file.write("True")
			logging.info("Файл preferences2.txt создан.")
		is_first_run = True
	except PermissionError:
		logging.error("Ошибка: не удается создать или прочитать файл preferences2.txt. Проверьте права доступа.")
		return
	
	if is_first_run:
		try:
			with open("preferences2.txt", "w") as file:
				file.write("False")
				# Если ключ отсутствует, задаем дефолтные значения
				bg_color = read_config()
				text_color = contrast_color(read_config())
				button_color = analogous_colors(read_config())
				entry_color = analogous_colors(read_config())
				
				# Применяем настройки к главному окну
				root.config(bg=bg_color)
				style = ttk.Style()  # Создаем экземпляр класса Style
				style.configure('.', background=bg_color, foreground=contrast_color(bg_color))
				style.configure('TLabel', background=bg_color, foreground=contrast_color(bg_color))
				style.configure('TButton', background=button_color, foreground=text_color)
				style.configure('TEntry', foreground=text_color, fieldbackground=entry_color,
				                insertbackground='black', selectforeground=text_color, selectbackground='gray')
				style.configure('Text', background=bg_color, foreground=contrast_color(bg_color))
				logging.info("Файл preferences2.txt обновлен.")
		except PermissionError:
			logging.error("Ошибка: не удается записать в файл preferences2.txt. Проверьте права доступа.")
	else:
		try:
			config = configparser.ConfigParser()
			config.read('config.ini')
			bg_color = config['Settings']['bg_color']
			text_color = config['Settings']['text_color']
			button_color = config['Settings']['button_color']
			entry_color = config['Settings']['entry_color']
			root.config(bg=bg_color)
			style = ttk.Style()  # Создаем экземпляр класса Style
			style.configure('.', background=bg_color, foreground=contrast_color(bg_color))
			style.configure('TLabel', background=bg_color, foreground=contrast_color(bg_color))
			style.configure('TButton', background=button_color, foreground=text_color)
			style.configure('TEntry', foreground=text_color, fieldbackground=entry_color,
			                insertbackground='black', selectforeground=text_color, selectbackground='gray')
			style.configure('Text', background=bg_color, foreground=contrast_color(bg_color))
		except KeyError:
			# Если ключ отсутствует, задаем дефолтные значения
			bg_color = read_config()
			text_color = contrast_color(read_config())
			button_color = analogous_colors(read_config())
			entry_color = analogous_colors(read_config())
			
			# Применяем настройки к главному окну
			root.config(bg=bg_color)
			style = ttk.Style()  # Создаем экземпляр класса Style
			style.configure('.', background=bg_color, foreground=contrast_color(bg_color))
			style.configure('TLabel', background=bg_color, foreground=contrast_color(bg_color))
			style.configure('TButton', background=button_color, foreground=text_color)
			style.configure('TEntry', foreground=text_color, fieldbackground=entry_color,
			                insertbackground='black', selectforeground=text_color, selectbackground='gray')
			style.configure('Text', background=bg_color, foreground=contrast_color(bg_color))


def settings_popup():
	check_first_run_and_show_tutorial_for_settings()
	try:
		config = configparser.ConfigParser()
		config.read('config.ini')
		bg_color = config['Settings']['bg_color']
		text_color = config['Settings']['text_color']
		button_color = config['Settings']['button_color']
		entry_color = config['Settings']['entry_color']
		root.config(bg=bg_color)
		style = ttk.Style()  # Создаем экземпляр класса Style
		style.configure('.', background=bg_color, foreground=contrast_color(bg_color))
		style.configure('TLabel', background=bg_color, foreground=contrast_color(bg_color))
		style.configure('TButton', background=button_color, foreground=text_color)
		style.configure('TEntry', foreground=text_color, fieldbackground=entry_color,
		                insertbackground='black', selectforeground=text_color, selectbackground='gray')
		style.configure('Text', background=bg_color, foreground=contrast_color(bg_color))
	
	except KeyError:
		# Если ключ отсутствует, задаем дефолтные значения
		bg_color = read_config()
		text_color = contrast_color(read_config())
		button_color = analogous_colors(read_config())
		entry_color = analogous_colors(read_config())
	settings_panel = SettingsPanel(root, root, bg_color, text_color, button_color, entry_color)
	# Загружаем начальные настройки
	settings_panel.load_settings(root, bg_color, text_color, button_color, entry_color)


def exit_program():
	"""Закрывает программу."""
	root.destroy()


def add_symbol(symbol):
	if symbol == '√':
		# Запрашиваем степень корня у пользователя
		n = simpledialog.askinteger("Степень корня", "Введите степень корня:")
		if n is not None:
			# Вставляем символ корня с указанием степени
			current_text = entry.get()
			entry.delete(0, tk.END)
			entry.insert(0, f"{current_text}{n}√")
	else:
		# Для других символов просто добавляем их в конец
		current_text = entry.get()
		entry.delete(0, tk.END)
		entry.insert(0, current_text + symbol)


def to_tg():
	webbrowser.open_new_tab("https://t.me/Ras_Kakulator_official")


import json


def save_history(filename):
	with open(filename, 'w') as file:
		json.dump(history, file)


def load_history(filename):
	try:
		with open(filename, 'r') as file:
			return json.load(file)
	except FileNotFoundError:
		return []


def form():
	webbrowser.open_new_tab("https://forms.yandex.ru/u/6861698d84227cbab5e787ba")


# Создаем главное окно
with open("logs.log", "w") as log:
	log.write("")
root = tk.Tk()
root.title("Расширенный Калькулятор")
root.geometry("1000x1000")
style = ttk.Style()
style.theme_use('default')
check_first_run_and_show_tutorial(root)
# Читаем выбранный цвет из конфигурации


# Применяем начальную тему
initial_bg_color = read_config()
apply_theme(root, initial_bg_color)
# Общий код калькулятора
try:
	with open("preferences2.txt", "r") as file:
		content = file.read().strip()
		is_first_run = content == "True"
		logging.info(f"Файл preferences2.txt прочитан: {content}, интерпретировано как: {is_first_run}")
except FileNotFoundError:
	with open("preferences2.txt", "w") as file:
		file.write("True")
		logging.info("Файл preferences2.txt создан.")
	is_first_run = True

else:
	config = configparser.ConfigParser()
	config.read('config.ini')
	
	try:
		bg_color = config['Settings']['bg_color']
		text_color = config['Settings']['text_color']
		button_color = config['Settings']['button_color']
		entry_color = config['Settings']['entry_color']
	except KeyError:
		# Если ключ отсутствует, задаем дефолтные значения
		bg_color = read_config()
		text_color = contrast_color(read_config())
		button_color = analogous_colors(read_config())
		entry_color = analogous_colors(read_config())
	
	# Применяем настройки к главному окну
	root.config(bg=bg_color)
	style = ttk.Style()  # Создаем экземпляр класса Style
	style.configure('.', background=bg_color, foreground=contrast_color(bg_color))
	style.configure('TLabel', background=bg_color, foreground=text_color)
	style.configure('TButton', background=button_color, foreground=text_color)
	style.configure('TEntry', foreground=text_color, fieldbackground=entry_color,
	                insertbackground='black', selectforeground=text_color, selectbackground='gray')
	style.configure('Text', background=bg_color, foreground=contrast_color(bg_color))
# Загружаем изображение
img = Image.open("settings_icon.png")
# Масштабируем изображение
scaled_img = img.resize((30, 30), Image.Resampling.LANCZOS)
# Конвертируем в PhotoImage
settings_icon = ImageTk.PhotoImage(scaled_img)

settings_button = ttk.Button(root, image=settings_icon, command=settings_popup)
settings_button.place(x=955, y=0)
label_basic_calc_text = ttk.Label(root, text="Введите числовое выражение (2+2):")
label_basic_calc_text.place(x=0, y=0)
help_button = ttk.Button(root, text='справка', command=lambda: show_tutorial("Помощь",
                                                                             
                                                                             "Помощь по калькулятору!\n\n"
                                                                             "Здесь вы можете решать уравнения, посчитать среднее арифметическое "
                                                                             "Медиану, дисперсию и это только малая часть функций\n"
                                                                             "Для вычисления факториала напишите 'число!'\n"
                                                                             "В уравнениях писать систему через пробел\n"
                                                                             "Пожалуйста, не делайте вычисления с корнем пока это не поддерживаеться\n\n"
                                                                             "Если возникнут вопросы или получили ошибку, пишите на email: mastersoftkompany@mail.ru"
                                                                             ))
help_button.place(x=930, y=55)
entry = ttk.Entry(root, width=35)
entry.place(x=0, y=20)
entry.bind("<Return>", calculate)

button_calc = ttk.Button(root, text="Вычислить")
button_calc.bind("<Button-1>", calculate)
button_calc.place(x=216, y=15)
button_cor = ttk.Button(root, text='√', command=lambda: add_symbol("√"))
button_cor.place(x=296, y=15)
label = ttk.Label(root, text="", font=("Helvetica", 12))
label.place(x=0, y=40)

label_system_of_equations_text = ttk.Label(root, text="Введите систему уравнений (через пробел):")
label_system_of_equations_text.place(x=0, y=60)

entry_system_of_equations = ttk.Entry(root, width=50)
entry_system_of_equations.place(x=0, y=80)
entry_system_of_equations.bind("<Return>", solve_system_of_equations)
button_system_of_equations = ttk.Button(root, text="Решить систему уравнений")
button_system_of_equations.config(command=solve_system_of_equations)
button_system_of_equations.place(x=305, y=80)

label_system_of_equations = ttk.Label(root, text="", font=("Helvetica", 12))
label_system_of_equations.place(x=0, y=105)

label_number_entry = ttk.Label(root, text="Введите числа через пробел:")
label_number_entry.place(x=0, y=145)

entry_numbers = ttk.Entry(root, width=50)
entry_numbers.place(x=0, y=165)

button_mean = ttk.Button(root, text="Среднее значение", command=lambda: calculate_statistics("mean"))
button_mean.place(x=305, y=160)

button_median = ttk.Button(root, text="Медиана", command=lambda: calculate_statistics("median"))
button_median.place(x=418, y=160)

button_max = ttk.Button(root, text="Максимум", command=lambda: calculate_statistics("max"))
button_max.place(x=484, y=160)

button_min = ttk.Button(root, text="Минимум", command=lambda: calculate_statistics("min"))
button_min.place(x=556, y=160)

button_range = ttk.Button(root, text="Размах", command=lambda: calculate_statistics("range"))
button_range.place(x=624, y=160)

button_variance = ttk.Button(root, text="Дисперсия", command=lambda: calculate_statistics("variance"))
button_variance.place(x=690, y=160)

button_exit = ttk.Button(root, text="Выход", command=exit_program)
button_exit.place(x=930, y=85)

label_stat_result = ttk.Label(root, text="", font=("Helvetica", 12))
label_stat_result.place(x=0, y=200)
label_of_errors = ttk.Label(root, text='Поле с ошибками при вычислении')
label_of_errors.place(x=0, y=380)
# Исправление ошибки: используем стандартный виджет Text из tkinter
error_frame = ttk.Frame(root)
error_frame.place(x=0, y=400)

scrollbar_error = ttk.Scrollbar(error_frame)
scrollbar_error.pack(side=tk.RIGHT, fill=tk.Y)

error_text = tk.Text(error_frame, height=5, width=80, yscrollcommand=scrollbar_error.set, state="disabled")
error_text.pack(side=tk.LEFT, fill=tk.BOTH)
scrollbar_error.config(command=error_text.yview)

label_fractions_text = ttk.Label(root, text="Арифметика дробей:")
label_fractions_text.place(x=0, y=290)

entry_first_fraction = ttk.Entry(root, width=20)
entry_first_fraction.place(x=0, y=310)

entry_second_fraction = ttk.Entry(root, width=20)
entry_second_fraction.place(x=185, y=310)

operator_choices = ['+', '-', '*', '/']
operator_variable = tk.StringVar(root)
operator_variable.set('+')

operator_dropdown = ttk.OptionMenu(root, operator_variable, *operator_choices)
operator_dropdown.place(x=125, y=310)

button_fractions_calculate = ttk.Button(root, text="Выполнить операцию",
                                        command=lambda: arithmetic_operation_fractions(entry_first_fraction.get(),
                                                                                       entry_second_fraction.get(),
                                                                                       operator_variable.get()))
button_fractions_calculate.place(x=0, y=338)

label_fractions_result = ttk.Label(root, text="", font=("Helvetica", 11))
label_fractions_result.place(x=0, y=363)

history_frame = ttk.Frame(root)
history_frame.place(x=0, y=530)

scrollbar_history = ttk.Scrollbar(history_frame)
scrollbar_history.pack(side=tk.RIGHT, fill=tk.Y)

history_text = tk.Text(history_frame, height=10, width=80, yscrollcommand=scrollbar_history.set, state="disabled")
history_text.pack(side=tk.LEFT, fill=tk.BOTH)
scrollbar_history.config(command=history_text.yview)
cl_b = ttk.Button(root, text="Очистить историю", command=clear_history)
cl_b.place(x=680, y=530)
cord_x = 0
cord_y = 220
label_trig_text = ttk.Label(root, text="Введите угол синус, косинус или тангенс которого вы хотите найти:")
label_trig_text.place(x=cord_x, y=cord_y)

trig_input = ttk.Entry(root, width=20)
trig_input.place(x=cord_x, y=cord_y + 20)

sin_button = ttk.Button(root, text="sin", command=lambda: process_trigonometric_function('sin'))
sin_button.place(x=cord_x, y=cord_y + 40)

cos_button = ttk.Button(root, text="cos", command=lambda: process_trigonometric_function('cos'))
cos_button.place(x=cord_x + 100, y=cord_y + 40)

tan_button = ttk.Button(root, text="tan", command=lambda: process_trigonometric_function('tan'))
tan_button.place(x=cord_x + 200, y=cord_y + 40)

trig_output = ttk.Label(root, text="", font=("Helvetica", 12))
trig_output.place(x=cord_x + 124, y=cord_y + 20)

tgb = ttk.Button(root, text='Перейти в официальный тгк Калькулятора', command=to_tg)
tgb.place(x=750, y=115)

form_btn = ttk.Button(root, text='Собщить об ошибке', command=form)
form_btn.place(x=870, y=150)
root.mainloop()