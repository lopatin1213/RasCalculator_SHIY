import addings
from sympy import *
import numpy as np
import matplotlib.pyplot as plt
import logging
import re
import sympy

def get_all_sympy_function_names():
    """Собирает имена всех встроенных функций и констант SymPy."""
    names = set(sympy.__all__)
    print(names)
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
    print(expr)
    expr = re.sub(r'[A-Za-z_]\w*', protect_known, expr)
    print(expr)
    # === ШАГ 2: Правила вставки умножения ===
    expr = re.sub(rf'(\d+)(\ue000\d+\ue001)(?=\()', r'\1*\2', expr)
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


def plot_equation(eq, var1, var2):

    try:
        def has_odz(expr, var):
            """
            Проверяет, есть ли у выражения ограничения на область допустимых значений (ОДЗ).
            Если есть - лучше рисовать через plot_implicit.
            """
            # 1. Проверяем наличие нелинейных функций с ограничениями (log, sqrt, asin, acos)
            # В SymPy log и ln — одно и то же.
            if expr.has(log) or expr.has(sqrt) or expr.has(asin) or expr.has(acos):
                return True

            # 2. Проверяем, есть ли переменная в знаменателе (деление на ноль)
            numer, denom = expr.as_numer_denom()
            if var in denom.free_symbols:
                return True

            return False

        # ================================
        # Добавляем поддержку Ctrl+ / Ctrl- для зума
        # ================================
        def zoom_key_handler(event):
            # Проверяем, что нажатие произошло на оси и это сочетание с Ctrl
            if event.inaxes != ax:
                return

            # Коэффициент масштабирования (1.2 = 120%, 0.8 = 80%)
            scale_factor = 1.2

            # Получаем текущие границы
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            # Вычисляем центр текущего обзора
            x_center = (cur_xlim[0] + cur_xlim[1]) / 2
            y_center = (cur_ylim[0] + cur_ylim[1]) / 2

            # Длина текущего диапазона
            cur_xrange = cur_xlim[1] - cur_xlim[0]
            cur_yrange = cur_ylim[1] - cur_ylim[0]
            #print(event.key)
            # Если нажато Ctrl + (или Ctrl + =) — приближаем
            if event.key == 'ctrl+plus' or event.key == 'ctrl+equal' or event.key == 'ctrl+=' or event.key == 'ctrl++':
                new_xrange = cur_xrange / scale_factor
                new_yrange = cur_yrange / scale_factor
            # Если нажато Ctrl - — отдаляем
            elif event.key == 'ctrl+minus' or event.key == 'ctrl+-':
                new_xrange = cur_xrange * scale_factor
                new_yrange = cur_yrange * scale_factor
            else:
                return  # Если нажата другая клавиша, ничего не делаем

            # Устанавливаем новые границы, центрируя обзор
            ax.set_xlim([x_center - new_xrange / 2, x_center + new_xrange / 2])
            ax.set_ylim([y_center - new_yrange / 2, y_center + new_yrange / 2])

            # Принудительно перерисовываем график
            event.canvas.draw_idle()

        # Подключаем обработчик к фигуре

        # ================================
        expr = eq.lhs - eq.rhs
        vars_list = sorted(eq.free_symbols, key=lambda s: str(s))
        var1, var2 = vars_list[0], vars_list[1]
        # === 1. Безопасный поиск пересечений (ловит ошибки abs) ===
        x_intercepts = []
        y_intercepts = []
        try:
            x_sol = solve(expr.subs(var2, 0), var1)
            x_intercepts = [float(s) for s in x_sol if s.is_real]
        except Exception:
            pass # Если sympy не может решить (abs), пропускаем

        try:
            y_sol = solve(expr.subs(var1, 0), var2)
            y_intercepts = [float(s) for s in y_sol if s.is_real]
        except Exception:
            pass
        limit = 1000
        # === 2. Увеличиваем разрешение для гладкости (было 500, стало 1000) ===
        if has_odz(expr, var1):
            from sympy.plotting import plot_implicit
            p = plot_implicit(eq, (var1, -100, 100), (var2, -100, 100), show=False, n=1300, depth=9)

            p.process_series()  # Отрисовываем линию
            ax = p.ax
            fig = p.fig
            fig.canvas.mpl_connect('key_press_event', zoom_key_handler)
            x_coords_str = ", ".join([f"({x:.2f}, 0)" for x in x_intercepts]) if x_intercepts else "Нет"
            y_coords_str = ", ".join([f"(0, {y:.2f})" for y in y_intercepts]) if y_intercepts else "Нет"

            # Три пустые линии для легенды (они не видны на графике, но создают текст в легенде)
            ax.plot([], [], ' ', label=f"${latex(eq)}$")  # Красивое уравнение через LaTeX
            ax.plot([], [], ' ', label=f"Пересечения с X: {x_coords_str}")  # Текст про X
            ax.plot([], [], ' ', label=f"Пересечения с Y: {y_coords_str}")  # Текст про Y

            # === ДОБАВЛЯЕМ ТОЛЩИНУ ЛИНИИ ===
            patches = ax.patches

            for patch in patches:
                # Устанавливаем толщину границы (в пунктах, например 4)
                patch.set_linewidth(2)

                # ================================

            # Дальше твой код с точками и оформлением...
            try:
                x_intercepts, y_intercepts = [], []
                try:
                    x_sol = solve(expr.subs(var2, 0), var1)
                    x_intercepts = [float(s) for s in x_sol if s.is_real]
                    for x in x_intercepts: ax.scatter(x, 0, s=60, color='red', marker='o', zorder=5)
                except:
                    pass
                try:
                    y_sol = solve(expr.subs(var1, 0), var2)
                    y_intercepts = [float(s) for s in y_sol if s.is_real]
                    for y in y_intercepts: ax.scatter(0, y, s=60, color='blue', marker='o', zorder=5)
                except:
                    pass

                ax.axhline(0, color='black', linewidth=1)
                ax.axvline(0, color='black', linewidth=1)
                ax.set_xlim(-20, 20)
                ax.set_ylim(-20, 20)
                ax.set_xlabel(str(var1))
                ax.set_ylabel(str(var2))
                ax.legend()
                ax.set_autoscale_on(False)
                ax.grid(True, linestyle='--', alpha=0.7)
            except Exception as e:
                logging.warning(f"Ошибка при добавлении оформления на p.ax: {e}")

            p.fig.tight_layout()
            p.plt.show()
            return
        else:

            x_vals = np.linspace(-limit, limit, 10000)
            y_vals = np.linspace(-limit, limit, 10000)
            y_vals[~np.isfinite(y_vals)] = np.nan
            X, Y = np.meshgrid(x_vals, y_vals)
            f = lambdify((var1, var2), expr, modules='numpy')
            #print(x_vals, y_vals, X, Y, f, sep='\n<------------------------------->\n')
            Z = f(X, Y)
            #print(Z)
            fig, ax = plt.subplots()
            x_coords_str = ", ".join([f"({x:.2f}, 0)" for x in x_intercepts]) if x_intercepts else "Нет"
            y_coords_str = ", ".join([f"(0, {y:.2f})" for y in y_intercepts]) if y_intercepts else "Нет"
            ax.contour(X, Y, Z, levels=[0], colors='blue', linewidths=2)

            ax.plot([], [], ' ', label=f"Уравнение: ${latex(eq)}$")
            fig.canvas.mpl_connect('key_press_event', zoom_key_handler)

            # Оси X и Y
            ax.axhline(0, color='black', linewidth=1)
            ax.axvline(0, color='black', linewidth=1)

            # Точки пересечения (теперь они не вызовут ошибку, если не найдутся)
            ax.scatter([x for x in x_intercepts], [0] * len(x_intercepts), s=60, color='red', marker='o', zorder=5,
                       label=f"Пересечения с X: {x_coords_str}")

            ax.scatter([0] * len(y_intercepts), [y for y in y_intercepts], s=60, color='blue', marker='o', zorder=5,
                       label=f"Пересечения с Y: {y_coords_str}")

            # Подписи осей строго по переменным
            ax.set_xlabel(str(var1))
            ax.set_ylabel(str(var2))
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.set_xlim(-20.0, 20.0)
            ax.set_ylim(-20.0, 20.0)
            ax.legend()
            ax.set_autoscale_on(False)
            plt.show()

    except Exception as e1:
        logging.warning(f"Matplotlib contour не сработал: {e1}")
        # Если контур упал (сингулярности), используем sympy.plot_implicit
        from sympy.plotting import plot_implicit
        p = plot_implicit(eq, (var1, -10, 10), (var2, -10, 10), show=False)
        p.show()

