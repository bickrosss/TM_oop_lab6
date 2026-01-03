#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def main() -> None:
    try:
        first: str = input("Первое значение: ")
        second: str = input("Второе значение: ")

        first_num: float = float(first)
        second_num: float = float(second)

        result: float = first_num + second_num
        print(f"Результат: {result}")
    except ValueError:
        result: str = first + second
        print(f"Результат: {result}")


if __name__ == "__main__":
    main()
