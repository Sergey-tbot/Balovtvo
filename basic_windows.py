import tkinter as tk
from tkinter import messagebox
import uuid


class BasicWindow:
    def __init__(self, master, data_storage, item_id, refresh_callback):
        self.master = master
        self.data_storage = data_storage
        self.item_id = item_id
        self.refresh_callback = refresh_callback

        self.window = tk.Toplevel(master)
        self.window.title("Редактировать базовый ресурс" if item_id else "Добавить базовый ресурс")
        self.window.grab_set()

        tk.Label(self.window, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry_name = tk.Entry(self.window, width=30)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.window, text="Цена мин.:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.entry_price_min = tk.Entry(self.window, width=30)
        self.entry_price_min.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.window, text="Цена макс.:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.entry_price_max = tk.Entry(self.window, width=30)
        self.entry_price_max.grid(row=2, column=1, padx=5, pady=5)

        btn_text = "Сохранить" if item_id else "Добавить"
        btn_save = tk.Button(self.window, text=btn_text, command=self.save)
        btn_save.grid(row=3, column=0, pady=10)

        btn_delete = tk.Button(self.window, text="Удалить ресурс", fg='red', command=self.on_delete)
        btn_delete.grid(row=3, column=1, pady=10)

        if item_id:
            self.load_item()

    def load_item(self):
        item = next((x for x in self.data_storage.data['basic'] if x['id'] == self.item_id), None)
        if not item:
            messagebox.showerror("Ошибка", "Элемент не найден")
            self.window.destroy()
            return
        self.entry_name.insert(0, item['name'])
        self.entry_price_min.insert(0, item['price_min'])
        self.entry_price_max.insert(0, item['price_max'])

    def save(self):
        name = self.entry_name.get().strip()
        price_min = self.entry_price_min.get().strip()
        price_max = self.entry_price_max.get().strip()
        if not name:
            messagebox.showwarning("Ошибка", "Введите название")
            return

        if self.item_id:
            item = next((x for x in self.data_storage.data['basic'] if x['id'] == self.item_id), None)
            if item:
                item['name'] = name
                item['price_min'] = price_min
                item['price_max'] = price_max
        else:
            new_id = str(uuid.uuid4())
            self.data_storage.data['basic'].append({
                'id': new_id,
                'name': name,
                'price_min': price_min,
                'price_max': price_max,
            })

        self.data_storage.save_data()
        self.refresh_callback('basic')
        self.window.destroy()

    def on_delete(self):
        if not self.item_id:
            self.window.destroy()
            return
        if messagebox.askyesno("Подтверждение", "Удалить этот ресурс?"):
            self.data_storage.data['basic'] = [item for item in self.data_storage.data['basic'] if item['id'] != self.item_id]
            self.data_storage.save_data()
            self.refresh_callback('basic')
            self.window.destroy()
