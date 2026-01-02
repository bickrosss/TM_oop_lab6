#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
from typing import List
from models import Product
from exceptions import DataFormatError, InvalidPriceError


class ProductStorage:
    """Класс для сохранения и загрузки товаров в XML."""
    
    @staticmethod
    def save(products: List[Product], filename: str) -> None:
        """Сохранить товары в XML файл."""
        root = ET.Element('products')
        
        for product in products:
            product_element = ET.Element('product')
            
            ET.SubElement(product_element, 'name').text = product.name
            ET.SubElement(product_element, 'store').text = product.store
            ET.SubElement(product_element, 'price').text = str(product.price)
            
            root.append(product_element)
        
        tree = ET.ElementTree(root)
        with open(filename, 'wb') as fout:
            fout.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
            tree.write(fout, encoding='utf-8')
    
    @staticmethod
    def load(filename: str) -> List[Product]:
        """Загрузить товары из XML файла."""
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
        except (ET.ParseError, FileNotFoundError) as e:
            raise DataFormatError(filename, f"ошибка чтения файла: {e}")
        
        products = []
        
        for product_element in root:
            try:
                name = product_element.find('name').text
                store = product_element.find('store').text
                price = float(product_element.find('price').text)
                
                product = Product(name=name, store=store, price=price)
                products.append(product)
                
            except (AttributeError, ValueError) as e:
                raise DataFormatError(filename, f"ошибка данных: {e}")
            except InvalidPriceError as e:
                raise DataFormatError(filename, f"некорректная цена: {e}")
        
        return products
