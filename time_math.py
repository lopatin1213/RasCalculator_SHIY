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
def _wrap_colon_blocks(expr: str) -> str:
    # Ищем цепочки вида числоединица:числоединица[:числоединица...]
    pattern = r'((?:\d+[a-zA-Z]+:)+(?:\d+[a-zA-Z]+))'
    def repl(match):
        block = match.group(1)
        # Заменяем все : на + внутри блока
        block_with_plus = block.replace(':', '+')
        # Возвращаем блок в скобках
        return f'({block_with_plus})'
    # Заменяем все такие блоки
    expr = re.sub(pattern, repl, expr)
    return expr

def _insert_colons(expr: str) -> str:
    """
    Вставляет ':' между блоками 'число+единица', если между ними нет оператора.
    """
    # Регулярка: ищем два подряд идущих блока вида число+единица
    # Пример: 2h30m -> 2h:30m
    # 1d12h30m -> 1d:12h:30m
    pattern = r'(\d+[a-zA-Z]+)(?=\d+[a-zA-Z]+)'
    # Заменяем на первую группу + ':'
    # Но нужно делать это аккуратно, чтобы не задеть уже существующие ':'
    # Сначала ищем все блоки вида число+единица
    # Простой подход: идём по строке и если видим границу между двумя блоками — вставляем ':'
    # Но проще с помощью регулярки: ищем место между двумя блоками и вставляем ':'

    # Блок — это число, за которым следует единица (одна или несколько букв)
    # Между ними не должно быть операторов (+, -, *, /, (, ))
    # Но наша регулярка захватывает только последовательности, поэтому она сработает

    # Используем re.sub с функцией замены
    def repl(match):
        # match — это группа (число+единица) перед следующим блоком
        # Добавляем ':'
        return match.group(0) + ':'

    # Заменяем все вхождения, пока есть совпадения
    # Но делаем это рекурсивно, чтобы обработать цепочки
    while True:
        new_expr = re.sub(pattern, repl, expr)
        if new_expr == expr:
            break
        expr = new_expr
    return expr
def compute_time(window):
    try:
        expr = window.text.text().strip()
        if not expr:
            window.result.setText("Ошибка: пустое выражение")
            return

        # Заменяем `:` на `+` в форматах `2h:30m` -> `2h+30m`
        def replace_colon(match):
            return match.group(1) + match.group(2) + '+' + match.group(3) + match.group(4)
        #expr = re.sub(r'(\d+)([a-zA-Z]+):(\d+)([a-zA-Z]+)', replace_colon, expr)

        result = _compute(expr)
        window.result.setText(result)

    except Exception as e:
        addings.handle_error(str(e), input_data=window.text.text(), function_name="compute_time")
        window.result.setText(f"Ошибка: {str(e)}")

def _compute(expr: str) -> str:
    try:
        expr = expr.replace(" ", "")
        if not expr:
            return "Ошибка: пустое выражение"
        expr = _insert_colons(expr)
        # Обработка : блоков
        print(expr)
        expr = _wrap_colon_blocks(expr)
        print(expr)
        parts = expr.split("->")
        if len(parts) > 2:
            return "Ошибка: только одна стрелка ->"
        left = parts[0]
        target_unit = parts[1].strip().lower() if len(parts) == 2 else None

        tokens = _tokenize(left)
        if not tokens:
            return "Ошибка: не удалось разобрать выражение"

        result_ms, error = _evaluate(tokens)
        if error:
            raise Exception(f"Ошибка: {error}")

        if target_unit:
            return _convert_to_unit(result_ms, target_unit)
        else:
            return _format_expanded(result_ms)

    except Exception as e:
        raise Exception(f"Ошибка: {str(e)}")

def _tokenize(expr: str) -> list:
    # Сортируем единицы по убыванию длины, чтобы 'ms' захватывался раньше 's'
    units = sorted(UNIT_TO_MS.keys(), key=len, reverse=True)
    pattern = r"(\d+\.?\d*|" + "|".join(re.escape(u) for u in units) + r"|[+\-*/()])"
    tokens = re.findall(pattern, expr, re.IGNORECASE)
    # Приводим единицы к нижнему регистру
    return [tok.lower() if tok.lower() in UNIT_TO_MS else tok for tok in tokens]

def _evaluate(tokens: list):
    i = 0
    new_tokens = []
    while i < len(tokens):
        tok = tokens[i]
        # Если токен — число (целое или дробное)
        if tok.replace('.', '').isdigit():
            # Проверяем, есть ли следующий токен — единица измерения
            if i+1 < len(tokens) and tokens[i+1] in UNIT_TO_MS:
                num = float(tok)
                unit = tokens[i+1]
                val = num * UNIT_TO_MS[unit]
                new_tokens.append(str(val))
                i += 2
            else:
                # Число без единицы — просто добавляем как число
                new_tokens.append(tok)
                i += 1
        elif tok in UNIT_TO_MS:
            # Единица без числа — считаем как 1 * единица
            val = UNIT_TO_MS[tok]
            new_tokens.append(str(val))
            i += 1
        elif tok in ['+', '-', '*', '/', '(', ')']:
            new_tokens.append(tok)
            i += 1
        else:
            return None, f"Неизвестный токен: {tok}"
    try:
        expr_str = " ".join(new_tokens)
        result = eval(expr_str)
        return result, None
    except Exception as e:
        return None, str(e)

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