import re
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
            #equation = equation.replace('=', '==')
            equation = insert_multiplication_signs(equation)
            print(equation)
            lhs, rhs = equation.split('=')
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

            # Диалог (оставляем, как ты просил)
            response = QMessageBox.question(None,
                                            'Выбор',
                                            'Бесконечное количество решений.\nВы хотите увидеть график или уравнение функции?',
                                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if response == QMessageBox.StandardButton.Yes:
                # Строим график для первого уравнения
                eq = expressions[0]
                vars_list = list(eq.free_symbols)

                if len(vars_list) == 2:
                    var1, var2 = vars_list[0], vars_list[1]
                    plot_equation(eq, var1, var2)
                    return
                else:
                    window.label_system_of_equations.setText("Невозможно построить 2D-график (переменных больше двух).")
                    return
            else:
                logging.info("Выбор пользователя: нет, график не нужен.")

        
        # Решаем систему уравнений
        solution = solve(expressions, used_variables)
        logging.info(f"Решение системы уравнений: {solution}")
        comment = None
        if solution:
            # Применяем dynamic_precision к каждому значению
            logging.info(str(solution))
            if isinstance(solution, list):
                num = []  # Список для хранения результирующих словарей

                for x in solution:

                    sol1 = list(x.values())[0]
                    if 'I' in str(sol1):
                        comment = f"Но решения содержат комплексные числа (имеют I), если ты школьник, то пропусти их"
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
            if comment:
                window.label_system_of_equations.setText(f"Решение системы уравнений:\n{formatted_result}, {comment}")
            else:
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

