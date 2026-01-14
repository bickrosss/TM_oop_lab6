import logging
import os
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import date


class IllegalYearError(Exception):

    def __init__(self, year: int, message: str = "Illegal year number") -> None:
        self.year = year
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.year} -> {self.message}"


class UnknownCommandError(Exception):

    def __init__(self, command: str, message: str = "Unknown command") -> None:
        self.command = command
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.command} -> {self.message}"


@dataclass(frozen=True)
class Worker:
    name: str
    post: str
    year: int


@dataclass
class Staff:
    workers: list[Worker] = field(default_factory=lambda: [])

    def add(self, name: str, post: str, year: int) -> None:
        today = date.today()

        if year < 0 or year > today.year:
            raise IllegalYearError(year)

        self.workers.append(Worker(name=name, post=post, year=year))

        self.workers.sort(key=lambda worker: worker.name)

    def __str__(self) -> str:
        if not self.workers:
            return "Нет данных о работниках"

        table = []
        line = f"+{'-' * 6}+{'-' * 34}+{'-' * 24}+{'-' * 12}+"
        table.append(line)

        table.append(f"| {'№':^4} | {'Ф.И.О':^32} | {'Должность':^22} | {'Год':^10} |")
        table.append(line)

        for idx, worker in enumerate(self.workers, 1):

            name = worker.name[:30] + ".." if len(worker.name) > 32 else worker.name
            post = worker.post[:20] + ".." if len(worker.post) > 22 else worker.post

            table.append(f"| {idx:>4} | {name:<32} | {post:<22} | {worker.year:>10} |")

        table.append(line)
        return "\n".join(table)

    def select(self, period: int) -> list[Worker]:
        today = date.today()

        results = []
        for worker in self.workers:
            if today.year - worker.year >= period:
                results.append(worker)
        return results

    def load(self, filename: str) -> None:
        with open(filename, "r", encoding="utf-8") as fin:
            xml = fin.read()
        parser = ET.XMLParser(encoding="utf-8")
        tree = ET.fromstring(xml, parser=parser)

        self.workers = []
        for worker_element in tree:
            name, post, year = None, None, None
            for element in worker_element:
                if element.tag == "name":
                    name = element.text
                elif element.tag == "post":
                    post = element.text
                elif element.tag == "year":
                    year = int(element.text or "0")

                if name is not None and post is not None and year is not None:
                    self.workers.append(Worker(name=name, post=post, year=year))

    def save(self, filename: str) -> None:
        folder = "xml_files"
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, filename)

        root = ET.Element("workers")
        for worker in self.workers:
            worker_element = ET.Element("worker")

            name_element = ET.SubElement(worker_element, "name")
            name_element.text = worker.name

            post_element = ET.SubElement(worker_element, "post")
            post_element.text = worker.post

            year_element = ET.SubElement(worker_element, "year")
            year_element.text = str(worker.year)

            root.append(worker_element)

        tree = ET.ElementTree(root)
        with open(path, "wb") as fout:
            tree.write(fout, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    logging.basicConfig(
        filename="worker.log",
        level=logging.INFO,
    )

    staff = Staff()

    while True:
        try:
            command = input(">>> ").lower()

            if command == "exit":
                break

            elif command == "add":
                name = input("Ф.И.О: ")
                post = input("Должность: ")
                year = int(input("Год приема на работу: "))
                staff.add(name, post, year)
                logging.info(f"Добавлен работник: {name}, {post}, {year}")
            elif command == "list":
                print(staff)

            elif command.startswith("select "):
                parts = command.split(maxsplit=1)
                selected = staff.select(int(parts[1]))
                if selected:
                    for idx, worker in enumerate(selected, 1):
                        print(
                            "{:>4}: {}".format(
                                idx,
                                worker.name,
                            )
                        )
                    logging.info(
                        f"Выборка работников со стажем работы более {parts[1]}"
                    )
            elif command.startswith("load "):
                parts = command.split(maxsplit=1)
                staff.load(parts[1])
                logging.info(f"Загружены данные из файла {parts[1]}")
                print(f"Данные из файла {parts[1]} успешно загружены:")
                print(staff)
            elif command.startswith("save "):
                parts = command.split(maxsplit=1)
                staff.save(parts[1])
                logging.info(f"Сохранены данные в файл {parts[1]}")
            elif command == "help":
                print("Список команд:\n")
                print("add - добавить работника;")
                print("list - вывести список работников;")
                print("select <стаж> - запросить работников со стажем;")
                print("load <имя файла> - загрузить данные из файла;")
                print("save <имя файла> - сохранить данные в файл;")
                print("help - отобразить справку;")
                print("exit - завершить работу с программой.")
            else:
                raise UnknownCommandError(command)
        except Exception as err:
            logging.error(err)
            print(err, file=sys.stderr)
