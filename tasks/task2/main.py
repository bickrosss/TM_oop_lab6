#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
from tasks.task2.models import ProductCatalog
from tasks.task2.storage import ProductStorage
from tasks.task2.exceptions import *


def print_help() -> None:
    """Вывод справки по командам."""
    help_text = """
Доступные команды:
  add <товар> <магазин> <цена>  - Добавить товар
  list                          - Показать все товары
  stores                        - Показать все магазины
  select <магазин>              - Показать товары в магазине
  save <файл.xml>               - Сохранить в XML
  load <файл.xml>               - Загрузить из XML
  help                          - Показать справку
  exit                          - Выйти
"""
    print(help_text)


def main() -> None:
    """Главная функция программы."""
    # Настройка логирования
    logging.basicConfig(
        filename='catalog.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    catalog = ProductCatalog()
    
    print("Каталог товаров")
    print("=" * 40)
    print_help()
    
    while True:
        try:
            # Ввод команды
            command = input(">>> ").strip().lower()
            
            if command == 'exit':
                logging.info("Завершение работы.")
                print("Выход.")
                break
            
            elif command == 'help':
                print_help()
                logging.info("Вывод справки.")
            
            elif command == 'list':
                print(catalog)
                logging.info("Вывод списка товаров.")
            
            elif command == 'stores':
                stores = catalog.get_stores()
                if stores:
                    print("Магазины:")
                    for store in stores:
                        print(f"  - {store}")
                    logging.info(f"Список магазинов: {len(stores)}")
                else:
                    print("Нет магазинов.")
                    logging.info("Нет магазинов.")
            
            elif command.startswith('add '):
                parts = command.split(maxsplit=3)
                if len(parts) != 4:
                    print("Используйте: add товар магазин цена")
                    continue
                
                name, store = parts[1], parts[2]
                try:
                    price = float(parts[3])
                    catalog.add(name, store, price)
                    print(f"Добавлен: {name} в {store} за {price} руб.")
                    logging.info(f"Добавлен товар: {name}")
                except InvalidPriceError as e:
                    print(f"Ошибка: {e}")
                    logging.error(f"Некорректная цена: {parts[3]}")
                except ValueError as e:
                    print(f"Ошибка: {e}")
            
            elif command.startswith('select '):
                store = command.split(maxsplit=1)[1]
                try:
                    products = catalog.select(store)
                    print(f"Товары в '{store}':")
                    for p in products:
                        print(f"  - {p.name}: {p.price} руб.")
                    logging.info(f"Выборка магазина '{store}': {len(products)} товаров")
                except StoreNotFoundError:
                    print(f"Магазин '{store}' не найден.")
                    logging.warning(f"Магазин не найден: {store}")
            
            elif command.startswith('save '):
                filename = command.split(maxsplit=1)[1]
                ProductStorage.save(catalog.products, filename)
                print(f"Сохранено в {filename}")
                logging.info(f"Сохранение в {filename}")
            
            elif command.startswith('load '):
                filename = command.split(maxsplit=1)[1]
                products = ProductStorage.load(filename)
                catalog.products = products
                catalog.products.sort(key=lambda p: p.store)
                print(f"Загружено из {filename}: {len(products)} товаров")
                logging.info(f"Загрузка из {filename}")
            
            else:
                raise UnknownCommandError(command)
        
        except KeyboardInterrupt:
            print("\nПрервано.")
            break
        
        except UnknownCommandError as e:
            print(f"Ошибка: {e}")
            logging.error(f"Неизвестная команда: {e}")
        
        except (InvalidPriceError, StoreNotFoundError, DataFormatError) as e:
            print(f"Ошибка: {e}")
            logging.error(f"Ошибка: {e}")
        
        except Exception as e:
            print(f"Ошибка: {e}")
            logging.error(f"Ошибка: {e}")


if __name__ == '__main__':
    main()
