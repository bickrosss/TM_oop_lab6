#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytest
from tasks.task1.models import UserManager, User
from tasks.task1.exceptions import UnauthorizedAccessError, InvalidLoginError
from tasks.task1.storage import UserStorage


def test_create_user():
    """Тест создания пользователя."""
    manager = UserManager()
    user = manager.add_user("testuser", "password123")
    assert user.login == "testuser"
    assert not user.authenticated


def test_authentication():
    """Тест аутентификации пользователя."""
    manager = UserManager()
    user = manager.add_user("testuser", "password123")
    
    # Правильный пароль
    user.authenticate("password123")
    assert user.authenticated
    
    # Неправильный пароль должен вызывать исключение
    user.logout()
    with pytest.raises(InvalidLoginError):
        user.authenticate("wrong_password")
    assert not user.authenticated


def test_unauthorized_access():
    """Тест доступа без аутентификации."""
    manager = UserManager()
    user = manager.add_user("testuser", "password123")
    
    # Доступ без аутентификации должен вызывать исключение
    with pytest.raises(UnauthorizedAccessError):
        user.access_resource()


def test_authorized_access():
    """Тест доступа после аутентификации."""
    manager = UserManager()
    user = manager.add_user("testuser", "password123")
    user.authenticate("password123")
    
    # Доступ после аутентификации должен работать
    result = user.access_resource()
    assert "Доступ разрешён" in result


def test_find_user():
    """Тест поиска пользователя."""
    manager = UserManager()
    manager.add_user("user1", "password123")
    manager.add_user("user2", "password456")
    
    # Поиск существующего пользователя
    user = manager.find_user("user1")
    assert user is not None
    assert user.login == "user1"
    
    # Поиск несуществующего пользователя
    user = manager.find_user("nonexistent")
    assert user is None


def test_xml_storage(tmp_path):
    """Тест сохранения и загрузки в XML."""
    import os
    
    manager = UserManager()
    manager.add_user("user1", "password123")
    manager.add_user("user2", "password456")
    
    # Аутентифицируем одного пользователя
    user1 = manager.find_user("user1")
    user1.authenticate("password123")
    
    # Сохраняем во временный файл
    filename = tmp_path / "test_users.xml"
    UserStorage.save(manager.get_all_users(), str(filename))
    assert os.path.exists(filename)
    
    # Загружаем
    loaded_users = UserStorage.load(str(filename))
    assert len(loaded_users) == 2
    
    # Проверяем состояние аутентификации
    auth_users = [u for u in loaded_users if u.authenticated]
    assert len(auth_users) == 1
    assert auth_users[0].login == "user1"


def test_user_manager_authenticate_user():
    """Тест аутентификации через менеджер."""
    manager = UserManager()
    manager.add_user("user1", "password123")
    
    # Правильная аутентификация
    user = manager.authenticate_user("user1", "password123")
    assert user.authenticated
    
    # Неправильная аутентификация должна вызывать исключение
    with pytest.raises(InvalidLoginError):
        manager.authenticate_user("user1", "wrong_password")


def test_change_password():
    """Тест смены пароля."""
    manager = UserManager()
    user = manager.add_user("testuser", "oldpassword")
    user.authenticate("oldpassword")
    
    # Смена пароля
    user.change_password("oldpassword", "newpassword123")
    
    # Проверяем, что старый пароль не работает
    user.logout()
    with pytest.raises(InvalidLoginError):
        user.authenticate("oldpassword")
    
    # Проверяем, что новый пароль работает
    user.authenticate("newpassword123")
    assert user.authenticated


def run_tests():
    """Запуск тестов системы (старая версия для совместимости)."""
    print("Тестирование системы авторизации")
    print("=" * 50)
    
    # Тест 1: Создание пользователя
    print("\n1. Создание пользователя:")
    try:
        manager = UserManager()
        user = manager.add_user("testuser", "password123")
        print(f"   Создан пользователь: {user.login}")
        print(f"   Аутентифицирован: {user.authenticated}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # Тест 2: Проверка доступа без аутентификации
    print("\n2. Проверка доступа без аутентификации:")
    try:
        manager = UserManager()
        user = manager.add_user("testuser", "password123")
        result = user.access_resource()
        print(f"   Результат: {result}")
    except UnauthorizedAccessError as e:
        print(f"   Исключение: {e}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # Тест 3: Аутентификация
    print("\n3. Аутентификация пользователя:")
    try:
        manager = UserManager()
        user = manager.add_user("testuser", "password123")
        user.authenticate("password123")
        print(f"   Пользователь аутентифицирован: {user.authenticated}")
    except InvalidLoginError as e:
        print(f"   Ошибка аутентификации: {e}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # Тест 4: Проверка доступа после аутентификации
    print("\n4. Проверка доступа после аутентификации:")
    try:
        manager = UserManager()
        user = manager.add_user("testuser", "password123")
        user.authenticate("password123")
        result = user.access_resource()
        print(f"   Результат: {result}")
    except UnauthorizedAccessError as e:
        print(f"   Исключение: {e}")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    # Тест 5: Сохранение в XML
    print("\n5. Сохранение в XML:")
    try:
        import os
        
        manager = UserManager()
        manager.add_user("admin", "password123")
        manager.add_user("guest", "password456")
        
        # Аутентифицируем одного пользователя
        admin_user = manager.find_user("admin")
        admin_user.authenticate("password123")
        
        filename = "test_users.xml"
        UserStorage.save(manager.get_all_users(), filename)
        print(f"   Данные сохранены в {filename}")
        
        if os.path.exists(filename):
            print(f"   Размер файла: {os.path.getsize(filename)} байт")
        
        # Тест 6: Загрузка из XML
        print("\n6. Загрузка из XML:")
        new_manager = UserManager()
        loaded_users = UserStorage.load(filename)
        new_manager.users = loaded_users
        
        print(f"   Загружено пользователей: {len(loaded_users)}")
        for user in loaded_users:
            print(f"   - {user.login}: authenticated={user.authenticated}")
        
        # Тест 7: Поиск несуществующего пользователя
        print("\n7. Поиск несуществующего пользователя:")
        try:
            manager.find_user("nonexistent")
        except InvalidLoginError as e:
            print(f"   Исключение: {e}")
        
        # Очистка
        if os.path.exists(filename):
            os.remove(filename)
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    print("\n" + "=" * 50)
    print("Все тесты завершены!")


if __name__ == '__main__':
    run_tests()