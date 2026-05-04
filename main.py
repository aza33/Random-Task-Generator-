import tkinter as tk
from tkinter import messagebox, ttk
import random
import json
import os

# Список предопределённых задач (название, тип)
PREDEFINED_TASKS = [
    ("Прочитать статью по программированию", "учёба"),
    ("Сделать зарядку 15 минут", "спорт"),
    ("Помыть посуду", "работа"),
    ("Посмотреть полезное видео на YouTube", "учёба"),
    ("Пробежка на улице", "спорт"),
    ("Закончить отчёт", "работа"),
]

class TaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("500x500")

        # Список всех задач (история)
        self.history = []

        # Загружаем историю из файла
        self.load_history()

        # Создаём виджеты
        self.create_widgets()

    def create_widgets(self):
        # Метка с заголовком
        title_label = tk.Label(self.root, text="Генератор случайных задач", font=("Arial", 16))
        title_label.pack(pady=10)

        # Кнопка генерации
        self.generate_btn = tk.Button(self.root, text="Сгенерировать задачу", command=self.generate_task, bg="lightblue")
        self.generate_btn.pack(pady=10)

        # Поле для отображения текущей задачи
        self.current_task_label = tk.Label(self.root, text="Нажмите кнопку!", font=("Arial", 12), wraplength=400)
        self.current_task_label.pack(pady=10)

        # Фильтр по типу
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(pady=10)

        tk.Label(filter_frame, text="Фильтр по типу:").pack(side=tk.LEFT)
        self.filter_var = tk.StringVar(value="все")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, values=["все", "учёба", "спорт", "работа"])
        filter_combo.pack(side=tk.LEFT, padx=5)
        filter_combo.bind("<<ComboboxSelected>>", self.update_history_display)

        # Список истории
        history_frame = tk.Frame(self.root)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(history_frame, text="История задач:", font=("Arial", 12)).pack(anchor=tk.W)

        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_listbox = tk.Listbox(history_frame, yscrollcommand=scrollbar.set, height=12)
        self.history_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.history_listbox.yview)

        # Блок добавления новой задачи
        add_frame = tk.Frame(self.root)
        add_frame.pack(pady=10, fill=tk.X, padx=10)

        tk.Label(add_frame, text="Новая задача:").pack(side=tk.LEFT)
        self.new_task_entry = tk.Entry(add_frame, width=25)
        self.new_task_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(add_frame, text="Тип:").pack(side=tk.LEFT)
        self.new_task_type = ttk.Combobox(add_frame, values=["учёба", "спорт", "работа"], width=8)
        self.new_task_type.pack(side=tk.LEFT, padx=5)
        self.new_task_type.set("учёба")

        add_btn = tk.Button(add_frame, text="Добавить", command=self.add_custom_task)
        add_btn.pack(side=tk.LEFT, padx=5)

        # Обновляем отображение истории
        self.update_history_display()

    def generate_task(self):
        """Выбирает случайную задачу из предопределённых + пользовательских"""
     
        
        # Берём названия задач из предопределённого списка
        all_task_names = [task[0] for task in PREDEFINED_TASKS]
        
        # Добавляем пользовательские задачи (которые добавляли через интерфейс)
        user_tasks = [item for item in self.history if item["type"] == "user_added"]
        for ut in user_tasks:
            all_task_names.append(ut["name"])
        
        # Убираем дубликаты (чтобы не было одинаковых, но можно и оставить)
        all_task_names = list(set(all_task_names))
        
        if not all_task_names:
            messagebox.showwarning("Нет задач", "Добавьте хотя бы одну задачу!")
            return
        
        task_name = random.choice(all_task_names)
        
        # Определяем тип задачи
        task_type = "другое"
        for predefined in PREDEFINED_TASKS:
            if predefined[0] == task_name:
                task_type = predefined[1]
                break
        
        # Запоминаем в истории
        self.history.append({
            "name": task_name,
            "type": task_type,
            "source": "predefined"
        })
        
        # Сохраняем историю в файл
        self.save_history()
        
        # Отображаем текущую задачу
        self.current_task_label.config(text=f"Текущая задача: {task_name} (тип: {task_type})")
        
        # Обновляем список истории
        self.update_history_display()
    
    def add_custom_task(self):
        """Добавляет новую задачу от пользователя"""
        task_name = self.new_task_entry.get().strip()
        task_type = self.new_task_type.get()
        
        # Проверка на пустую строку
        if task_name == "":
            messagebox.showerror("Ошибка", "Название задачи не может быть пустым!")
            return
        
        # Проверка на дубликат (опционально)
        for item in self.history:
            if item["name"].lower() == task_name.lower() and item["type"] == task_type:
                messagebox.showwarning("Предупреждение", "Такая задача уже есть в истории!")
                return
        
        # Добавляем в историю
        self.history.append({
            "name": task_name,
            "type": task_type,
            "source": "user"
        })
        
        self.save_history()
        self.update_history_display()
        self.new_task_entry.delete(0, tk.END)
        messagebox.showinfo("Успех", f"Задача '{task_name}' добавлена!")
    
    def update_history_display(self, event=None):
        """Обновляет список истории с учётом фильтра"""
        self.history_listbox.delete(0, tk.END)
        
        filter_type = self.filter_var.get()
        
        for idx, task in enumerate(self.history, 1):
            # Применяем фильтр
            if filter_type != "все" and task["type"] != filter_type:
                continue
            
            display_text = f"{idx}. {task['name']} (тип: {task['type']})"
            self.history_listbox.insert(tk.END, display_text)
    
    def save_history(self):
        """Сохраняет историю в JSON файл"""
        try:
            with open("tasks.json", "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")
    
    def load_history(self):
        """Загружает историю из JSON файла"""
        if os.path.exists("tasks.json"):
            try:
                with open("tasks.json", "r", encoding="utf-8") as f:
                    self.history = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить историю: {e}")
                self.history = []
        else:
            self.history = []

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = TaskGenerator(root)
    root.mainloop()