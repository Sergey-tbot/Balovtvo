import os
import xml.etree.ElementTree as ET
import uuid

documents = os.path.join(os.path.expanduser('~'), 'Documents')
target_dir = os.path.join(documents, 'Баловство')
os.makedirs(target_dir, exist_ok=True)
file_path = os.path.join(target_dir, 'data.xml')


class DataStorage:
    def __init__(self):
        self.data = {
            'basic': [],
            'derived': []
        }
        self.load_data()

    def load_data(self):
        for key in self.data:
            self.data[key].clear()
        if not os.path.exists(file_path):
            return
        tree = ET.parse(file_path)
        root = tree.getroot()
        for category in root.findall('category'):
            cat_name = category.get('name')
            if cat_name not in self.data:
                continue
            for elem in category.findall('item'):
                item_id = elem.get('id') or str(uuid.uuid4())
                name = elem.find('name').text if elem.find('name') is not None else ''
                price_min = elem.find('price_min').text if elem.find('price_min') is not None else ''
                price_max = elem.find('price_max').text if elem.find('price_max') is not None else ''
                materials = []
                if cat_name == 'derived':
                    mats_elem = elem.find('materials')
                    if mats_elem is not None:
                        for mat in mats_elem.findall('material'):
                            mat_id = mat.get('id') or str(uuid.uuid4())
                            mat_name = mat.find('name').text if mat.find('name') is not None else ''
                            qty = mat.find('quantity').text if mat.find('quantity') is not None else ''
                            materials.append({'id': mat_id, 'name': mat_name, 'quantity': qty})
                output_per_cycle = elem.find('output_per_cycle').text if elem.find('output_per_cycle') is not None else ''
                cycles_per_day = elem.find('cycles_per_day').text if elem.find('cycles_per_day') is not None else ''
                production_cost_per_day = elem.find('production_cost_per_day').text if elem.find('production_cost_per_day') is not None else ''
                self.data[cat_name].append({
                    'id': item_id,
                    'name': name,
                    'price_min': price_min,
                    'price_max': price_max,
                    'materials': materials,
                    'output_per_cycle': output_per_cycle,
                    'cycles_per_day': cycles_per_day,
                    'production_cost_per_day': production_cost_per_day
                })

    def save_data(self):
        root = ET.Element('data')
        for cat_name, items in self.data.items():
            cat_elem = ET.SubElement(root, 'category', {'name': cat_name})
            for item in items:
                item_elem = ET.SubElement(cat_elem, 'item', {'id': item['id']})
                ET.SubElement(item_elem, 'name').text = item['name']
                ET.SubElement(item_elem, 'price_min').text = item['price_min']
                ET.SubElement(item_elem, 'price_max').text = item['price_max']
                if cat_name == 'derived':
                    ET.SubElement(item_elem, 'output_per_cycle').text = item.get('output_per_cycle', '')
                    ET.SubElement(item_elem, 'cycles_per_day').text = item.get('cycles_per_day', '')
                    ET.SubElement(item_elem, 'production_cost_per_day').text = item.get('production_cost_per_day', '')
                    mats_elem = ET.SubElement(item_elem, 'materials')
                    for mat in item.get('materials', []):
                        mat_elem = ET.SubElement(mats_elem, 'material', {'id': mat['id']})
                        ET.SubElement(mat_elem, 'name').text = mat['name']
                        ET.SubElement(mat_elem, 'quantity').text = mat['quantity']
        tree = ET.ElementTree(root)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)

    def find_material(self, mat_id):
        for cat in ['basic', 'derived']:
            for item in self.data[cat]:
                if item['id'] == mat_id:
                    return item
        return None
