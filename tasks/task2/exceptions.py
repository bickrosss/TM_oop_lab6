#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class InvalidPriceError(Exception):
    """Исключение при некорректной цене."""
    def __init__(self, price, message="некорректная цена"):
        self.price = price
        self.message = message
        super().__init__(f"'{price}' -> {message}")


class StoreNotFoundError(Exception):
    """Исключение при поиске несуществующего магазина."""
    def __init__(self, store, message="магазин не найден"):
        self.store = store
        self.message = message
        super().__init__(f"'{store}' -> {message}")


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
