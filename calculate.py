from sympy import *
import addings
from fractions import Fraction
import math
import logging
from decimal import Decimal, getcontext
import re
def replace_caret_with_power(expression):
    """Заменяет символ ^ на оператор возведения в степень (**)."""
    return expression.replace('^', '**')


def replace_z_t(expression):
    def repl(match):
        return match.group(0).replace(',', '.')
    # Паттерн: цифра, запятая, цифра (возможно с дополнительными цифрами)
    pattern = r'(\d+),(\d+)'
    return re.sub(pattern, repl, expression)





def nth_root(number, n):
    """Вычисляет корень n-й степени из числа."""
    if number < 0 and n % 2 == 0:
        raise ValueError("Корень четной степени из отрицательного числа невозможен.")
    return number ** (1 / n)

from equations import insert_multiplication_signs

def calculate(windows):
    try:
        logging.debug("Выполнение")
        expression = windows.entry.text()
        expression = replace_z_t(expression)
        expression = replace_caret_with_power(expression)
        expression = insert_multiplication_signs(expression)
        logging.info(expression)
        if expression == "":
            return
        if '0' in expression and '/' in expression:
            parts = expression.split('/')
            if parts[1].strip() == '0':
                raise ZeroDivisionError
        if '!' in expression:
            expression = expression.replace('!', '')
            result = factorial_scientific(int(expression))
            final_result = addings.dynamic_precision(result)
            mantissa, exponent = final_result.split("E")
            final_result = "{}*10^{}".format(float(mantissa), int(exponent))

            windows.label.setText(f"{final_result}")
            
            
            return
        elif '√' in expression:
            parts = expression.split('√')
            if len(parts) != 2:
                raise ValueError("Неверный формат корня")
            x = float(parts[1])
            n = float(parts[0])
            result = nth_root(x, n)
        else:
            result = sympify(expression).evalf()
            # result = eval(expression)
            logging.info(result)
            logging.info(result)
            logging.info(type(result))

        # Применение динамической точности
        # Применение динамической точности
        final_result = addings.format_number(addings.dynamic_precision(result))
        logging.info(final_result)
        windows.label.setText(f"{final_result}")

        
    
    except ZeroDivisionError:
        logging.error("Ошибка")
        addings.handle_error("деление на ноль")
    except ValueError as ve:
        addings.handle_error(str(ve), input_data=windows.entry.text(), function_name="calculate")
    except SyntaxError:
        addings.handle_error("Синтаксическа ошибка", input_data=windows.entry.text(), function_name="calculate")
    except Exception as e:
        logging.error(e)
        addings.handle_error(str(e), input_data=windows.entry.text(), function_name="calculate")












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




def arithmetic_operation_fractions(window, first_fraction, second_fraction, operation):
    """Производит арифметические операции с дробями."""
    try:
        logging.info(type(first_fraction))
        frac1 = Fraction(first_fraction)
        logging.info(type(second_fraction))
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
        window.label_fractions_result.setText(f"Результат: {result}")
        
        
    except ZeroDivisionError:
        addings.handle_error("деление на ноль", function_name="calculate")
    except ValueError as ve:
        addings.handle_error(str(ve), function_name="arithmetic_operation_fractions")
    except Exception as e:
        addings.handle_error(str(e), function_name="arithmetic_operation_fractions")