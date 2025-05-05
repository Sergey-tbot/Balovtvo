import tkinter as tk
from tkinter import ttk, messagebox
import uuid

class ProductWindow:
    def __init__(self, master, data_storage, item_id, refresh_callback):
        self.master = master
        self.data_storage = data_storage
        self.item_id = item_id
        self.refresh_callback = refresh_callback

        self.window = tk.Toplevel(master)
        self.window.title("Редактировать производство" if item_id else "Добавить производство")
        self.window.grab_set()

        left_frame = tk.Frame(self.window)
        left_frame.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        # Название производства
        tk.Label(left_frame, text="Название производства:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.entry_name = tk.Entry(left_frame, width=30)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)

        # Циклов в день
        tk.Label(left_frame, text="Циклов в день:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.entry_cycles_per_day = tk.Entry(left_frame, width=30)
        self.entry_cycles_per_day.grid(row=1, column=1, padx=5, pady=5)

        # Стоимость производства в день
        tk.Label(left_frame, text="Стоимость производства в день:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.entry_production_cost_per_day = tk.Entry(left_frame, width=30)
        self.entry_production_cost_per_day.grid(row=2, column=1, padx=5, pady=5)

        # --- Таблица входных материалов ---
        tk.Label(left_frame, text="Входные материалы (сырьё):").grid(row=3, column=0, columnspan=2, pady=(10, 0))
        self.materials_tree = ttk.Treeview(left_frame, columns=('Материал', 'Количество', 'Действие'), show='headings', height=6)
        self.materials_tree.heading('Материал', text='Материал')
        self.materials_tree.heading('Количество', text='Количество')
        self.materials_tree.heading('Действие', text='Действие')
        self.materials_tree.column('Материал', width=200)
        self.materials_tree.column('Количество', width=120, anchor='center')
        self.materials_tree.column('Действие', width=100, anchor='center')
        self.materials_tree.grid(row=4, column=0, columnspan=2, padx=5, pady=5)
        self.materials_tree.bind('<Button-1>', self.on_materials_tree_click)

        btn_materials_frame = tk.Frame(left_frame)
        btn_materials_frame.grid(row=5, column=0, columnspan=2, pady=5)

        btn_add_material = tk.Button(btn_materials_frame, text="Добавить материал", command=self.on_add_material)
        btn_add_material.pack(side='left', padx=5)

        btn_edit_material = tk.Button(btn_materials_frame, text="Редактировать материал", command=self.on_edit_material)
        btn_edit_material.pack(side='left', padx=5)

        btn_delete_material = tk.Button(btn_materials_frame, text="Удалить материал", command=self.on_delete_material)
        btn_delete_material.pack(side='left', padx=5)


        # --- Таблица выходных продуктов ---
        tk.Label(left_frame, text="Выходные продукты:").grid(row=6, column=0, columnspan=2, pady=(15, 0))
        self.outputs_tree = ttk.Treeview(left_frame, columns=('Продукт', 'Количество', 'Действие'), show='headings', height=6)
        self.outputs_tree.heading('Продукт', text='Продукт')
        self.outputs_tree.heading('Количество', text='Количество за цикл')
        self.outputs_tree.heading('Действие', text='Действие')
        self.outputs_tree.column('Продукт', width=200)
        self.outputs_tree.column('Количество', width=120, anchor='center')
        self.outputs_tree.column('Действие', width=100, anchor='center')
        self.outputs_tree.grid(row=7, column=0, columnspan=2, padx=5, pady=5)
        self.outputs_tree.bind('<Button-1>', self.on_outputs_tree_click)

        btn_outputs_frame = tk.Frame(left_frame)
        btn_outputs_frame.grid(row=8, column=0, columnspan=2, pady=5)

        btn_add_output = tk.Button(btn_outputs_frame, text="Добавить выходной продукт", command=self.on_add_output)
        btn_add_output.pack(side='left', padx=5)

        btn_edit_output = tk.Button(btn_outputs_frame, text="Редактировать выходной продукт", command=self.on_edit_output)
        btn_edit_output.pack(side='left', padx=5)

        btn_delete_output = tk.Button(btn_outputs_frame, text="Удалить выходной продукт", command=self.on_delete_output)
        btn_delete_output.pack(side='left', padx=5)

        # Кнопки сохранения и удаления
        btn_save = tk.Button(left_frame, text="Сохранить", command=self.save)
        btn_save.grid(row=9, column=0, pady=10)

        btn_delete_resource = tk.Button(left_frame, text="Удалить производство", fg='red', command=self.on_delete_resource)
        btn_delete_resource.grid(row=9, column=1, pady=10)

        # Данные
        self.materials = []
        self.outputs = []

        if item_id:
            self.load_item()
        else:
            self.refresh_materials_table()
            self.refresh_outputs_table()

    # --- Методы для работы с материалами (сырьём) ---
    def on_add_material(self):
        # Получаем список всех доступных ресурсов (базовых и производных), исключая текущее производство
        all_resources = self.data_storage.data['basic'] + self.data_storage.data['derived']
        if self.item_id:
            all_resources = [r for r in all_resources if r['id'] != self.item_id]
        resource_names = [r['name'] for r in all_resources]

        def on_ok():
            sel_index = combo_resource.current()
            if sel_index == -1:
                messagebox.showwarning("Ошибка", "Выберите ресурс")
                return
            qty = entry_quantity.get().strip()
            if not qty or not qty.replace('.', '', 1).isdigit():
                messagebox.showwarning("Ошибка", "Введите корректное количество")
                return
            res = all_resources[sel_index]
            # Проверяем, есть ли уже такой материал, если есть - обновляем количество
            for m in self.materials:
                if m['id'] == res['id']:
                    m['quantity'] = qty
                    self.refresh_materials_table()
                    add_win.destroy()
                    return
            # Добавляем новый материал
            self.materials.append({'id': res['id'], 'name': res['name'], 'quantity': qty})
            self.refresh_materials_table()
            add_win.destroy()

        add_win = tk.Toplevel(self.window)
        add_win.title("Добавить входной материал")
        add_win.grab_set()

        tk.Label(add_win, text="Ресурс:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        combo_resource = ttk.Combobox(add_win, values=resource_names, state='readonly')
        combo_resource.grid(row=0, column=1, padx=5, pady=5)
        if resource_names:
            combo_resource.current(0)

        tk.Label(add_win, text="Количество:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        entry_quantity = tk.Entry(add_win, width=20)
        entry_quantity.grid(row=1, column=1, padx=5, pady=5)

        btn_ok = tk.Button(add_win, text="ОК", command=on_ok)
        btn_ok.grid(row=2, column=0, columnspan=2, pady=10)

    def refresh_materials_table(self):
        self.materials_tree.delete(*self.materials_tree.get_children())
        for mat in self.materials:
            self.materials_tree.insert('', 'end', iid=mat['id'], values=(mat['name'], mat['quantity'], 'Редактировать'))

    def on_materials_tree_click(self, event):
        region = self.materials_tree.identify('region', event.x, event.y)
        if region != 'cell':
            return
        row_id = self.materials_tree.identify_row(event.y)
        col = self.materials_tree.identify_column(event.x)
        if col == '#3' and row_id:
            self.edit_material(row_id)

    def edit_material(self, mat_id):
        # Аналогично редактированию выходных продуктов
        pass  # Реализуйте по аналогии с выходными продуктами

    def on_add_material(self):
        # Аналогично добавлению выходных продуктов, но для материалов
        pass  # Реализуйте по аналогии с выходными продуктами

    def on_edit_material(self):
        selected = self.materials_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите материал для редактирования")
            return
        self.edit_material(selected[0])

    def on_delete_material(self):
        selected = self.materials_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите материал для удаления")
            return
        mat_id = selected[0]
        self.materials = [m for m in self.materials if m['id'] != mat_id]
        self.refresh_materials_table()

    # --- Методы для работы с выходными продуктами ---
    def refresh_outputs_table(self):
        self.outputs_tree.delete(*self.outputs_tree.get_children())
        for output in self.outputs:
            self.outputs_tree.insert('', 'end', iid=output['id'], values=(output['name'], output['quantity'], 'Редактировать'))

    def on_outputs_tree_click(self, event):
        region = self.outputs_tree.identify('region', event.x, event.y)
        if region != 'cell':
            return
        row_id = self.outputs_tree.identify_row(event.y)
        col = self.outputs_tree.identify_column(event.x)
        if col == '#3' and row_id:
            self.edit_output(row_id)

    def edit_output(self, output_id):
        # Аналогично редактированию материалов
        pass  # Реализуйте по аналогии с материалами

    def on_add_output(self):
        # Аналогично добавлению материалов
        pass  # Реализуйте по аналогии с материалами

    def on_edit_output(self):
        selected = self.outputs_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите выходной продукт для редактирования")
            return
        self.edit_output(selected[0])

    def on_delete_output(self):
        selected = self.outputs_tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите выходной продукт для удаления")
            return
        output_id = selected[0]
        self.outputs = [o for o in self.outputs if o['id'] != output_id]
        self.refresh_outputs_table()

    # --- Загрузка и сохранение ---
    def load_item(self):
        item = next((x for x in self.data_storage.data['derived'] if x['id'] == self.item_id), None)
        if not item:
            messagebox.showerror("Ошибка", "Элемент не найден")
            self.window.destroy()
            return
        self.entry_name.insert(0, item['name'])
        self.entry_cycles_per_day.insert(0, item.get('cycles_per_day', ''))
        self.entry_production_cost_per_day.insert(0, item.get('production_cost_per_day', ''))
        self.materials = item.get('materials', [])
        self.outputs = item.get('outputs', [])
        self.refresh_materials_table()
        self.refresh_outputs_table()

    def save(self):
        name = self.entry_name.get().strip()
        cycles_per_day = self.entry_cycles_per_day.get().strip()
        production_cost_per_day = self.entry_production_cost_per_day.get().strip()

        if not name:
            messagebox.showwarning("Ошибка", "Введите название производства")
            return

        if self.item_id:
            item = next((x for x in self.data_storage.data['derived'] if x['id'] == self.item_id), None)
            if item:
                item['name'] = name
                item['cycles_per_day'] = cycles_per_day
                item['production_cost_per_day'] = production_cost_per_day
                item['materials'] = self.materials
                item['outputs'] = self.outputs
        else:
            new_id = str(uuid.uuid4())
            self.data_storage.data['derived'].append({
                'id': new_id,
                'name': name,
                'cycles_per_day': cycles_per_day,
                'production_cost_per_day': production_cost_per_day,
                'materials': self.materials,
                'outputs': self.outputs
            })

        self.data_storage.save_data()
        self.refresh_callback('derived')
        self.window.destroy()

    def on_delete_resource(self):
        if not self.item_id:
            self.window.destroy()
            return
        if messagebox.askyesno("Подтверждение", "Удалить это производство?"):
            self.data_storage.data['derived'] = [item for item in self.data_storage.data['derived'] if item['id'] != self.item_id]
            self.data_storage.save_data()
            self.refresh_callback('derived')
            self.window.destroy()
