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
            
            login_element = ET.SubElement(user_element, 'login')
            login_element.text = user.login
            
            password_hash_element = ET.SubElement(user_element, 'password_hash')
            password_hash_element.text = user.password_hash
            
            salt_element = ET.SubElement(user_element, 'salt')
            salt_element.text = user.salt
            
            authenticated_element = ET.SubElement(user_element, 'authenticated')
            authenticated_element.text = str(user.authenticated).lower()
            
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
            login = None
            password_hash = None
            salt = None
            authenticated = False
            
            for element in user_element:
                if element.tag == 'login':
                    login = element.text
                elif element.tag == 'password_hash':
                    password_hash = element.text
                elif element.tag == 'salt':
                    salt = element.text
                elif element.tag == 'authenticated':
                    try:
                        authenticated = element.text.lower() == 'true'
                    except AttributeError:
                        authenticated = False
            
            if all([login, password_hash, salt]):
                # Создаем нового пользователя с нужным состоянием
                user = User(
                    login=login, 
                    password_hash=password_hash,
                    salt=salt,
                    authenticated=authenticated
                )
                users.append(user)
            else:
                raise DataFormatError(filename, "неполные данные пользователя")
        
        return users
