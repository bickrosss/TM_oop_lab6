#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tempfile

import pytest
from exceptions import (
    InvalidPriceError, 
    StoreNotFoundError, 
    UnknownCommandError, 
    DataFormatError
)
from models import Product, ProductCatalog
from storage import ProductStorage


def test_product_creation():
    """Тест создания товара"""
    product = Product("Молоко", "Пятерочка", 85.50)
    
    assert product.name == "Молоко"
    assert product.store == "Пятерочка"
    assert product.price == 85.50


def test_product_invalid_price():
    """Тест создания товара с некорректной ценой"""
    with pytest.raises(InvalidPriceError) as exc_info:
        Product("Товар", "Магазин", -10.0)
    
    assert "цена должна быть больше 0" in str(exc_info.value)


def test_product_zero_price():
    """Тест создания товара с нулевой ценой"""
    with pytest.raises(InvalidPriceError):
        Product("Товар", "Магазин", 0.0)


def test_productcatalog_add_valid():
    """Тест добавления корректного товара"""
    catalog = ProductCatalog()
    product = catalog.add("Хлеб", "Пятерочка", 45.00)
    
    assert len(catalog.products) == 1
    assert catalog.products[0].name == "Хлеб"
    assert catalog.products[0].price == 45.00


def test_productcatalog_add_invalid_price():
    """Тест добавления товара с некорректной ценой"""
    catalog = ProductCatalog()
    
    with pytest.raises(InvalidPriceError) as exc_info:
        catalog.add("Товар", "Магазин", -5.0)
    
    assert "цена должна быть больше 0" in str(exc_info.value)


def test_productcatalog_add_empty_name():
    """Тест добавления товара с пустым названием"""
    catalog = ProductCatalog()
    
    with pytest.raises(ValueError) as exc_info:
        catalog.add("", "Магазин", 100.0)
    
    assert "не могут быть пустыми" in str(exc_info.value)


def test_productcatalog_select_existing_store():
    """Тест выборки товаров существующего магазина"""
    catalog = ProductCatalog()
    catalog.add("Молоко", "Пятерочка", 85.50)
    catalog.add("Хлеб", "Пятерочка", 45.00)
    catalog.add("Кофе", "Магнит", 350.00)
    
    products = catalog.select("Пятерочка")
    
    assert len(products) == 2
    assert all(p.store == "Пятерочка" for p in products)


def test_productcatalog_select_nonexisting_store():
    """Тест выборки товаров несуществующего магазина"""
    catalog = ProductCatalog()
    catalog.add("Молоко", "Пятерочка", 85.50)
    
    with pytest.raises(StoreNotFoundError) as exc_info:
        catalog.select("Дикси")
    
    assert "'Дикси' -> магазин не найден" in str(exc_info.value)


def test_productcatalog_select_case_insensitive():
    """Тест выборки магазина без учета регистра"""
    catalog = ProductCatalog()
    catalog.add("Молоко", "Пятерочка", 85.50)
    
    products = catalog.select("пятерочка")  # строчные буквы
    assert len(products) == 1
    assert products[0].store == "Пятерочка"


def test_productcatalog_get_stores():
    """Тест получения списка магазинов"""
    catalog = ProductCatalog()
    catalog.add("Молоко", "Пятерочка", 85.50)
    catalog.add("Хлеб", "Пятерочка", 45.00)
    catalog.add("Кофе", "Магнит", 350.00)
    catalog.add("Чай", "Магнит", 180.00)
    
    stores = catalog.get_stores()
    
    assert len(stores) == 2
    assert "Магнит" in stores
    assert "Пятерочка" in stores
    assert stores == sorted(stores)  # Проверяем сортировку


def test_productcatalog_str_empty():
    """Тест строкового представления пустого каталога"""
    catalog = ProductCatalog()
    result = str(catalog)
    
    assert "Каталог товаров пуст" in result


def test_productcatalog_str_with_products():
    """Тест строкового представления с товарами"""
    catalog = ProductCatalog()
    catalog.add("Молоко", "Пятерочка", 85.50)
    
    result = str(catalog)
    
    assert "Молоко" in result
    assert "Пятерочка" in result
    assert "85.50" in result
    assert "Название товара" in result
    assert "Магазин" in result
    assert "Цена, руб." in result


