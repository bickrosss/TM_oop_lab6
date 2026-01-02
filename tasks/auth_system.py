#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
import logging
import sys
import xml.etree.ElementTree as ET


# ========== КЛАССЫ ИСКЛЮЧЕНИЙ ==========
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


# ========== КЛАССЫ ДАННЫХ ==========
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
    users: list[User] = field(default_factory=list)
    
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
    
    def select_authenticated(self) -> list[User]:
        """Выбрать аутентифицированных пользователей."""
        return [user for user in self.users if user.authenticated]
    
    def select_by_prefix(self, prefix: str) -> list[User]:
        """Выбрать пользователей по префиксу логина."""
        return [user for user in self.users if user.login.startswith(prefix)]
    
    def __str__(self) -> str:
        """Представление всех пользователей в виде таблицы."""
        if not self.users:
            return "Нет пользователей."
        
        # Заголовок таблицы
        table = []
        line = '+{}+{}+{}+'.format(
            '-' * 4,
            '-' * 25,
            '-' * 15
        )
        table.append(line)
        table.append(
            '| {:^4} | {:^25} | {:^15} |'.format(
                "№",
                "Логин",
                "Авторизован"
            )
        )
        table.append(line)
        
        # Данные пользователей
        for idx, user in enumerate(self.users, 1):
            status = "Да" if user.authenticated else "Нет"
            table.append(
                '| {:^4} | {:^25} | {:^15} |'.format(
                    idx,
                    user.login,
                    status
                )
            )
        table.append(line)
        return '\n'.join(table)
    
    def save(self, filename: str) -> None:
        """Сохранить пользователей в XML файл."""
        root = ET.Element('users')
        
        for user in self.users:
            user_element = ET.Element('user')
            
            login_element = ET.SubElement(user_element, 'login')
            login_element.text = user.login
            
            auth_element = ET.SubElement(user_element, 'authenticated')
            auth_element.text = str(user.authenticated).lower()
            
            root.append(user_element)
        
        tree = ET.ElementTree(root)
        with open(filename, 'wb') as fout:
            # Добавляем декларацию XML
            fout.write(b'<?xml version="1.0" encoding="utf-8"?>\n')
            tree.write(fout, encoding='utf-8')
    
    def load(self, filename: str) -> None:
        """Загрузить пользователей из XML файла."""
        try:
            tree = ET.parse(filename)
            root = tree.getroot()
        except (ET.ParseError, FileNotFoundError) as e:
            raise DataFormatError(filename, f"ошибка чтения файла: {e}")
        
        loaded_users = []
        
        for user_element in root:
            login = None
            authenticated = False
            
            for element in user_element:
                if element.tag == 'login':
                    login = element.text
                elif element.tag == 'authenticated':
                    try:
                        authenticated = element.text.lower() == 'true'
                    except (AttributeError, ValueError):
                        authenticated = False
            
            if login is not None:
                user = User(login=login, authenticated=authenticated)
                loaded_users.append(user)
        
        self.users = loaded_users
        self.users.sort(key=lambda u: u.login)


# ========== ОСНОВНАЯ ПРОГРАММА ==========
def print_help() -> None:
    """Вывод справки по командам."""
    help_text = """
Доступные команды:
  add <логин>           - Добавить нового пользователя
  auth <логин> <пароль> - Авторизовать пользователя (пароль: password123)
  logout <логин>        - Выйти из системы
  access <логин>        - Проверить доступ к ресурсу
  list                  - Показать всех пользователей
  select_auth           - Показать авторизованных пользователей
  select <префикс>      - Показать пользователей с логином на <префикс>
  save <файл.xml>       - Сохранить в XML
  load <файл.xml>       - Загрузить из XML
  help                  - Показать справку
  exit                  - Выйти
"""
    print(help_text)


