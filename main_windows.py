import tkinter as tk
from tkinter import ttk
from basic_windows import BasicWindow
from product_windows import ProductWindow
from data_storage import DataStorage


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Ресурсы")

        self.data_storage = DataStorage()

        self.frame_basic = ttk.LabelFrame(root, text="Базовые ресурсы")
        self.frame_basic.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.frame_derived = ttk.LabelFrame(root, text="Производные")
        self.frame_derived.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

        btn_add_basic = tk.Button(self.frame_basic, text="Добавить", command=self.open_basic_add)
        btn_add_basic.pack(pady=5)

        btn_add_derived = tk.Button(self.frame_derived, text="Добавить", command=self.open_product_add)
        btn_add_derived.pack(pady=5)

        columns_basic = ('Название', 'Цена мин.', 'Цена макс.', 'Действие')
        self.tree_basic = ttk.Treeview(self.frame_basic, columns=columns_basic, show='headings', height=10)
        for col in columns_basic:
            self.tree_basic.heading(col, text=col)
            self.tree_basic.column(col, width=120, anchor='center')
        self.tree_basic.pack(padx=5, pady=5)
        self.tree_basic.bind('<Button-1>', self.on_basic_click)

        columns_derived = ('Название', 'Цена мин.', 'Цена макс.', 'Прибыль', 'Действие')
        self.tree_derived = ttk.Treeview(self.frame_derived, columns=columns_derived, show='headings', height=10)
        for col in columns_derived:
            self.tree_derived.heading(col, text=col)
            self.tree_derived.column(col, width=120, anchor='center')
        self.tree_derived.pack(padx=5, pady=5)
        self.tree_derived.bind('<Button-1>', self.on_derived_click)

        self.summary_frame = ttk.Frame(root)
        self.summary_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=10, pady=10)

        self.summary_text = tk.Text(self.summary_frame, height=10, state='disabled')
        self.summary_text.pack(fill='both', expand=True)

        self.tree_derived.bind('<<TreeviewSelect>>', self.on_derived_select)

        self.refresh_tables()

        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)
        root.rowconfigure(1, weight=0)

    def refresh_tables(self):
        self.refresh_table('basic')
        self.refresh_table('derived')

    def refresh_table(self, cat_key):
        tree = self.tree_basic if cat_key == 'basic' else self.tree_derived
        tree.delete(*tree.get_children())
        items = self.data_storage.data[cat_key]
        for item in items:
            profit = self.calculate_profit(item) if cat_key == 'derived' else ''
            if cat_key == 'basic':
                tree.insert('', 'end', iid=str(item['id']),
                            values=(item['name'], item['price_min'], item['price_max'], 'Редактировать'))
            else:
                tree.insert('', 'end', iid=str(item['id']),
                            values=(item['name'], item['price_min'], item['price_max'], profit, 'Редактировать'))

    def calculate_profit(self, item):
        try:
            total_cost, total_revenue = self.calculate_total_cost_revenue(item['id'])
            return f"{total_revenue - total_cost:.2f}"
        except Exception as e:
            print(f"Error calculating profit: {e}")
            return "N/A"

    def calculate_total_cost_revenue(self, product_id, multiplier=1.0):
        product = self.data_storage.find_material(product_id)
        if not product:
            return 0.0, 0.0

        try:
            cycles_per_day = float(product.get('cycles_per_day', 0))
            production_cost_per_day = float(product.get('production_cost_per_day', 0))
        except Exception:
            cycles_per_day = 0
            production_cost_per_day = 0

        # Себестоимость материалов (сырья)
        cost_materials = 0.0
        for mat in product.get('materials', []):
            mat_id = mat['id']
            try:
                qty = float(mat.get('quantity', 0)) * multiplier
            except Exception:
                qty = 0
            mat_cost, _ = self.calculate_total_cost_revenue(mat_id, qty)
            cost_materials += mat_cost

        # Себестоимость производства (стоимость в день)
        production_cost_total = production_cost_per_day * multiplier

        total_cost = cost_materials + production_cost_total

        # Доход от всех выходных продуктов
        total_revenue = 0.0
        for output in product.get('outputs', []):
            try:
                qty_out = float(output.get('quantity', 0)) * cycles_per_day * multiplier
            except Exception:
                qty_out = 0
            out_data = self.data_storage.find_material(output['id'])
            if not out_data:
                continue
            try:
                price_avg = (float(out_data.get('price_min', 0)) + float(out_data.get('price_max', 0))) / 2 / 1000
            except Exception:
                price_avg = 0
            total_revenue += price_avg * qty_out

        return total_cost, total_revenue

    def get_material_cost(self, material):
        mat_id = material.get('id')
        if not mat_id:
            return 0
        mat_data = self.data_storage.find_material(mat_id)
        if not mat_data:
            return 0
        price_avg = (float(mat_data['price_min']) + float(mat_data['price_max'])) / 2 / 1000
        quantity = float(material.get('quantity', 0))
        return price_avg * quantity

    def on_basic_click(self, event):
        self._on_tree_click(event, 'basic')

    def on_derived_click(self, event):
        self._on_tree_click(event, 'derived')

    def _on_tree_click(self, event, cat_key):
        tree = self.tree_basic if cat_key == 'basic' else self.tree_derived
        region = tree.identify('region', event.x, event.y)
        if region != 'cell':
            return
        row_id = tree.identify_row(event.y)
        col = tree.identify_column(event.x)
        expected_col = '#4' if cat_key == 'basic' else '#5'
        if col == expected_col and row_id:
            if cat_key == 'basic':
                BasicWindow(self.root, self.data_storage, row_id, self.refresh_table)
            else:
                ProductWindow(self.root, self.data_storage, row_id, self.refresh_table)

    def open_basic_add(self):
        BasicWindow(self.root, self.data_storage, None, self.refresh_table)

    def open_product_add(self):
        ProductWindow(self.root, self.data_storage, None, self.refresh_table)

    def get_all_materials(self, materials, parent_multiplier=1.0, depth=0, max_depth=10):
        if depth > max_depth:
            return []
        all_mats = []
        for mat in materials:
            mat_data = self.data_storage.find_material(mat['id'])
            if not mat_data:
                continue
            try:
                qty_per_cycle = float(mat.get('quantity', 0))
            except Exception:
                qty_per_cycle = 0.0
            total_qty = qty_per_cycle * parent_multiplier
            all_mats.append({
                'id': mat_data['id'],
                'name': '  ' * depth + mat_data['name'],
                'quantity': total_qty
            })
            if mat_data.get('materials'):
                all_mats.extend(self.get_all_materials(mat_data['materials'], total_qty, depth + 1, max_depth))
        return all_mats

    def on_derived_select(self, event):
        item_id = self.tree_derived.selection()[0] if self.tree_derived.selection() else None
        if not item_id:
            return

        item = next((x for x in self.data_storage.data['derived'] if x['id'] == item_id), None)
        if not item:
            return

        try:
            cycles_per_day = float(item.get('cycles_per_day', 1))
        except Exception:
            cycles_per_day = 1.0

        all_materials = self.get_all_materials(item['materials'], parent_multiplier=cycles_per_day)

        text = f"Ресурс: {item['name']}\n"
        text += f"Выход в день: {float(item.get('output_per_cycle', 0)) * cycles_per_day:.2f}\n"
        text += "Используемые материалы:\n"
        for mat in all_materials:
            text += f"- {mat['name']}: {mat['quantity']:.2f} ед. (Стоимость: {self.get_material_cost(mat):.2f}/день)\n"

        try:
            profit = float(self.calculate_profit(item))
            text += f"\nПрибыльность: {profit:.2f} / день"
        except:
            text += "\nПрибыльность: N/A"

        self.summary_text.config(state='normal')
        self.summary_text.delete('1.0', tk.END)
        self.summary_text.insert(tk.END, text)
        self.summary_text.config(state='disabled')


if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
