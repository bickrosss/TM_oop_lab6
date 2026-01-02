#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
from models import UserManager
from storage import UserStorage
from exceptions import *


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
        format='%(asctime)s - %(levelname)s - %(message)s'
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
                filename = command.split(maxsplit=1)[1]
                UserStorage.save(user_manager.users, filename)
                print(f"Данные сохранены в {filename}")
                logging.info(f"Сохранение в файл: {filename}")
            
            elif command.startswith('load '):
                filename = command.split(maxsplit=1)[1]
                users = UserStorage.load(filename)
                user_manager.users = users
                user_manager.users.sort(key=lambda u: u.login)
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
