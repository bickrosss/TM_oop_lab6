#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List, Optional
import hashlib
import secrets
import string
from tasks.task1.exceptions import UnauthorizedAccessError, InvalidLoginError, InvalidPasswordError


def hash_password(password: str, salt: str) -> str:
    """Хэширование пароля с солью."""
    return hashlib.sha256((password + salt).encode()).hexdigest()


def generate_salt(length: int = 16) -> str:
    """Генерация случайной соли."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


@dataclass(frozen=True)
class User:
    """Класс пользователя."""
    login: str
    password_hash: str
    salt: str
    authenticated: bool = False
    
    def verify_password(self, password: str) -> bool:
        """Проверить пароль."""
        return hash_password(password, self.salt) == self.password_hash
    
    def access_resource(self) -> str:
        """Метод для доступа к ресурсу."""
        if not self.authenticated:
            raise UnauthorizedAccessError(self.login)
        return f"Пользователь '{self.login}': Доступ разрешён."
    
    def authenticate(self, password: str) -> None:
        """Метод для аутентификации пользователя."""
        if not self.verify_password(password):
            raise InvalidLoginError(self.login, "неверный пароль")
        self._set_authenticated(True)
    
    def logout(self) -> None:
        """Метод для выхода из системы."""
        self._set_authenticated(False)
    
    def _set_authenticated(self, value: bool) -> None:
        """Внутренний метод для изменения состояния аутентификации."""
        object.__setattr__(self, 'authenticated', value)
    
    def change_password(self, old_password: str, new_password: str) -> None:
        """Сменить пароль пользователя."""
        if not self.verify_password(old_password):
            raise InvalidLoginError(self.login, "старый пароль неверен")
        
        if len(new_password) < 6:
            raise InvalidPasswordError("пароль должен быть не менее 6 символов")
        
        # Генерируем новую соль для повышения безопасности
        new_salt = generate_salt()
        new_hash = hash_password(new_password, new_salt)
        
        object.__setattr__(self, 'password_hash', new_hash)
        object.__setattr__(self, 'salt', new_salt)


@dataclass
class UserManager:
    """Класс для управления коллекцией пользователей."""
    users: List[User] = field(default_factory=list)
    
    def add_user(self, login: str, password: str) -> User:
        """Добавить нового пользователя."""
        # Проверка логина
        if not login or len(login) < 3:
            raise InvalidLoginError(login, "логин должен быть не менее 3 символов")
        
        if not login.isalnum():
            raise InvalidLoginError(login, "логин должен содержать только буквы и цифры")
        
        # Проверка пароля
        if len(password) < 6:
            raise InvalidPasswordError("пароль должен быть не менее 6 символов")
        
        # Проверка уникальности логина
        for user in self.users:
            if user.login == login:
                raise InvalidLoginError(login, "логин уже существует")
        
        # Создание пользователя с хэшированным паролем
        salt = generate_salt()
        password_hash = hash_password(password, salt)
        
        user = User(
            login=login, 
            password_hash=password_hash,
            salt=salt,
            authenticated=False
        )
        self.users.append(user)
        return user
    
    def find_user(self, login: str) -> Optional[User]:
        """Найти пользователя по логину."""
        for user in self.users:
            if user.login == login:
                return user
        return None
    
    def get_user_or_raise(self, login: str) -> User:
        """Найти пользователя или вызвать исключение."""
        user = self.find_user(login)
        if user is None:
            raise InvalidLoginError(login, "пользователь не найден")
        return user
    
    def authenticate_user(self, login: str, password: str) -> User:
        """Аутентифицировать пользователя."""
        user = self.get_user_or_raise(login)
        user.authenticate(password)
        return user
    
    def logout_user(self, login: str) -> User:
        """Выйти из системы."""
        user = self.get_user_or_raise(login)
        user.logout()
        return user
    
    def change_user_password(self, login: str, old_password: str, new_password: str) -> User:
        """Сменить пароль пользователя."""
        user = self.get_user_or_raise(login)
        user.change_password(old_password, new_password)
        return user
    
    def get_authenticated_users(self) -> List[User]:
        """Получить список аутентифицированных пользователей."""
        return [user for user in self.users if user.authenticated]
    
    def get_all_users(self) -> List[User]:
        """Получить список всех пользователей."""
        return self.users
    
    def sort_users(self) -> None:
        """Отсортировать пользователей по логину."""
        self.users.sort(key=lambda user: user.login)
    
    def __str__(self) -> str:
        """Представление всех пользователей в виде таблицы."""
        if not self.users:
            return "Нет пользователей."
        
        # Заголовок таблицы
        table = []
        line = '+{}+{}+{}+'.format(
            '-' * 4,
            '-' * 30,
            '-' * 15
        )
        table.append(line)
        table.append(
            '| {:^4} | {:^30} | {:^15} |'.format(
                "№",
                "Логин",
                "Аутентифицирован"
            )
        )
        table.append(line)
        
        # Данные пользователей
        for idx, user in enumerate(self.users, 1):
            status = "Да" if user.authenticated else "Нет"
            table.append(
                '| {:^4} | {:^30} | {:^15} |'.format(
                    idx,
                    user.login,
                    status
                )
            )
        table.append(line)
        return '\n'.join(table)