import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import uuid

class ProductWindow:
    def __init__(self, master, data_storage, item_id, refresh_callback):
        self.master = master
        self.data_storage = data_storage
        self.item_id = item_id
        self.refresh_callback = refresh_callback

        self.window = tk.Toplevel(master)
        self.window.title("Редактировать производный ресурс" if item_id else "Добавить производный ресурс")
        self.window.grab_set()

        left_frame = tk.Frame(self.window)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        # Основные поля
        tk.Label(left_frame, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry_name = tk.Entry(left_frame, width=30)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(left_frame, text="Цена мин.:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.entry_price_min = tk.Entry(left_frame, width=30)
        self.entry_price_min.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(left_frame, text="Цена макс.:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.entry_price_max = tk.Entry(left_frame, width=30)
        self.entry_price_max.grid(row=2, column=1, padx=5, pady=5)

        # Новые поля
        tk.Label(left_frame, text="Кол-во на цикл:").grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.entry_output_per_cycle = tk.Entry(left_frame, width=30)
        self.entry_output_per_cycle.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(left_frame, text="Циклов в день:").grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.entry_cycles_per_day = tk.Entry(left_frame, width=30)
        self.entry_cycles_per_day.grid(row=4, column=1, padx=5, pady=5)

        tk.Label(left_frame, text="Стоимость производства в день:").grid(row=5, column=0, padx=5, pady=5, sticky='e')
        self.entry_production_cost_per_day = tk.Entry(left_frame, width=30)
        self.entry_production_cost_per_day.grid(row=5, column=1, padx=5, pady=5)

        # Материалы
        tk.Label(left_frame, text="Используемые материалы:").grid(row=6, column=0, columnspan=2, pady=(10,0))

        self.materials_tree = ttk.Treeview(left_frame, columns=('Материал', 'Количество'), show='headings', height=8)
        self.materials_tree.heading('Материал', text='Материал')
        self.materials_tree.heading('Количество', text='Количество')
        self.materials_tree.column('Материал', width=150)
        self.materials_tree.column('Количество', width=100, anchor='center')
        self.materials_tree.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

        btn_frame = tk.Frame(left_frame)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=5)

        btn_add_material = tk.Button(btn_frame, text="Добавить материал", command=self.on_add_material)
        btn_add_material.pack(side='left', padx=5)

        btn_edit_material = tk.Button(btn_frame, text="Редактировать материал", command=self.on_edit_material)
        btn_edit_material.pack(side='left', padx=5)

        btn_delete_material = tk.Button(btn_frame, text="Удалить материал", command=self.on_delete_material)
        btn_delete_material.pack(side='left', padx=5)

        btn_save = tk.Button(left_frame, text="Сохранить", command=self.save)
        btn_save.grid(row=9, column=0, pady=10)

        btn_delete_resource = tk.Button(left_frame, text="Удалить ресурс", fg='red', command=self.on_delete_resource)
        btn_delete_resource.grid(row=9, column=1, pady=10)

        # Правая часть - статистика
        right_frame = tk.Frame(self.window)
        right_frame.grid(row=0, column=1, sticky='nsew', padx=10, pady=10)

        tk.Label(right_frame, text="Статистика", font=('Arial', 12, 'bold')).pack()

        self.stats_text = tk.Text(right_frame, width=40, height=20, state='disabled', bg='#f0f0f0')
        self.stats_text.pack(padx=5, pady=5)

        self.materials = []

        if item_id:
            self.load_item()
        else:
            self.refresh_materials_table()
            self.update_statistics()

        self.window.columnconfigure(0, weight=3)
        self.window.columnconfigure(1, weight=2)
        self.window.rowconfigure(0, weight=1)

    def load_item(self):
        item = next((x for x in self.data_storage.data['derived'] if x['id'] == self.item_id), None)
        if not item:
            messagebox.showerror("Ошибка", "Элемент не найден")
            self.window.destroy()
            return
        self.entry_name.insert(0, item['name'])
        self.entry_price_min.insert(0, item['price_min'])
        self.entry_price_max.insert(0, item['price_max'])
        self.entry_output_per_cycle.insert(0, item.get('output_per_cycle', ''))
        self.entry_cycles_per_day.insert(0, item.get('cycles_per_day', ''))
        self.entry_production_cost_per_day.insert(0, item.get('production_cost_per_day', ''))
        self.materials = item.get('materials', [])
        self.refresh_materials_table()
        self.update_statistics()

    def refresh_materials_table(self):
        self.materials_tree.delete(*self.materials_tree.get_children())
        for mat in self.materials:
            self.materials_tree.insert('', 'end', iid=mat['id'], values=(mat['name'], mat['quantity']))
        self.update_statistics()

    def on_add_material(self):
        # Объединяем базовые и производные материалы для выбора
        all_materials = self.data_storage.data['basic'] + self.data_storage.data['derived']
        if self.item_id is not None:
            all_materials = [m for m in all_materials if m['id'] != self.item_id]
        material_names = [m['name'] for m in all_materials]

        def on_material_ok():
            sel_index = combo_material.current()
            if sel_index == -1:
                messagebox.showwarning("Ошибка", "Выберите материал")
                return
            qty = entry_quantity.get().strip()
            if not qty:
                messagebox.showwarning("Ошибка", "Введите количество")
                return
            mat = all_materials[sel_index]
            # Проверяем, есть ли уже такой материал, если да - обновляем количество
            for m in self.materials:
                if m['id'] == mat['id']:
                    m['quantity'] = qty
                    self.refresh_materials_table()
                    add_mat_window.destroy()
                    return
            # Добавляем новый
            self.materials.append({'id': mat['id'], 'name': mat['name'], 'quantity': qty})
            self.refresh_materials_table()
            add_mat_window.destroy()

        add_mat_window = tk.Toplevel(self.window)
        add_mat_window.title("Добавить материал")
        add_mat_window.grab_set()

        tk.Label(add_mat_window, text="Материал:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        combo_material = ttk.Combobox(add_mat_window, values=material_names, state='readonly')
        combo_material.grid(row=0, column=1, padx=5, pady=5)
        combo_material.current(0)

        tk.Label(add_mat_window, text="Количество:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        entry_quantity = tk.Entry(add_mat_window, width=20)
        entry_quantity.grid(row=1, column=1, padx=5, pady=5)

        btn_ok = tk.Button(add_mat_window, text="ОК", command=on_material_ok)
        btn_ok.grid(row=2, column=0, columnspan=2, pady=10)

    def on_edit_material(self):
        selected = self.materials_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите материал для редактирования")
            return
        mat_id = selected[0]
        mat = next((m for m in self.materials if m['id'] == mat_id), None)
        if not mat:
            messagebox.showerror("Ошибка", "Материал не найден")
            return

        def on_save():
            qty = entry_quantity.get().strip()
            if not qty:
                messagebox.showwarning("Ошибка", "Введите количество")
                return
            mat['quantity'] = qty
            self.refresh_materials_table()
            edit_win.destroy()

        edit_win = tk.Toplevel(self.window)
        edit_win.title("Редактировать материал")
        edit_win.grab_set()

        tk.Label(edit_win, text=f"Материал: {mat['name']}").grid(row=0, column=0, columnspan=2, padx=5, pady=5)

        tk.Label(edit_win, text="Количество:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        entry_quantity = tk.Entry(edit_win, width=20)
        entry_quantity.insert(0, mat['quantity'])
        entry_quantity.grid(row=1, column=1, padx=5, pady=5)

        btn_save = tk.Button(edit_win, text="Сохранить", command=on_save)
        btn_save.grid(row=2, column=0, columnspan=2, pady=10)

    def update_statistics(self):
        def parse_float(s):
            try:
                return float(s)
            except:
                return 0.0

        min_cost = 0.0
        max_cost = 0.0
        avg_cost = 0.0

        min_sell = parse_float(self.entry_price_min.get())
        max_sell = parse_float(self.entry_price_max.get())
        avg_sell = (min_sell + max_sell) / 2 if (min_sell and max_sell) else 0.0

        output_per_cycle = parse_float(self.entry_output_per_cycle.get())
        cycles_per_day = parse_float(self.entry_cycles_per_day.get())
        production_cost_per_day = parse_float(self.entry_production_cost_per_day.get())

        # Себестоимость материалов за цикл
        for mat in self.materials:
            mat_data = self.find_material_data(mat['id'])
            if not mat_data:
                continue
            qty = parse_float(mat['quantity'])
            price_min = parse_float(mat_data['price_min']) / 1000
            price_max = parse_float(mat_data['price_max']) / 1000
            price_avg = (price_min + price_max) / 2 if (price_min and price_max) else price_min or price_max

            min_cost += price_min * qty
            max_cost += price_max * qty
            avg_cost += price_avg * qty

        # Себестоимость материалов за день (умножаем на количество циклов)
        min_cost_day = min_cost * cycles_per_day
        max_cost_day = max_cost * cycles_per_day
        avg_cost_day = avg_cost * cycles_per_day

        # Общая себестоимость = себестоимость материалов + стоимость производства в день
        total_min_cost = min_cost_day + production_cost_per_day
        total_max_cost = max_cost_day + production_cost_per_day
        total_avg_cost = avg_cost_day + production_cost_per_day

        # Цена продажи за день (учитывая количество получаемого материала за цикл и циклы)
        # Предполагаем, что цена продажи указана за единицу товара
        # Итого продаётся output_per_cycle * cycles_per_day единиц
        total_output_per_day = output_per_cycle * cycles_per_day if output_per_cycle and cycles_per_day else 0
        if total_output_per_day > 0:
            sell_min_day = (min_sell / 1000) * total_output_per_day
            sell_max_day = (max_sell / 1000) * total_output_per_day
            sell_avg_day = (avg_sell / 1000) * total_output_per_day
        else:
            sell_min_day = sell_max_day = sell_avg_day = 0.0

        profit_min = sell_min_day - total_min_cost
        profit_avg = sell_avg_day - total_avg_cost
        profit_max = sell_max_day - total_max_cost

        text = (
            f"Себестоимость производства (в день):\n"
            f"  Мин: {total_min_cost:.2f}\n"
            f"  Средняя: {total_avg_cost:.2f}\n"
            f"  Макс: {total_max_cost:.2f}\n\n"
            f"Продажа (в день):\n"
            f"  Мин: {sell_min_day:.2f}\n"
            f"  Средняя: {sell_avg_day:.2f}\n"
            f"  Макс: {sell_max_day:.2f}\n\n"
            f"Прибыль (в день):\n"
            f"  Мин: {profit_min:.2f}\n"
            f"  Средняя: {profit_avg:.2f}\n"
            f"  Макс: {profit_max:.2f}\n"
        )

        self.stats_text.config(state='normal')
        self.stats_text.delete('1.0', tk.END)
        self.stats_text.insert(tk.END, text)
        self.stats_text.config(state='disabled')

    def find_material_data(self, mat_id):
        for cat in ['basic', 'derived']:
            for m in self.data_storage.data[cat]:
                if m['id'] == mat_id:
                    return m
        return None

    def save(self):
        name = self.entry_name.get().strip()
        price_min = self.entry_price_min.get().strip()
        price_max = self.entry_price_max.get().strip()
        output_per_cycle = self.entry_output_per_cycle.get().strip()
        cycles_per_day = self.entry_cycles_per_day.get().strip()
        production_cost_per_day = self.entry_production_cost_per_day.get().strip()

        if not name:
            messagebox.showwarning("Ошибка", "Введите название")
            return

        if self.item_id:
            item = next((x for x in self.data_storage.data['derived'] if x['id'] == self.item_id), None)
            if item:
                item['name'] = name
                item['price_min'] = price_min
                item['price_max'] = price_max
                item['output_per_cycle'] = output_per_cycle
                item['cycles_per_day'] = cycles_per_day
                item['production_cost_per_day'] = production_cost_per_day
                item['materials'] = self.materials
        else:
            new_id = str(uuid.uuid4())
            self.data_storage.data['derived'].append({
                'id': new_id,
                'name': name,
                'price_min': price_min,
                'price_max': price_max,
                'output_per_cycle': output_per_cycle,
                'cycles_per_day': cycles_per_day,
                'production_cost_per_day': production_cost_per_day,
                'materials': self.materials
            })

        self.data_storage.save_data()
        self.refresh_callback('derived')
        self.window.destroy()

    def on_delete_material(self):
        selected = self.materials_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите материал для удаления")
            return
        mat_id = selected[0]
        mat = next((m for m in self.materials if m['id'] == mat_id), None)
        if not mat:
            messagebox.showerror("Ошибка", "Материал не найден")
            return
        if messagebox.askyesno("Подтверждение", f"Удалить материал '{mat['name']}'?"):
            self.materials = [m for m in self.materials if m['id'] != mat_id]
            self.refresh_materials_table()

    def on_delete_resource(self):
        if not self.item_id:
            # Если ресурс ещё не сохранён, просто закрываем окно
            self.window.destroy()
            return
        if messagebox.askyesno("Подтверждение", "Удалить этот ресурс?"):
            self.data_storage.data['derived'] = [item for item in self.data_storage.data['derived'] if
                                                 item['id'] != self.item_id]
            self.data_storage.save_data()
            self.refresh_callback('derived')
            self.window.destroy()