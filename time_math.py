import re
import addings

UNIT_TO_MS = {
    'ms': 1,
    's': 1000,
    'm': 60000,
    'h': 3600000,
    'd': 86400000,
    'mo': 2592000000,
    'y': 31536000000
}

UNITS_ORDER = [
    ('y', 31536000000),
    ('mo', 2592000000),
    ('d', 86400000),
    ('h', 3600000),
    ('m', 60000),
    ('s', 1000),
    ('ms', 1)
]

def compute_time(window):
    try:
        expr = window.text.text().strip()
        if not expr:
            window.result.setText("Ошибка: пустое выражение")
            return
        result = _compute(expr)
        window.result.setText(result)
    except Exception as e:
        addings.handle_error(str(e), input_data=window.text.text(), function_name="compute_time")
        window.result.setText(f"Ошибка: {str(e)}")

def compute_time_str(expr: str) -> str:
    try:
        if not expr.strip():
            return "Ошибка: пустое выражение"
        return _compute(expr.strip())
    except Exception as e:
        addings.handle_error(str(e), input_data=expr, function_name="compute_time_str")
        return f"Ошибка: {str(e)}"

def _insert_colons(expr: str) -> str:
    pattern = r'(\d+[a-zA-Z]+)(?=\d+[a-zA-Z]+)'
    def repl(match):
        return match.group(0) + ':'
    while True:
        new_expr = re.sub(pattern, repl, expr)
        if new_expr == expr:
            break
        expr = new_expr
    return expr

def _wrap_colon_blocks(expr: str) -> str:
    pattern = r'((?:\d+[a-zA-Z]+:)+(?:\d+[a-zA-Z]+))'
    def repl(match):
        block = match.group(1)
        block_with_plus = block.replace(':', '+')
        return f'({block_with_plus})'
    expr = re.sub(pattern, repl, expr)
    return expr

def _tokenize(expr: str) -> list:
    units = sorted(UNIT_TO_MS.keys(), key=len, reverse=True)
    pattern = r"(\d+\.?\d*|" + "|".join(re.escape(u) for u in units) + r"|[+\-*/()])"
    tokens = re.findall(pattern, expr, re.IGNORECASE)
    return [tok.lower() if tok.lower() in UNIT_TO_MS else tok for tok in tokens]

def _apply_op(op, left, right):
    left_val, left_dim = left
    right_val, right_dim = right
    if op == '+':
        if left_dim != right_dim:
            raise ValueError("Нельзя складывать время и безразмерную величину")
        return (left_val + right_val, left_dim)
    elif op == '-':
        if left_dim != right_dim:
            raise ValueError("Нельзя вычитать время и безразмерную величину")
        return (left_val - right_val, left_dim)
    elif op == '*':
        # Умножение: если один безразмерный, то результат размерный (если другой размерный)
        return (left_val * right_val, left_dim or right_dim)  # если хоть один размерный → размерный
    elif op == '/':
        if left_dim and right_dim:
            # время / время → безразмерное
            return (left_val / right_val, False)
        elif left_dim and not right_dim:
            # время / безразмерное → время
            return (left_val / right_val, True)
        elif not left_dim and right_dim:
            # безразмерное / время → ошибка
            raise ValueError("Деление безразмерной величины на время недопустимо")
        else:
            # безразмерное / безразмерное → безразмерное
            return (left_val / right_val, False)
    else:
        raise ValueError(f"Неизвестный оператор {op}")

def _evaluate(tokens: list):
    values = []      # стек для чисел — каждый элемент: (value, is_time)
    ops = []         # стек операторов
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok.replace('.', '').isdigit():
            if i+1 < len(tokens) and tokens[i+1] in UNIT_TO_MS:
                num = float(tok)
                unit = tokens[i+1]
                val = num * UNIT_TO_MS[unit]
                values.append((val, True))   # размерное (время)
                i += 2
            else:
                values.append((float(tok), False))   # безразмерное
                i += 1
        elif tok in UNIT_TO_MS:
            val = UNIT_TO_MS[tok]
            values.append((val, True))
            i += 1
        elif tok in precedence:
            while ops and ops[-1] in precedence and precedence[ops[-1]] >= precedence[tok]:
                op = ops.pop()
                right = values.pop()
                left = values.pop()
                res = _apply_op(op, left, right)
                values.append(res)
            ops.append(tok)
            i += 1
        elif tok == '(':
            ops.append(tok)
            i += 1
        elif tok == ')':
            while ops and ops[-1] != '(':
                op = ops.pop()
                right = values.pop()
                left = values.pop()
                res = _apply_op(op, left, right)
                values.append(res)
            if ops and ops[-1] == '(':
                ops.pop()
            i += 1
        else:
            return None, f"Неизвестный токен: {tok}"

    while ops:
        op = ops.pop()
        right = values.pop()
        left = values.pop()
        res = _apply_op(op, left, right)
        values.append(res)

    if len(values) != 1:
        return None, "Ошибка в выражении"
    result_val, result_is_time = values[0]
    return result_val, result_is_time   # возвращаем значение и флаг размерности

def _compute(expr: str) -> str:
    try:
        expr = expr.replace(" ", "")
        if not expr:
            return "Ошибка: пустое выражение"
        expr = _insert_colons(expr)
        expr = _wrap_colon_blocks(expr)

        parts = expr.split("->")
        if len(parts) > 2:
            return "Ошибка: только одна стрелка ->"
        left = parts[0]
        target_unit = parts[1].strip().lower() if len(parts) == 2 else None

        tokens = _tokenize(left)
        if not tokens:
            return "Ошибка: не удалось разобрать выражение"

        result_val, is_time = _evaluate(tokens)
        if result_val is None:
            return f"Ошибка: {is_time}"  # is_time содержит сообщение об ошибке

        # Если результат безразмерный, выводим как число
        if not is_time:
            return addings.dynamic_precision(result_val)

        # Результат — время, форматируем
        if target_unit:
            return _convert_to_unit(result_val, target_unit)
        else:
            return _format_expanded(result_val)

    except Exception as e:
        return f"Ошибка: {str(e)}"

def _convert_to_unit(value_ms: float, unit: str) -> str:
    if unit not in UNIT_TO_MS:
        return f"Ошибка: неизвестная единица '{unit}'"
    result = value_ms / UNIT_TO_MS[unit]
    result = addings.dynamic_precision(result)
    return f"{result}{unit}"

def _format_expanded(value_ms: float) -> str:
    if value_ms < 0:
        return "Ошибка: отрицательное время"
    parts = []
    remaining = int(round(value_ms))
    for unit, ms_in_unit in UNITS_ORDER:
        if remaining >= ms_in_unit:
            count = remaining // ms_in_unit
            remaining -= count * ms_in_unit
            parts.append(f"{count}{unit}")
    if remaining > 0:
        parts.append(f"{remaining}ms")
    return ":".join(parts) if parts else "0ms"