def main() -> None:
    """Главная функция программы."""
    # Настройка логирования
    logging.basicConfig(
        filename='auth.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8'
    )
    
    user_manager = UserManager()
    
    print("Система управления пользователями")
    print("Пароль по умолчанию: password123")
    print_help()
    
    while True:
        try:
            # Ввод команды
            command = input(">>> ").strip().lower()
            
            if command == 'exit':
                logging.info("Завершение работы программы.")
                print("До свидания!")
                break
            
            elif command == 'help':
                print_help()
                logging.info("Вывод справки.")
            
            elif command == 'list':
                print(user_manager)
                logging.info("Вывод списка пользователей.")
            
            elif command.startswith('add '):
                parts = command.split(maxsplit=1)
                if len(parts) < 2:
                    print("Ошибка: укажите логин", file=sys.stderr)
                    continue
                
                login = parts[1]
                user_manager.add(login)
                print(f"Пользователь '{login}' добавлен.")
                logging.info(f"Добавлен пользователь: {login}")
            
            elif command.startswith('auth '):
                parts = command.split(maxsplit=2)
                if len(parts) < 3:
                    print("Ошибка: укажите логин и пароль", file=sys.stderr)
                    continue
                
                login, password = parts[1], parts[2]
                user_manager.authenticate(login, password)
                print(f"Пользователь '{login}' авторизован.")
                logging.info(f"Авторизован пользователь: {login}")
            
            elif command.startswith('logout '):
                parts = command.split(maxsplit=1)
                if len(parts) < 2:
                    print("Ошибка: укажите логин", file=sys.stderr)
                    continue
                
                login = parts[1]
                user_manager.logout(login)
                print(f"Пользователь '{login}' вышел из системы.")
                logging.info(f"Выход пользователя: {login}")
            
            elif command.startswith('access '):
                parts = command.split(maxsplit=1)
                if len(parts) < 2:
                    print("Ошибка: укажите логин", file=sys.stderr)
                    continue
                
                login = parts[1]
                user = user_manager.find(login)
                result = user.access_resource()
                print(result)
                logging.info(f"Проверка доступа: {login}")
            
            elif command == 'select_auth':
                auth_users = user_manager.select_authenticated()
                if auth_users:
                    print("Авторизованные пользователи:")
                    for idx, user in enumerate(auth_users, 1):
                        print(f"  {idx}. {user.login}")
                    logging.info(f"Найдено {len(auth_users)} авторизованных пользователей.")
                else:
                    print("Нет авторизованных пользователей.")
                    logging.info("Нет авторизованных пользователей.")
            
            elif command.startswith('select '):
                parts = command.split(maxsplit=1)
                if len(parts) < 2:
                    print("Ошибка: укажите префикс", file=sys.stderr)
                    continue
                
                prefix = parts[1]
                selected = user_manager.select_by_prefix(prefix)
                if selected:
                    print(f"Пользователи с логином на '{prefix}':")
                    for idx, user in enumerate(selected, 1):
                        print(f"  {idx}. {user.login}")
                    logging.info(f"Найдено {len(selected)} пользователей с префиксом '{prefix}'.")
                else:
                    print(f"Пользователи с логином на '{prefix}' не найдены.")
                    logging.info(f"Пользователи с префиксом '{prefix}' не найдены.")
            
            elif command.startswith('save '):
                parts = command.split(maxsplit=1)
                if len(parts) < 2:
                    print("Ошибка: укажите имя файла", file=sys.stderr)
                    continue
                
                filename = parts[1]
                user_manager.save(filename)
                print(f"Данные сохранены в {filename}")
                logging.info(f"Сохранение в файл: {filename}")
            
            elif command.startswith('load '):
                parts = command.split(maxsplit=1)
                if len(parts) < 2:
                    print("Ошибка: укажите имя файла", file=sys.stderr)
                    continue
                
                filename = parts[1]
                user_manager.load(filename)
                print(f"Данные загружены из {filename}")
                logging.info(f"Загрузка из файла: {filename}")
            
            else:
                raise UnknownCommandError(command)
        
        except KeyboardInterrupt:
            print("\nПрограмма прервана.")
            break
        
        except UnknownCommandError as e:
            print(f"Ошибка: {e}", file=sys.stderr)
            logging.error(f"Неизвестная команда: {e}")
        
        except UnauthorizedAccessError as e:
            print(f"Ошибка доступа: {e}", file=sys.stderr)
            logging.error(f"Ошибка доступа: {e}")
        
        except (InvalidLoginError, DataFormatError) as e:
            print(f"Ошибка: {e}", file=sys.stderr)
            logging.error(f"Ошибка: {e}")
        
        except Exception as e:
            print(f"Непредвиденная ошибка: {e}", file=sys.stderr)
            logging.error(f"Непредвиденная ошибка: {e}", exc_info=True)


if __name__ == '__main__':
    main()
