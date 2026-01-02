#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List
from exceptions import InvalidPriceError, StoreNotFoundError


@dataclass(frozen=True)
class Product:
    """Класс товара."""
    name: str
    store: str
    price: float
    
    def __post_init__(self):
        """Валидация цены после инициализации."""
        if self.price <= 0:
            raise InvalidPriceError(self.price, "цена должна быть больше 0")


@dataclass
class ProductCatalog:
    """Класс для управления каталогом товаров."""
    products: List[Product] = field(default_factory=list)
    
    def add(self, name: str, store: str, price: float) -> Product:
        """Добавить новый товар."""
        # Валидация ввода
        if not name or not store:
            raise ValueError("Название товара и магазин не могут быть пустыми")
        
        if price <= 0:
            raise InvalidPriceError(price, "цена должна быть больше 0")
        
        product = Product(name=name, store=store, price=price)
        self.products.append(product)
        self.products.sort(key=lambda p: p.store)  # Сортировка по магазину
        return product
    
    def select(self, store: str) -> List[Product]:
        """Выбрать все товары в указанном магазине."""
        if not store:
            raise ValueError("Название магазина не может быть пустым")
        
        result = [p for p in self.products if p.store.lower() == store.lower()]
        
        if not result:
            raise StoreNotFoundError(store)
        
        return result
    
    def get_stores(self) -> List[str]:
        """Получить список всех уникальных магазинов."""
        return sorted(set(p.store for p in self.products))
    
    def __str__(self) -> str:
        """Представление всех товаров в виде таблицы."""
        if not self.products:
            return "Каталог товаров пуст."
        
        table = []
        line = '+{}+{}+{}+{}+'.format('-' * 4, '-' * 25, '-' * 20, '-' * 12)
        table.append(line)
        table.append('| {:^4} | {:^25} | {:^20} | {:^12} |'.format(
            "№", "Название товара", "Магазин", "Цена, руб."))
        table.append(line)
        
        for idx, product in enumerate(self.products, 1):
            table.append('| {:^4} | {:^25} | {:^20} | {:^12.2f} |'.format(
                idx, product.name[:25], product.store[:20], product.price))
        
        table.append(line)
        return '\n'.join(table)
