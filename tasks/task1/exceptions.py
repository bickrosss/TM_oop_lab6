#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class UnauthorizedAccessError(Exception):
    """Исключение при попытке доступа без авторизации."""
    def __init__(self, username, message="доступ запрещён"):
        self.username = username
        self.message = message
        super().__init__(f"'{username}' -> {message}")


class InvalidLoginError(Exception):
    """Исключение при некорректном логине."""
    def __init__(self, login, message="некорректный логин"):
        self.login = login
        self.message = message
        super().__init__(f"'{login}' -> {message}")


class UnknownCommandError(Exception):
    """Исключение при вводе неизвестной команды."""
    def __init__(self, command, message="неизвестная команда"):
        self.command = command
        self.message = message
        super().__init__(f"'{command}' -> {message}")


class DataFormatError(Exception):
    """Исключение при некорректном формате данных."""
    def __init__(self, filename, message="некорректный формат данных"):
        self.filename = filename
        self.message = message
        super().__init__(f"'{filename}' -> {message}")


class InvalidPasswordError(Exception):
    """Исключение при некорректном пароле."""
    def __init__(self, message="некорректный пароль"):
        self.message = message
        super().__init__(message)