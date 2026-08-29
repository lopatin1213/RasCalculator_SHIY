import addings
from sympy import *
import logging

import re
import sympy


def get_all_sympy_function_names():
    """Собирает имена всех встроенных функций и констант SymPy."""
    names = set(sympy.__all__)
    # print(names)
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
    expr = re.sub(rf'(\d+)(\ue000\d+\ue001)(?=\()', r'\1*\2', expr)
    # Явно вставляем * между цифрой/буквой и известным именем перед '('
    expr = re.sub(rf'(\d)({func_pattern})(?=\()', r'\1*\2', expr)
    expr = re.sub(rf'({LETTER})({func_pattern})(?=\()', r'\1*\2', expr)

    # Основные правила с кириллицей
    expr = re.sub(rf'(\d)({LETTER})', r'\1*\2', expr)  # 2x, 2я
    # РАЗРЫВАЕМ ВСЕ ЦЕПОЧКИ БУКВ (кроме защищённых имён)
    expr = re.sub(rf'({LETTER})(?={LETTER})', r'\1*', expr)  # a*b*c, а*я
    expr = re.sub(rf'({LETTER_DIGIT})(\()', r'\1*\2', expr)  # a(, 3(, я(
    expr = re.sub(rf'(\))({LETTER_DIGIT}\()', r'\1*\2', expr)  # )a, )(, )я
   # Вставляем * между цифрой и защищённым именем (константы, переменные)
    expr = re.sub(rf'(\d)(\ue000\d+\ue001)', r'\1*\2', expr)

    # === ШАГ 3: Возвращаем защищённые имена на место ===
    for placeholder, name in protected.items():
        expr = expr.replace(placeholder, name)

    return expr



import re
from PyQt6.QtWidgets import QMessageBox
from adopt_plot import AdoptPlot
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
        used_variables = list()  # Множество переменных, используемых в уравнениях
        for equation in equations_list:
            logging.info(f"Преобразование уравнения: {equation}")

            equation = equation.replace('=', '==')

            equation = insert_multiplication_signs(equation)
            print(equation)
            try:
                lhs, rhs = equation.split('==')
                logging.info(str(lhs))
                logging.info(str(rhs))
            except ValueError:
                return 'А знак равно ("=") ты забыл? Я не умею читать мысли чему равна вторая часть уравнения'
            expressions.append(Eq(sympify(lhs), sympify(rhs)))
            logging.info(f"Добавлено уравнение: {expressions[-1]}")

            # Определяем переменные, участвующие в текущем уравнении
            list2 = expressions[-1].free_symbols
            used_variables.extend(x for x in list2 if x not in used_variables)

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
                plt = AdoptPlot(equations_str, limit=300, n=10000)
            else:
                logging.info("Выбор пользователя: нет, график не нужен.")

        solution = nonlinsolve(expressions, used_variables)
        logging.info(f"Решение системы уравнений: {solution}")

        if solution != S.EmptySet:
            # Применяем dynamic_precision к каждому значению
            if not solution.has(ConditionSet) and not solution.has(ImageSet):
                logging.info(str(solution))
                num = []
                for sol in solution:
                    for i in range(0, len(used_variables)):
                        logging.info(f"{used_variables[i]} = {sol[i]}")
                        var = used_variables[i]
                        numeric_dict = {var: addings.dynamic_precision(sol[i].evalf())}
                        logging.info(f"{numeric_dict}")
                        # Добавляем полученный словарь в список
                        num.append(numeric_dict)

                # Теперь мы имеем список словарей в переменной num
                # Нам нужно объединить их в единую строку формата "var=value"
                results = []
                for dct in num:
                    # Для каждого словаря создадим строки вида "var=value"
                    for var, val in dct.items():
                        logging.info(f"{var}, {val}")
                        results.append(f"{var}={val}")

                # Объединяем все полученные строки в одну общую строку
                formatted_result = ", ".join(results)

                logging.info(str(formatted_result))
                # Выводим решение

                window.label_system_of_equations.setText(f"Решение системы уравнений:\n{formatted_result}")
            elif solution.has(ImageSet):
                for sol in solution:
                    for so in sol:
                        for s in so.args:

                            # 2. Достаем лямбда-выражение (функцию)
                            lambda_expr = s.lamda
                            # Lambda(n, n*pi)

                            # 3. Достаем саму формулу (n*pi)
                            formula = lambda_expr.expr
                            # n*pi

                            # 4. Достаем переменную, которая крутится в формуле (n)
                            variable = lambda_expr.variables[0]
                            # n

                            # 5. Достаем базовое множество (Integers)
                            base_set = s.base_sets[0]
                            # Integers
                            window.label_system_of_equations.setText(f"x = {formula}, где {variable} — {base_set}")
            else:
                for sol in solution:
                    for s in sol:
                        core_equation = s.condition.lhs - s.condition.rhs

                        # Проверяем, в каких числах искали
                        if s.base_set == S.Reals:
                            area_text = "действительных числах"
                        elif s.base_set == S.Complexes:
                            area_text = "комплексных числах"
                        else:
                            area_text = str(s.base_set)

                        # Формируем понятное сообщение для пользователя
                        window.label_system_of_equations.setText(
                            f"Уравнение {core_equation} = 0 не имеет аналитического решения "
                            f"в {area_text}. Ответ может быть найден только численно."
                        )
        else:
            # Если решение не найдено
            window.label_system_of_equations.setText("Решение не найдено.")
            
            
            logging.info("Решение не найдено.")
        
    
    # Обновляем историю
    
    except Exception as e:
        logging.error(str(e))
        addings.handle_error(str(e), input_data=window.entry.text(), function_name="solve_system_of_equations")
        logging.error(f"Исключительная ситуация в solve_system_of_equations: {e}")

