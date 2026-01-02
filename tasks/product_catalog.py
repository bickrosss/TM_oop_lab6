#!/usr/bin/env python3
import logging
import xml.etree.ElementTree as ET


class Product:
    def __init__(self, name, store, price):
        if price <= 0:
            raise ValueError(f"Некорректная цена: {price}")
        self.name, self.store, self.price = name, store, price


class Catalog:
    def __init__(self):
        self.products = []
    
    def add(self, name, store, price):
        self.products.append(Product(name, store, price))
        self.products.sort(key=lambda p: p.store)
        logging.info(f"Добавлен: {name} в {store} за {price}")
    
    def select(self, store):
        result = [p for p in self.products if p.store == store]
        if not result:
            logging.warning(f"Магазин не найден: {store}")
            raise ValueError(f"Магазин '{store}' не найден")
        return result
    
    def save(self, file):
        root = ET.Element('products')
        for p in self.products:
            prod = ET.Element('product')
            ET.SubElement(prod, 'name').text = p.name
            ET.SubElement(prod, 'store').text = p.store
            ET.SubElement(prod, 'price').text = str(p.price)
            root.append(prod)
        ET.ElementTree(root).write(file, encoding='utf-8', xml_declaration=True)
        logging.info(f"Сохранено в {file}")
    
    def load(self, file):
        tree = ET.parse(file)
        self.products = [
            Product(
                e.find('name').text,
                e.find('store').text,
                float(e.find('price').text)
            ) for e in tree.findall('product')
        ]
        self.products.sort(key=lambda p: p.store)
        logging.info(f"Загружено из {file}: {len(self.products)} товаров")


def main():
    logging.basicConfig(filename='catalog.log', level=logging.INFO, format='%(asctime)s - %(message)s')
    cat = Catalog()
    
    print("Каталог товаров (add, select, list, save, load, exit)")
    
    while True:
        try:
            cmd = input("> ").strip()
            if cmd == 'exit':
                break
            elif cmd == 'list':
                for i, p in enumerate(cat.products, 1):
                    print(f"{i}. {p.name} | {p.store} | {p.price} руб.")
            elif cmd.startswith('add '):
                parts = cmd.split()
                if len(parts) != 4:
                    print("Формат: add товар магазин цена")
                    continue
                try:
                    cat.add(parts[1], parts[2], float(parts[3]))
                    print("OK")
                except ValueError as e:
                    print(f"Ошибка: {e}")
            elif cmd.startswith('select '):
                store = cmd[7:]
                try:
                    for p in cat.select(store):
                        print(f"  - {p.name}: {p.price} руб.")
                except ValueError as e:
                    print(e)
            elif cmd.startswith('save '):
                cat.save(cmd[5:])
                print("Сохранено")
            elif cmd.startswith('load '):
                cat.load(cmd[5:])
                print("Загружено")
            else:
                print("Неизвестная команда")
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == '__main__':
    main()
