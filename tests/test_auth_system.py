#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tempfile

import pytest
from exceptions import (
    UnauthorizedAccessError, 
    InvalidLoginError, 
    UnknownCommandError, 
    DataFormatError
)
from models import User, UserManager
from storage import UserStorage


def test_user_creation():
    """Тест создания пользователя"""
    user = User("testuser", False)
    assert user.login == "testuser"
    assert user.authenticated == False


def test_user_access_resource_unauthorized():
    """Тест доступа без авторизации"""
    user = User("guest", False)
    
    with pytest.raises(UnauthorizedAccessError) as exc_info:
        user.access_resource()
    
    assert "guest" in str(exc_info.value)
    assert "доступ запрещён" in str(exciss_info.value)


def test_user_access_resource_authorized():
    """Тест доступа с авторизацией"""
    user = User("admin", True)
    result = user.access_resource()
    
    assert "admin" in result
    assert "Доступ разрешён" in result


def test_user_authenticate_success():
    """Тест успешной аутентификации"""
    user = User("testuser", False)
    user.authenticate("password123")
    
    assert user.authenticated == True


def test_user_authenticate_failure():
    """Тест неудачной аутентификации"""
    user = User("testuser", False)
    
    with pytest.raises(InvalidLoginError) as exc_info:
        user.authenticate("wrongpassword")
    
    assert "testuser" in str(exc_info.value)
    assert "неверный пароль" in str(exc_info.value)


def test_usermanager_add_valid():
    """Тест добавления корректного пользователя"""
    manager = UserManager()
    user = manager.add("newuser")
    
    assert len(manager.users) == 1
    assert manager.users[0].login == "newuser"
    assert manager.users[0].authenticated == False


def test_usermanager_add_invalid_login():
    """Тест добавления пользователя с некорректным логином"""
    manager = UserManager()
    
    with pytest.raises(InvalidLoginError):
        manager.add("ab")  # Слишком короткий логин


def test_usermanager_add_duplicate_login():
    """Тест добавления пользователя с существующим логином"""
    manager = UserManager()
    manager.add("user1")
    
    with pytest.raises(InvalidLoginError) as exc_info:
        manager.add("user1")
    
    assert "логин уже существует" in str(exc_info.value)


def test_usermanager_find_existing():
    """Тест поиска существующего пользователя"""
    manager = UserManager()
    manager.add("user1")
    manager.add("user2")
    
    user = manager.find("user1")
    assert user.login == "user1"


def test_usermanager_find_non_existing():
    """Тест поиска несуществующего пользователя"""
    manager = UserManager()
    manager.add("user1")
    
    with pytest.raises(InvalidLoginError) as exc_info:
        manager.find("nonexistent")
    
    assert "пользователь не найден" in str(exc_info.value)


def test_usermanager_authenticate():
    """Тест аутентификации пользователя"""
    manager = UserManager()
    manager.add("testuser")
    
    user = manager.authenticate("testuser", "password123")
    assert user.authenticated == True


def test_usermanager_logout():
    """Тест выхода из системы"""
    manager = UserManager()
    manager.add("testuser")
    manager.authenticate("testuser", "password123")
    
    user = manager.logout("testuser")
    assert user.authenticated == False


def test_usermanager_select_authenticated():
    """Тест выбора аутентифицированных пользователей"""
    manager = UserManager()
    manager.add("user1")
    manager.add("user2")
    manager.add("user3")
    
    manager.authenticate("user1", "password123")
    manager.authenticate("user3", "password123")
    
    auth_users = manager.select_authenticated()
    assert len(auth_users) == 2
    assert auth_users[0].login == "user1"
    assert auth_users[1].login == "user3"


def test_usermanager_select_by_prefix():
    """Тест выбора пользователей по префиксу"""
    manager = UserManager()
    manager.add("admin1")
    manager.add("admin2")
    manager.add("user1")
    
    admin_users = manager.select_by_prefix("admin")
    assert len(admin_users) == 2
    assert all(u.login.startswith("admin") for u in admin_users)


def test_usermanager_str_empty():
    """Тест строкового представления пустого менеджера"""
    manager = UserManager()
    result = str(manager)
    assert "Нет пользователей" in result


def test_usermanager_str_with_users():
    """Тест строкового представления с пользователями"""
    manager = UserManager()
    manager.add("user1")
    manager.add("user2")
    
    result = str(manager)
    assert "user1" in result
    assert "user2" in result
    assert "Логин" in result
    assert "Авторизован" in result


def test_userstorage_save_and_load():
    """Тест сохранения и загрузки пользователей"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        temp_filename = f.name
    
    try:
        # Создаем тестовых пользователей
        users = [
            User("user1", True),
            User("user2", False),
            User("admin", True)
        ]
        
        # Сохраняем
        UserStorage.save(users, temp_filename)
        
        # Загружаем
        loaded_users = UserStorage.load(temp_filename)
        
        # Проверяем
        assert len(loaded_users) == 3
        
        # Проверяем первого пользователя
        assert loaded_users[0].login == "user1"
        assert loaded_users[0].authenticated == True
        
        # Проверяем второго пользователя
        assert loaded_users[1].login == "user2"
        assert loaded_users[1].authenticated == False
        
        # Проверяем третьего пользователя
        assert loaded_users[2].login == "admin"
        assert loaded_users[2].authenticated == True
        
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def test_userstorage_load_invalid_xml():
    """Тест загрузки некорректного XML"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
        f.write("Это не XML файл")
        temp_filename = f.name
    
    try:
        with pytest.raises(DataFormatError) as exc_info:
            UserStorage.load(temp_filename)
        
        assert "некорректный формат данных" in str(exc_info.value)
        
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)


def test_userstorage_load_missing_file():
    """Тест загрузки отсутствующего файла"""
    with pytest.raises(DataFormatError) as exc_info:
        UserStorage.load("nonexistent_file.xml")
    
    assert "nonexistent_file.xml" in str(exc_info.value)


def test_exception_messages():
    """Тест сообщений исключений"""
    # UnauthorizedAccessError
    exc1 = UnauthorizedAccessError("guest")
    assert "'guest' -> доступ запрещён" in str(exc1)
    
    # InvalidLoginError
    exc2 = InvalidLoginError("user", "неверный пароль")
    assert "'user' -> неверный пароль" in str(exc2)
    
    # UnknownCommandError
    exc3 = UnknownCommandError("invalid_cmd")
    assert "'invalid_cmd' -> неизвестная команда" in str(exc3)
    
    # DataFormatError
    exc4 = DataFormatError("file.xml", "ошибка парсинга")
    assert "'file.xml' -> ошибка парсинга" in str(exc4)


def test_usermanager_sorting():
    """Тест сортировки пользователей по логину"""
    manager = UserManager()
    manager.add("zebra")
    manager.add("apple")
    manager.add("banana")
    
    assert manager.users[0].login == "apple"
    assert manager.users[1].login == "banana"
    assert manager.users[2].login == "zebra"
