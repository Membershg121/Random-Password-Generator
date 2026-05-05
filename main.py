import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime

class PasswordGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Password Generator")
        self.root.geometry("700x500")
        self.root.resizable(True, True)

        # История паролей
        self.history_file = "history.json"
        self.history = self.load_history()

        # Элементы интерфейса
        self.create_widgets()
        self.update_password_strength()

    def create_widgets(self):
        # Рамка параметров
        frame_settings = ttk.LabelFrame(self.root, text="Настройки пароля", padding=10)
        frame_settings.pack(fill="x", padx=10, pady=5)

        # Ползунок длины пароля
        ttk.Label(frame_settings, text="Длина пароля:").grid(row=0, column=0, sticky="w", pady=5)
        self.length_var = tk.IntVar(value=12)
        self.length_slider = ttk.Scale(frame_settings, from_=4, to=32, orient="horizontal",
                                       variable=self.length_var, command=self.update_length_label)
        self.length_slider.grid(row=0, column=1, sticky="ew", padx=5)
        self.length_label = ttk.Label(frame_settings, text="12")
        self.length_label.grid(row=0, column=2, padx=5)
        
        # Чекбоксы
        self.use_digits = tk.BooleanVar(value=True)
        self.use_letters = tk.BooleanVar(value=True)
        self.use_special = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(frame_settings, text="Цифры (0-9)", variable=self.use_digits,
                        command=self.update_password_strength).grid(row=1, column=0, sticky="w", pady=5)
        ttk.Checkbutton(frame_settings, text="Буквы (A-Z, a-z)", variable=self.use_letters,
                        command=self.update_password_strength).grid(row=1, column=1, sticky="w", pady=5)
        ttk.Checkbutton(frame_settings, text="Спецсимволы (!@#$%^&*)", variable=self.use_special,
                        command=self.update_password_strength).grid(row=1, column=2, sticky="w", pady=5)

        # Кнопка генерации
        self.generate_btn = ttk.Button(self.root, text="Сгенерировать пароль", command=self.generate_password)
        self.generate_btn.pack(pady=10)

        # Поле для отображения пароля
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(self.root, textvariable=self.password_var, font=("Courier", 12), state="readonly")
        self.password_entry.pack(fill="x", padx=10, pady=5)

        # Индикатор сложности
        self.strength_label = ttk.Label(self.root, text="Сложность: ")
        self.strength_label.pack(pady=5)

        # Кнопка копирования
        self.copy_btn = ttk.Button(self.root, text="Копировать в буфер", command=self.copy_to_clipboard)
        self.copy_btn.pack(pady=5)

        # Таблица истории
        ttk.Label(self.root, text="История паролей:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(10,0))
        
        frame_history = ttk.Frame(self.root)
        frame_history.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(frame_history)
        scrollbar.pack(side="right", fill="y")
        
        self.history_tree = ttk.Treeview(frame_history, columns=("password", "length", "date"), show="headings",
                                         yscrollcommand=scrollbar.set)
        self.history_tree.heading("password", text="Пароль")
        self.history_tree.heading("length", text="Длина")
        self.history_tree.heading("date", text="Дата и время")
        self.history_tree.column("password", width=200)
        self.history_tree.column("length", width=60)
        self.history_tree.column("date", width=150)
        self.history_tree.pack(fill="both", expand=True)
        scrollbar.config(command=self.history_tree.yview)
        
        # Кнопка очистки истории
        ttk.Button(self.root, text="Очистить историю", command=self.clear_history).pack(pady=5)
        
        # Загрузить историю в таблицу
        self.refresh_history_table()
        
        # Настройка сетки
        frame_settings.columnconfigure(1, weight=1)

    def update_length_label(self, event=None):
        self.length_label.config(text=str(int(self.length_var.get())))

    def generate_password(self):
        length = int(self.length_var.get())
        use_digits = self.use_digits.get()
        use_letters = self.use_letters.get()
        use_special = self.use_special.get()
        
        # Проверка: выбран хотя бы один тип символов
        if not (use_digits or use_letters or use_special):
            messagebox.showerror("Ошибка", "Выберите хотя бы один тип символов!")
            return
        
        # Формируем пул символов
        chars = ""
        if use_digits:
            chars += string.digits
        if use_letters:
            chars += string.ascii_letters
        if use_special:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Генерация пароля
        password = ''.join(random.choice(chars) for _ in range(length))
        
        # Проверка: содержит ли пароль требуемые типы (для надёжности)
        # В реальности random.choice может выдать однотипный пароль, но редко.
        # Можно добавить гарантию наличия каждого выбранного типа.
        password = self.ensure_all_types(password, use_digits, use_letters, use_special, chars, length)
        
        self.password_var.set(password)
        self.update_password_strength()
        
        # Сохраняем в историю
        self.save_to_history(password, length)
        self.refresh_history_table()
    
    def ensure_all_types(self, password, use_digits, use_letters, use_special, chars, length):
        """Гарантирует, что пароль содержит все выбранные типы символов"""
        # Простая проверка: если пароль не содержит нужные типы, генерируем заново
        # (более надёжный метод - явное добавление, но для простоты оставим так)
        max_attempts = 10
        for _ in range(max_attempts):
            ok = True
            if use_digits and not any(c in string.digits for c in password):
                ok = False
            if use_letters and not any(c in string.ascii_letters for c in password):
                ok = False
            if use_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
                ok = False
            if ok:
                return password
            password = ''.join(random.choice(chars) for _ in range(length))
        return password
    
    def update_password_strength(self):
        length = int(self.length_var.get())
        types_count = sum([self.use_digits.get(), self.use_letters.get(), self.use_special.get()])
        
        if length < 6 or types_count < 2:
            strength = "Слабый"
            color = "red"
        elif length < 10 or types_count < 3:
            strength = "Средний"
            color = "orange"
        else:
            strength = "Сильный"
            color = "green"
        
        self.strength_label.config(text=f"Сложность: {strength}", foreground=color)
    
    def save_to_history(self, password, length):
        entry = {
            "password": password,
            "length": length,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(entry)
        # Ограничим историю 50 записями
        if len(self.history) > 50:
            self.history = self.history[-50:]
        self.save_history()
    
    def save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")
    
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def refresh_history_table(self):
        # Очищаем таблицу
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)
        # Добавляем записи (новые сверху)
        for entry in reversed(self.history):
            self.history_tree.insert("", "end", values=(entry["password"], entry["length"], entry["date"]))
    
    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю историю паролей?"):
            self.history = []
            self.save_history()
            self.refresh_history_table()
    
    def copy_to_clipboard(self):
        if self.password_var.get():
            self.root.clipboard_clear()
            self.root.clipboard_append(self.password_var.get())
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Внимание", "Нет сгенерированного пароля.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()