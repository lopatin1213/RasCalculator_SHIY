import addings
from sympy import *
import numpy as np
import matplotlib.pyplot as plt
import logging
import re
import sympy

def get_all_sympy_function_names():
    """Собирает имена всех встроенных функций и констант SymPy."""
    names = set()

    # Сбор функций (как и раньше)
    def collect(module):
        for attr_name in dir(module):
            if attr_name.startswith('_'):
                continue
            try:
                attr = getattr(module, attr_name)
            except Exception:
                continue
            if callable(attr) or isinstance(attr, type):
                names.add(attr_name)
            elif hasattr(attr, '__module__') and 'sympy.functions' in getattr(attr, '__module__', ''):
                collect(attr)
    collect(sympy.functions)

    # Сбор констант (новое!)
    for name in dir(sympy):
        if name.startswith('_'):
            continue
        try:
            obj = getattr(sympy, name)
        except Exception:
            continue
        # Проверяем, что это константа, а не функция или класс
        if hasattr(obj, 'is_constant') and obj.is_constant:
            if not callable(obj) and not isinstance(obj, type):
                names.add(name)

    # Твои любимые ручные дополнения
    names.update(['sqrt', 'log', 'ln', 'Abs', 'sign', 'floor', 'ceiling'])
    return names

def insert_multiplication_signs(expr: str, extra_functions=None) -> str:
    """
    Вставляет знаки умножения с учётом неявного умножения.
    Поддерживает латиницу и кириллицу в именах переменных.
    Защищает все известные SymPy-функции и константы от разбиения.
    """
    func_set = get_all_sympy_function_names()  # теперь там и функции, и константы
    if extra_functions:
        func_set.update(extra_functions)

    sorted_funcs = sorted(func_set, key=len, reverse=True)
    func_pattern = '|'.join(re.escape(f) for f in sorted_funcs)

    LETTER = r'[A-Za-zА-Яа-яёЁ_]'
    LETTER_DIGIT = r'[\dA-Za-zА-Яа-яёЁ_]'

    # === ШАГ 1: Защита известных имён (функций и констант) ===
    protected = {}
    def protect_known(match):
        name = match.group(0)
        if name not in func_set:
            return name
        placeholder = f'\ue000{len(protected)}\ue001'
        protected[placeholder] = name
        return placeholder

    expr = re.sub(r'[A-Za-z_]\w*', protect_known, expr)

    # === ШАГ 2: Правила вставки умножения ===
    # Явно вставляем * между цифрой/буквой и известным именем перед '('
    expr = re.sub(rf'(\d)({func_pattern})(?=\()', r'\1*\2', expr)
    expr = re.sub(rf'({LETTER})({func_pattern})(?=\()', r'\1*\2', expr)

    # Основные правила с кириллицей
    expr = re.sub(rf'(\d)({LETTER})', r'\1*\2', expr)                # 2x, 2я
    # РАЗРЫВАЕМ ВСЕ ЦЕПОЧКИ БУКВ (кроме защищённых имён)
    expr = re.sub(rf'({LETTER})(?={LETTER})', r'\1*', expr)         # a*b*c, а*я
    expr = re.sub(rf'({LETTER_DIGIT})(\()', r'\1*\2', expr)         # a(, 3(, я(
    expr = re.sub(rf'(\))({LETTER_DIGIT}\()', r'\1*\2', expr)       # )a, )(, )я

    # === ШАГ 3: Возвращаем защищённые имена на место ===
    for placeholder, name in protected.items():
        expr = expr.replace(placeholder, name)

    return expr
def plot_linear_equation(a, b, c):
    """
    Строит график линейного уравнения ax + by + c = 0.
    """
    try:
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
    except Exception as e:
        raise Exception(e)


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
    
    transformed_eq = f"-{k}*{x}+{y}={b}"
    return transformed_eq

