#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
from typing import List
from models import User
from exceptions import DataFormatError


class UserStorage:
    """Класс для сохранения и загрузки пользователей в XML."""
    
    @staticmethod
    def save(users: List[User], filename: str) -> None:
        """Сохранить пользователей в XML файл."""
        root = ET.Element('users')
        
        for user in users:
            user_element = ET.Element('user')
            
            ET.SubElement(user_element, 'login').text = user.login
            ET.SubElement(user_element, 'authenticated').text = str(user.authenticated).lower()
            
            root.append(user_element)
        
        tree = ET.ElementTree(root)
        with open(filename, 'wb') as fout:
            fout.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
            tree.write(fout, encoding='utf-8')
    
    @staticmethod
    def load(filename: str) -> List[User]:
        """Загрузить пользователей из XML файла."""
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
        except (ET.ParseError, FileNotFoundError) as e:
            raise DataFormatError(filename, f"ошибка чтения файла: {e}")
        
        users = []
        
        for user_element in root:
            try:
                login = user_element.find('login').text
                auth_text = user_element.find('authenticated').text
                authenticated = auth_text.lower() == 'true'
                
                user = User(login=login, authenticated=authenticated)
                users.append(user)
                
            except (AttributeError, ValueError) as e:
                raise DataFormatError(filename, f"ошибка данных: {e}")
        
        return users
