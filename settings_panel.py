import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser as tkcolorchooser
import configparser

class SettingsPanel:
    def __init__(self, parent, main_window, initial_bg_color, initial_text_color, initial_button_color,
                 initial_entry_color):
        self.parent = parent
        self.main_window = main_window
        self.style = ttk.Style()  # Экземпляр класса Style
        self.initial_bg_color = initial_bg_color
        self.initial_text_color = initial_text_color
        self.initial_button_color = initial_button_color
        self.initial_entry_color = initial_entry_color

        self.window = tk.Toplevel(parent)
        self.window.title("Настройки")
        self.window.resizable(False, False)

        self.frame = ttk.Frame(self.window)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.window.focus_force()  # Гарантирует получение фокуса
        self.window.grab_set()  # Захватывает управление мышью и клавиатурой
        # Переменные для хранения выбранных цветов
        self.bg_color_var = tk.StringVar(value=self.initial_bg_color)
        self.text_color_var = tk.StringVar(value=self.initial_text_color)
        self.button_color_var = tk.StringVar(value=self.initial_button_color)
        self.entry_color_var = tk.StringVar(value=self.initial_entry_color)

        # Настройки для изменения цвета фона
        self.create_setting("Цвет фона", self.bg_color_var, default_color=self.initial_bg_color)

        # Настройки для изменения цвета текста
        self.create_setting("Цвет текста", self.text_color_var, default_color=self.initial_text_color)

        # Настройки для изменения цвета кнопок
        self.create_setting("Цвет кнопок", self.button_color_var, default_color=self.initial_button_color)

        # Настройки для изменения цвета полей ввода
        self.create_setting("Цвет полей ввода", self.entry_color_var, default_color=self.initial_entry_color)

        # Кнопка для сохранения настроек
        save_button = ttk.Button(self.frame, text="Сохранить настройки", command=self.save_settings)
        save_button.pack(pady=10)

    def create_setting(self, label_text, variable, default_color):
        """Создание блока настроек для выбора цвета"""
        frame = ttk.Frame(self.frame)
        frame.pack(fill=tk.X, pady=5)

        label = ttk.Label(frame, text=label_text)
        label.pack(side=tk.LEFT)

        combobox = ttk.Combobox(frame, textvariable=variable, values=[default_color, "#ffffff", "#000000", "#e0e0e0"], state="readonly")
        combobox.current(0)
        combobox.pack(side=tk.LEFT, padx=10)

        button = ttk.Button(frame, text="Выбрать цвет", command=lambda v=variable: self.choose_color(v))
        button.pack(side=tk.LEFT)

    def choose_color(self, variable):
        """Выбор цвета через диалоговое окно"""
        chosen_color = tkcolorchooser.askcolor()[1]
        if chosen_color:
            variable.set(chosen_color)

    def apply_background_color(self, color):
        self.main_window.config(bg=color)
        self.style.configure('.', background=color, foreground=self.contrast_color(color))
        self.style.configure('TLabel', background=color, foreground=self.contrast_color(color))
        self.style.configure('TButton', background=self.contrast_color(color), foreground=color)
        self.style.configure('TEntry', foreground=self.contrast_color(self.contrast_color(color)),
                            fieldbackground=self.contrast_color(color), insertbackground='black',
                            selectforeground=self.contrast_color(self.contrast_color(color)),
                            selectbackground='gray')
        self.style.configure('Text', background=color, foreground=self.contrast_color(color))

    def apply_text_color(self, color):
        self.style.configure('TLabel', foreground=color)
        self.style.configure('TButton', foreground=color)
        self.style.configure('TEntry', foreground=color, selectforeground=color)
        self.style.configure('Text', foreground=color)

    def apply_button_color(self, color):
        self.style.configure('TButton', background=color)

    def apply_entry_color(self, color):
        self.style.configure('TEntry', fieldbackground=color)

    def save_settings(self):
        config = configparser.ConfigParser()
        config['Settings'] = {
            'bg_color': self.bg_color_var.get(),
            'text_color': self.text_color_var.get(),
            'button_color': self.button_color_var.get(),
            'entry_color': self.entry_color_var.get()
        }
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        print("Настройки успешно сохранены!")

        # Применяем новые настройки
        self.apply_background_color(self.bg_color_var.get())
        self.apply_text_color(self.text_color_var.get())
        self.apply_button_color(self.button_color_var.get())
        self.apply_entry_color(self.entry_color_var.get())



    @staticmethod
    def contrast_color(hex_color):
        """Вычисляет контрастный цвет для данного HEX-кода"""
        red = int(hex_color[1:3], 16)
        green = int(hex_color[3:5], 16)
        blue = int(hex_color[5:], 16)
        inverted_red = 255 - red
        inverted_green = 255 - green
        inverted_blue = 255 - blue
        contrast_hex = "#{:02X}{:02X}{:02X}".format(inverted_red, inverted_green, inverted_blue)
        return contrast_hex

    def load_settings(self, main_window, initial_bg_color, initial_text_color, initial_button_color,
                 initial_entry_color):
        config = configparser.ConfigParser()
        config.read('config.ini')

        try:
            bg_color = config['Settings']['bg_color']
            text_color = config['Settings']['text_color']
            button_color = config['Settings']['button_color']
            entry_color = config['Settings']['entry_color']
        except KeyError:
            # Если ключ отсутствует, задаем дефолтные значения
            bg_color = initial_bg_color
            text_color = initial_text_color
            button_color = initial_button_color
            entry_color = initial_entry_color

        # Применяем настройки к главному окну
        main_window.config(bg=bg_color)
        style = ttk.Style()  # Создаем экземпляр класса Style
        style.configure('.', background=bg_color, foreground=self.contrast_color(bg_color))
        style.configure('TLabel', background=bg_color, foreground=self.contrast_color(bg_color))
        style.configure('TButton', background=button_color, foreground=text_color)
        style.configure('TEntry', foreground=text_color, fieldbackground=entry_color,
                        insertbackground='black', selectforeground=text_color, selectbackground='gray')
        style.configure('Text', background=bg_color, foreground=self.contrast_color(bg_color))

# Пример использования в другом файле
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Главное окно")
    # Создаем экземпляр класса SettingsPanel
    settings_panel = SettingsPanel(root, root, "#FFFFFF", "#000000", "#E0E0E0", "#F0F0F0")
    settings_panel.load_settings(root, "#FFFFFF", "#000000", "#E0E0E0", "#F0F0F0")



    # Показываем главное окно
    root.mainloop()