def test_productcatalog_sorting():
    """Тест сортировки товаров по магазину"""
    catalog = ProductCatalog()
    catalog.add("Кофе", "Магнит", 350.00)      # 2-й по алфавиту
    catalog.add("Молоко", "Пятерочка", 85.50)  # 3-й по алфавиту
    catalog.add("Вода", "Ашан", 40.00)        # 1-й по алфавиту
    
    assert catalog.products[0].store == "Ашан"
    assert catalog.products[1].store == "Магнит"
    assert catalog.products[2].store == "Пятерочка"


def test_productstorage_save_and_load():
    """Тест сохранения и загрузки товаров"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        temp_filename = f.name
    
    try:
        # Создаем тестовые товары
        products = [
            Product("Молоко", "Пятерочка", 85.50),
            Product("Хлеб", "Пятерочка", 45.00),
            Product("Кофе", "Магнит", 350.00)
        ]
        
        # Сохраняем
        ProductStorage.save(products, temp_filename)
        
        # Проверяем что файл создан
        assert os.path.exists(temp_filename)
        
        # Загружаем
        loaded_products = ProductStorage.load(temp_filename)
        
        # Проверяем
        assert len(loaded_products) == 3
        
        # Проверяем первый товар
        assert loaded_products[0].name == "Молоко"
        assert loaded_products[0].store == "Пятерочка"
        assert loaded_products[0].price == 85.50
        
        # Проверяем второй товар
        assert loaded_products[1].name == "Хлеб"
        assert loaded_products[1].store == "Пятерочка"
        assert loaded_products[1].price == 45.00
        
        # Проверяем третий товар
        assert loaded_products[2].name == "Кофе"
        assert loaded_products[2].store == "Магнит"
        assert loaded_products[2].price == 350.00
        
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def test_productstorage_load_invalid_xml():
    """Тест загрузки некорректного XML"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write("Это не XML файл")
        temp_filename = f.name
    
    try:
        with pytest.raises(DataFormatError) as exc_info:
            ProductStorage.load(temp_filename)
        
        assert "некорректный формат данных" in str(exc_info.value)
        
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def test_productstorage_load_missing_fields():
    """Тест загрузки XML с отсутствующими полями"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write('''<?xml version="1.0" encoding="utf-8"?>
<products>
  <product>
    <name>Товар</name>
    <!-- store отсутствует -->
    <price>100.0</price>
  </product>
</products>''')
        temp_filename = f.name
    
    try:
        with pytest.raises(DataFormatError) as exc_info:
            ProductStorage.load(temp_filename)
        
        assert "ошибка данных" in str(exc_info.value)
        
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def test_productstorage_load_invalid_price():
    """Тест загрузки XML с некорректной ценой"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write('''<?xml version="1.0" encoding="utf-8"?>
<products>
  <product>
    <name>Товар</name>
    <store>Магазин</store>
    <price>не число</price>
  </product>
</products>''')
        temp_filename = f.name
    
    try:
        with pytest.raises(DataFormatError) as exc_info:
            ProductStorage.load(temp_filename)
        
        assert "ошибка данных" in str(exc_info.value)
        
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def test_exception_messages():
    """Тест сообщений исключений"""
    # InvalidPriceError
    exc1 = InvalidPriceError(-10, "цена должна быть больше 0")
    assert "'-10' -> цена должна быть больше 0" in str(exc1)
    
    # StoreNotFoundError
    exc2 = StoreNotFoundError("Дикси")
    assert "'Дикси' -> магазин не найден" in str(exc2)
    
    # UnknownCommandError
    exc3 = UnknownCommandError("invalid")
    assert "'invalid' -> неизвестная команда" in str(exc3)
    
    # DataFormatError
    exc4 = DataFormatError("file.xml")
    assert "'file.xml' -> некорректный формат данных" in str(exc4)


def test_productcatalog_store_stats():
    """Тест статистики по магазину"""
    catalog = ProductCatalog()
    catalog.add("Молоко", "Пятерочка", 85.50)
    catalog.add("Хлеб", "Пятерочка", 45.00)
    catalog.add("Сыр", "Пятерочка", 320.00)
    
    stats = catalog.get_store_stats("Пятерочка")
    
    assert stats['store'] == "Пятерочка"
    assert stats['total_products'] == 3
    assert stats['min_price'] == 45.00
    assert stats['max_price'] == 320.00
    assert stats['avg_price'] == pytest.approx((85.50 + 45.00 + 320.00) / 3)


def test_productcatalog_store_stats_nonexisting():
    """Тест статистики несуществующего магазина"""
    catalog = ProductCatalog()
    catalog.add("Молоко", "Пятерочка", 85.50)
    
    with pytest.raises(StoreNotFoundError):
        catalog.get_store_stats("Дикси")
