from cx_Freeze import setup, Executable
import os
import sys

# Заданная версия в setup.py
app_version = str(input("Какая версия: "))  # Здесь указывается версия сборки

# Чтение версии из setup.py и запись в version.txt
version_file = "version.txt"
with open(version_file, "w") as f:
    f.write(app_version)

with open('preferences2.txt', 'w') as f3:
    f3.write('True')
with open('preferences.txt', 'w') as f2:
    f2.write('True')

with open("logs.log", "w") as f4:
    f4.write('')
base_executable = 'Win32Gui'
# Базовые настройки сборки
app_name = "Рас. Калькулятор"       # Название вашего приложения
     # Тип приложения (GUI или консольное); None - консольный режим
icon_path = "calculator.ico"      # Путь к иконке приложения (если есть)

# Скрипт главного модуля
# Ярлык в меню "Пуск"
start_menu_shortcut = Executable(
    script="The_mainest.py",
    base=base_executable,
    icon=icon_path,
    target_name="calculator.exe",
    shortcut_name='Рас.Калькулятор',
    shortcut_dir='ProgramMenuFolder'
)

# Ярлык на рабочем столе
desktop_shortcut = Executable(
    script="The_mainest.py",
    base=base_executable,
    icon=icon_path,
    target_name="calculator.exe",
    shortcut_name='Рас.Калькулятор',
    shortcut_dir='DesktopFolder'
)

# Параметры сборки
options = {
    "build_exe": {
        "packages": [
            "tkinter",      # Необходим для GUI
            "sympy",        # Символьные вычисления
            "PIL",          # Pillow для изображений
            "configparser",  # Конфигурационные файлы
            "settings_panel",  # ВАЖНО: добавляем ваш собственный модуль!
            "matplotlib",   # Матплотлиб для графиков
            "numpy"         # Нампай для массивов и математикиpython setup.py bdist_msi
        ],
        "includes": [],                      # Дополнительные модули, если нужны
        "include_files": ["version.txt", "settings_icon.png", 'settings_panel.py', 'preferences.txt', 'preferences2.txt', 'config.ini', 'cur_version.txt'],# Добавляем файл version.txt
        "optimize": 2,
         # Попробуйте добавить этот параметр# Уровень оптимизации байт-кода (может уменьшить размер)
    },
    "bdist_msi": {
        "upgrade_code": "{66666666-6667-6666-6666-666666666666}",  # Уникальный идентификатор обновления
        "add_to_path": False,  # Не добавлять в PATH
        'initial_target_dir': 'C:\\Antonrasrab',


    }
}

# Настройка сборки
setup(
    name=app_name,
    version=app_version,
    description="Рас. Калькулятор",
    executables=[start_menu_shortcut, desktop_shortcut],  # Два разных ярлык,
    options=options,
    author='PythonSoft'
)
