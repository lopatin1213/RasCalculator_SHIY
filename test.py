import requests
import json

url = "https://rascalculator.alwaysdata.net/send_errors/"

# Тестовая критическая ошибка
test_data = [
    {
        "error": "КРИТИЧЕСКАЯ [test-001]:\nTraceback (most recent call last):\n  File \"test.py\", line 1, in <module>\n    c = 2/0\nZeroDivisionError: division by zero",
        "version": "9.25.54.24-test",
        "source": "Приложение (глобальный перехватчик)"
    }
]

# Стандартная процедура с CSRF (как в твоём приложении)
session = requests.Session()
session.get(url)  # получаем куки
csrftoken = session.cookies.get('csrftoken')

headers = {
    'Referer': url,
    'X-CSRFToken': csrftoken
}

response = session.post(url, json=test_data, headers=headers)
print("Статус:", response.status_code)
print("Ответ сервера:", response.json())