import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("800x600")
        
        self.records = []
        self.filename = "weather_diary.json"
        
        self.load_data()
        self.create_widgets()
        self.update_list()
    
    def create_widgets(self):
        # Frame для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавить запись", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Поля ввода
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.temp_entry = ttk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Описание погоды:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.desc_entry = ttk.Entry(input_frame, width=40)
        self.desc_entry.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="ew")
        
        self.precip_var = tk.BooleanVar()
        ttk.Checkbutton(input_frame, text="Осадки", variable=self.precip_var).grid(row=1, column=4, padx=5, pady=5)
        
        ttk.Button(input_frame, text="➕ Добавить запись", command=self.add_record).grid(row=2, column=0, columnspan=5, pady=10)
        
        # Frame для фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Дата:").grid(row=0, column=0, padx=5)
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(filter_frame, text="Температура >").grid(row=0, column=2, padx=5)
        self.filter_temp_entry = ttk.Entry(filter_frame, width=8)
        self.filter_temp_entry.grid(row=0, column=3, padx=5)
        ttk.Label(filter_frame, text="°C").grid(row=0, column=4, padx=5)
        
        ttk.Button(filter_frame, text="🔍 Применить фильтр", command=self.apply_filter).grid(row=0, column=5, padx=10)
        ttk.Button(filter_frame, text="❌ Сбросить фильтр", command=self.reset_filter).grid(row=0, column=6, padx=5)
        
        # Таблица записей
        columns = ("Дата", "Температура", "Описание", "Осадки")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        
        # Кнопки управления
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(btn_frame, text="💾 Сохранить в JSON", command=self.save_to_json).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📂 Загрузить из JSON", command=self.load_from_json).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑 Удалить выбранное", command=self.delete_selected).pack(side="left", padx=5)
    
    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def add_record(self):
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precip_var.get()
        
        # Проверки
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД")
            return
        
        try:
            temp_float = float(temp)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return
        
        if not description:
            messagebox.showerror("Ошибка", "Описание погоды не может быть пустым")
            return
        
        record = {
            "date": date,
            "temperature": temp_float,
            "description": description,
            "precipitation": precipitation
        }
        
        self.records.append(record)
        self.update_list()
        
        # Очистка полей
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)
        
        messagebox.showinfo("Успех", "Запись добавлена!")
    
    def update_list(self, records_to_show=None):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        data = records_to_show if records_to_show is not None else self.records
        
        for record in data:
            precip_text = "Да" if record["precipitation"] else "Нет"
            self.tree.insert("", "end", values=(
                record["date"],
                f"{record['temperature']}°C",
                record["description"],
                precip_text
            ))
    
    def apply_filter(self):
        filter_date = self.filter_date_entry.get().strip()
        filter_temp_str = self.filter_temp_entry.get().strip()
        
        filtered = self.records.copy()
        
        if filter_date:
            if not self.validate_date(filter_date):
                messagebox.showerror("Ошибка", "Неверный формат даты в фильтре")
                return
            filtered = [r for r in filtered if r["date"] == filter_date]
        
        if filter_temp_str:
            try:
                filter_temp = float(filter_temp_str)
                filtered = [r for r in filtered if r["temperature"] > filter_temp]
            except ValueError:
                messagebox.showerror("Ошибка", "Температура в фильтре должна быть числом")
                return
        
        self.update_list(filtered)
    
    def reset_filter(self):
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        self.update_list()
    
    def save_to_json(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные сохранены в {self.filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")
    
    def load_from_json(self):
        if not os.path.exists(self.filename):
            messagebox.showwarning("Предупреждение", f"Файл {self.filename} не найден")
            return
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.records = json.load(f)
            self.update_list()
            messagebox.showinfo("Успех", f"Данные загружены из {self.filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")
    
    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.records = json.load(f)
            except:
                self.records = []
    
    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите запись для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранную запись?"):
            # Получаем значения из выбранной строки
            values = self.tree.item(selected[0])['values']
            date = values[0]
            temp = float(values[1].replace('°C', ''))
            
            # Находим и удаляем запись
            for i, record in enumerate(self.records):
                if record["date"] == date and record["temperature"] == temp:
                    del self.records[i]
                    break
            
            self.update_list()
            messagebox.showinfo("Успех", "Запись удалена")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()