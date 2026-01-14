#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import getpass
from models import UserManager
from storage import UserStorage
from exceptions import (
    UnauthorizedAccessError, 
    InvalidLoginError, 
    UnknownCommandError, 
    DataFormatError,
    InvalidPasswordError
)


def setup_logging() -> None:
    """Настройка системы логирования."""
    logging.basicConfig(
        filename='auth_system.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        encoding='utf-8'
    )


def print_help() -> None:
    """Вывод справки по командам."""
    help_text = """
Доступные команды:
  add <логин>             - Добавить нового пользователя (запросит пароль)
  auth <логин>            - Аутентифицировать пользователя (запросит пароль)
  logout <логин>          - Выйти из системы
  access <логин>          - Проверить доступ к ресурсу
  changepass <логин>      - Сменить пароль (запросит старый и новый пароли)
  list                    - Показать всех пользователей
  list_auth               - Показать аутентифицированных пользователей
  save <файл.xml>         - Сохранить пользователей в XML
  load <файл.xml>         - Загрузить пользователей из XML
  help                    - Показать эту справку
  exit                    - Выйти из программы
  
Требования к паролю:
  - Не менее 6 символов
  - Рекомендуется использовать буквы, цифры и специальные символы
"""
    print(help_text)


def get_password(prompt: str = "Пароль: ") -> str:
    """Безопасный ввод пароля."""
    return getpass.getpass(prompt)


def main() -> None:
    """Основная функция программы."""
    setup_logging()
    user_manager = UserManager()
    
    print("Система управления пользователями с безопасной аутентификацией")
    print("=" * 60)
    print_help()
    
    while True:
        try:
            # Ввод команды
            command_input = input("\n>>> ").strip()
            if not command_input:
                continue
            
            parts = command_input.split()
            command = parts[0].lower()
            
            # Обработка команд
            if command == 'exit':
                logging.info("Завершение работы программы.")
                print("До свидания!")
                break
            
            elif command == 'help':
                print_help()
                logging.info("Вывод справки.")
            
            elif command == 'add' and len(parts) >= 2:
                login = parts[1]
                print(f"Добавление пользователя: {login}")
                password = get_password("Введите пароль (мин. 6 символов): ")
                confirm = get_password("Повторите пароль: ")
                
                if password != confirm:
                    print("Ошибка: пароли не совпадают!", file=sys.stderr)
                    continue
                
                user = user_manager.add_user(login, password)
                print(f"✓ Пользователь '{login}' успешно добавлен.")
                logging.info(f"Добавлен пользователь: {login}")
            
            elif command == 'auth' and len(parts) >= 2:
                login = parts[1]
                password = get_password(f"Пароль для {login}: ")
                user = user_manager.authenticate_user(login, password)
                print(f"✓ Пользователь '{login}' успешно аутентифицирован.")
                logging.info(f"Аутентифицирован пользователь: {login}")
            
            elif command == 'logout' and len(parts) >= 2:
                login = parts[1]
                user = user_manager.logout_user(login)
                print(f"✓ Пользователь '{login}' вышел из системы.")
                logging.info(f"Выход пользователя: {login}")
            
            elif command == 'access' and len(parts) >= 2:
                login = parts[1]
                user = user_manager.get_user_or_raise(login)
                result = user.access_resource()
                print(f"✓ {result}")
                logging.info(f"Проверка доступа для пользователя: {login}")
            
            elif command == 'changepass' and len(parts) >= 2:
                login = parts[1]
                print(f"Смена пароля для пользователя: {login}")
                old_password = get_password("Старый пароль: ")
                new_password = get_password("Новый пароль (мин. 6 символов): ")
                confirm = get_password("Повторите новый пароль: ")
                
                if new_password != confirm:
                    print("Ошибка: новые пароли не совпадают!", file=sys.stderr)
                    continue
                
                user = user_manager.change_user_password(login, old_password, new_password)
                print(f"✓ Пароль для пользователя '{login}' успешно изменен.")
                logging.info(f"Смена пароля для пользователя: {login}")
            
            elif command == 'list':
                user_manager.sort_users()
                print("\n" + str(user_manager))
                logging.info("Вывод списка всех пользователей.")
            
            elif command == 'list_auth':
                auth_users = user_manager.get_authenticated_users()
                if auth_users:
                    print("\nАутентифицированные пользователи:")
                    for idx, user in enumerate(auth_users, 1):
                        print(f"{idx:>4}: {user.login}")
                    logging.info(f"Вывод {len(auth_users)} аутентифицированных пользователей.")
                else:
                    print("\nНет аутентифицированных пользователей.")
                    logging.info("Нет аутентифицированных пользователей.")
            
            elif command == 'save' and len(parts) >= 2:
                filename = parts[1]
                UserStorage.save(user_manager.get_all_users(), filename)
                print(f"✓ Данные сохранены в файл: {filename}")
                logging.info(f"Сохранение данных в файл: {filename}")
            
            elif command == 'load' and len(parts) >= 2:
                filename = parts[1]
                users = UserStorage.load(filename)
                user_manager.users = users
                user_manager.sort_users()
                print(f"✓ Данные загружены из файла: {filename}")
                print(f"  Загружено пользователей: {len(users)}")
                logging.info(f"Загрузка данных из файла: {filename}")
            
            else:
                raise UnknownCommandError(command_input)
        
        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем.")
            logging.warning("Программа прервана пользователем (Ctrl+C).")
            break
        
        except UnknownCommandError as e:
            print(f"\n✗ Ошибка: {e}", file=sys.stderr)
            logging.error(f"Неизвестная команда: {e}")
        
        except InvalidLoginError as e:
            print(f"\n✗ Ошибка авторизации: {e}", file=sys.stderr)
            logging.error(f"Ошибка авторизации: {e}")
        
        except UnauthorizedAccessError as e:
            print(f"\n✗ Ошибка доступа: {e}", file=sys.stderr)
            logging.error(f"Ошибка доступа: {e}")
        
        except InvalidPasswordError as e:
            print(f"\n✗ Ошибка пароля: {e}", file=sys.stderr)
            logging.error(f"Ошибка пароля: {e}")
        
        except DataFormatError as e:
            print(f"\n✗ Ошибка данных: {e}", file=sys.stderr)
            logging.error(f"Ошибка данных: {e}")
        
        except Exception as e:
            print(f"\n✗ Непредвиденная ошибка: {e}", file=sys.stderr)
            logging.error(f"Непредвиденная ошибка: {e}", exc_info=True)


if __name__ == '__main__':
    main()