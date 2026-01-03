#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import List
from exceptions import UnauthorizedAccessError, InvalidLoginError


@dataclass(frozen=True)
class User:
    """Класс пользователя."""
    login: str
    authenticated: bool = False
    
    def access_resource(self) -> str:
        """Метод для доступа к ресурсу."""
        if not self.authenticated:
            raise UnauthorizedAccessError(self.login)
        return f"Пользователь '{self.login}': Доступ разрешён."
    
    def authenticate(self, password: str) -> None:
        """Метод для аутентификации пользователя."""
        # Простая проверка пароля (для демонстрации)
        if password == "password123":
            self._set_authenticated(True)
        else:
            raise InvalidLoginError(self.login, "неверный пароль")
    
    def logout(self) -> None:
        """Метод для выхода из системы."""
        self._set_authenticated(False)
    
    def _set_authenticated(self, value: bool) -> None:
        """Внутренний метод для изменения состояния аутентификации."""
        # Используем object.__setattr__ для изменения frozen dataclass
        object.__setattr__(self, 'authenticated', value)


@dataclass
class UserManager:
    """Класс для управления пользователями."""
    users: List[User] = field(default_factory=list)
    
    def add(self, login: str) -> User:
        """Добавить нового пользователя."""
        # Проверка логина
        if not login or len(login) < 3:
            raise InvalidLoginError(login, "логин должен быть не менее 3 символов")
        
        # Проверка уникальности логина
        for user in self.users:
            if user.login == login:
                raise InvalidLoginError(login, "логин уже существует")
        
        user = User(login=login, authenticated=False)
        self.users.append(user)
        self.users.sort(key=lambda u: u.login)  # Сортировка по логину
        return user
    
    def find(self, login: str) -> User:
        """Найти пользователя по логину."""
        for user in self.users:
            if user.login == login:
                return user
        raise InvalidLoginError(login, "пользователь не найден")
    
    def authenticate(self, login: str, password: str) -> User:
        """Аутентифицировать пользователя."""
        user = self.find(login)
        user.authenticate(password)
        return user
    
    def logout(self, login: str) -> User:
        """Выйти из системы."""
        user = self.find(login)
        user.logout()
        return user
    
    def select_authenticated(self) -> List[User]:
        """Выбрать аутентифицированных пользователей."""
        return [user for user in self.users if user.authenticated]
    
    def select_by_prefix(self, prefix: str) -> List[User]:
        """Выбрать пользователей по префиксу логина."""
        return [user for user in self.users if user.login.startswith(prefix)]
    
    def __str__(self) -> str:
        """Представление всех пользователей в виде таблицы."""
        if not self.users:
            return "Нет пользователей."
        
        # Заголовок таблицы
        table = []
        line = '+{}+{}+{}+'.format('-' * 4, '-' * 25, '-' * 15)
        table.append(line)
        table.append('| {:^4} | {:^25} | {:^15} |'.format(
            "№", "Логин", "Авторизован"))
        table.append(line)
        
        # Данные пользователей
        for idx, user in enumerate(self.users, 1):
            status = "Да" if user.authenticated else "Нет"
            table.append('| {:^4} | {:^25} | {:^15} |'.format(
                idx, user.login, status))
        
        table.append(line)
        return '\n'.join(table)