from PyQt6.QtWidgets import QMessageBox
def solve_system_of_equations(window):
    try:
        # Получаем уравнения из поля ввода
        equations_str = window.entry.text()
        logging.info(f"Полученная строка уравнений: {equations_str}")
        if equations_str == "":
            return
        # Проверяем наличие запятых в строке
        
        # Разбиение строки на отдельные уравнения
        equations_list = equations_str.split(' ')
        logging.info(f"Разбито на уравнения: {equations_list}")
        
        # Преобразование уравнений в объекты Sympy
        expressions = []
        used_variables = set()  # Множество переменных, используемых в уравнениях
        for equation in equations_list:
            logging.info(f"Преобразование уравнения: {equation}")
            equation = equation.replace('=', '==')
            equation = insert_multiplication_signs(equation)
            print(equation)
            lhs, rhs = equation.split('==')
            logging.info(str(lhs))
            logging.info(str(rhs))
            expressions.append(Eq(sympify(lhs), sympify(rhs)))
            logging.info(f"Добавлено уравнение: {expressions[-1]}")
            
            # Определяем переменные, участвующие в текущем уравнении
            used_variables.update(list(expressions[-1].free_symbols))
        
        logging.info(f"Переменные, задействованные в уравнениях: {used_variables}")
        
        # Проверка на недоопределённость системы
        if len(expressions) < len(used_variables) <= 2:
            logging.info("Количество уравнений меньше количества переменных, система недоопределена.")
            response = QMessageBox.question(None,
                                            'Выбор',
                                            'Бесконечное количество решений.\nВы хотите увидеть график или уравнение функции?',
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            logging.info(str(response))
            if response == QMessageBox.StandardButton.Yes:
                variable = re.findall('[A-Za-zА-ЯЁа-яё]', lhs)
                
                logging.info(str(variable))
                variables = [Symbol(name) for name in variable]
                logging.info(str(variables))
                
                if len(variables) < len(used_variables):
                    
                    equation = transform_equation(lhs, rhs)
                    logging.info(str(equation))
                    equation = equation.replace('=', '==')
                    lhs, rhs = equation.split('==')
                    logging.info(str(lhs))
                    logging.info(str(rhs))
                    equ = Eq(sympify(lhs), sympify(rhs))
                    logging.info(str(equ))
                    variable = re.findall('[A-Za-zА-ЯЁа-яё]', lhs)
                    logging.info(variable)
                    variables = [Symbol(name) for name in variable]
                    logging.info(str(variables))
                    eq = expressions[0]
                    logging.info(str(variables))
                    logging.info(str(iter(variables)))
                    logging.info(str(next(iter(variables))))
                    first_var = next(iter(variables))
                    # Автоматически определяем первые две переменные
                    second_var = next(var for var in variables if var != first_var)
                    logging.info(str(first_var))
                    logging.info(str(second_var))
                    # Используя все свободные символы
                    collected_expr = equ.lhs.collect([first_var, second_var])
                    logging.info(str(collected_expr))
                    collected_expr_str = str(collected_expr)
                    collected_expr_str = collected_expr_str.replace(' ', '')
                    if str(lhs) == collected_expr_str:
                        
                        a = collected_expr.coeff(first_var)  # Коэффициент при первой переменной
                        b = collected_expr.coeff(second_var)  # Коэффициент при второй переменной
                        c = -equ.rhs
                        logging.info(str(a))
                        logging.info(str(b))
                        logging.info(str(c))
                    else:
                        a = collected_expr.coeff(second_var)  # Коэффициент при первой переменной
                        b = collected_expr.coeff(first_var)  # Коэффициент при второй переменной
                        c = -equ.rhs
                        logging.info(str(a))
                        logging.info(str(b))
                        logging.info(str(c))
                    # Строим график
                    plot_linear_equation(a, b, c)
                    return
                logging.info("Выбор пользователя: да, строить график.")
                eq = expressions[0]
                if len(variables) > len(used_variables):
                    print("Длина больше чем в sympy")
                    for i in range(3):
                        for variable in variables:
                            if variable not in used_variables:
                                print(variable)
                                variables.remove(variable)
                logging.info(str(variables))
                logging.info(str(iter(variables)))
                logging.info(str(next(iter(variables))))
                first_var = next(iter(variables))
                # Автоматически определяем первые две переменные
                second_var = next(var for var in variables if var != first_var)
                logging.info(str(first_var))
                logging.info(str(second_var))
                # Используя все свободные символы
                collected_expr = eq.lhs.collect([first_var, second_var])
                logging.info(str(collected_expr))
                collected_expr_str = str(collected_expr)
                collected_expr_str = collected_expr_str.replace(' ', '')
                if str(lhs) == collected_expr_str:
                    
                    a = collected_expr.coeff(first_var)  # Коэффициент при первой переменной
                    b = collected_expr.coeff(second_var)  # Коэффициент при второй переменной
                    c = -eq.rhs
                    logging.info(f"{a}, {b}, {c}")
                else:
                    a = collected_expr.coeff(second_var)  # Коэффициент при первой переменной
                    b = collected_expr.coeff(first_var)  # Коэффициент при второй переменной
                    c = -eq.rhs
                    logging.info(f"{a}, {b}, {c}")
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
            logging.info(str(solution))
            if isinstance(solution, list):
                num = []  # Список для хранения результирующих словарей
                
                for x in solution:
                    # Применяем точность к каждому решению
                    numeric_dict = {var: addings.dynamic_precision(sol.evalf()) for var, sol in x.items()}
                    
                    # Добавляем полученный словарь в список
                    num.append(numeric_dict)
                
                # Теперь мы имеем список словарей в переменной num
                # Нам нужно объединить их в единую строку формата "var=value"
                results = []
                for dct in num:
                    # Для каждого словаря создадим строки вида "var=value"
                    for var, val in dct.items():
                        results.append(f"{var}={val}")
                
                # Объединяем все полученные строки в одну общую строку
                formatted_result = ", ".join(results)
                
                logging.info(str(formatted_result))
            else:
                numeric_dict = {var: addings.dynamic_precision(sol.evalf()) for var, sol in solution.items()}
                logging.info(f"Применение динамической точности: {numeric_dict}")
                
                # Форматируем результат для отображения
                formatted_result = ', '.join(f'{var}={val}' for var, val in numeric_dict.items())
            logging.info(f"Форматированный результат: {formatted_result}")
            
            
            # Выводим решение
            window.label_system_of_equations.setText(f"Решение системы уравнений:\n{formatted_result}")
        else:
            # Если решение не найдено
            window.label_system_of_equations.setText("Решение не найдено.")
            
            
            logging.info("Решение не найдено.")
        
    
    # Обновляем историю
    
    except Exception as e:
        logging.error(str(e))
        addings.handle_error(str(e), input_data=window.entry.text(), function_name="solve_system_of_equations")
        logging.error(f"Исключительная ситуация в solve_system_of_equations: {e}")

