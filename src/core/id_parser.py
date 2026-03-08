"""
Парсер для сбора всех уникальных ID из лог-файла.
"""

import re
from typing import Set, List, Tuple, Optional
from collections import Counter


class IDParser:
    """Класс для сбора всех уникальных ID из лог-файла."""

    def __init__(self, file_path: str, encoding: str = 'utf-8'):
        """
        Инициализация парсера.

        Args:
            file_path: Путь к файлу
            encoding: Кодировка файла
        """
        self.file_path = file_path
        self.encoding = encoding
        self.ids_found = set()  # Множество для хранения уникальных ID
        self.id_counter = Counter()  # Счетчик вхождений каждого ID
        self.lines_with_ids = []  # Список кортежей (номер_строки, ID, строка)
        self._parse_file()

    def _parse_file(self) -> None:
        """
        Парсит файл и собирает все найденные ID.
        """
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as file:
                for line_num, line in enumerate(file, 1):
                    ids_in_line = self._extract_ids_from_line(line)

                    for found_id in ids_in_line:
                        self.ids_found.add(found_id)
                        self.id_counter[found_id] += 1
                        self.lines_with_ids.append((line_num, found_id, line.rstrip('\n')))

        except FileNotFoundError:
            raise FileNotFoundError(f"Файл '{self.file_path}' не найден.")
        except UnicodeDecodeError:
            raise UnicodeDecodeError(f"Ошибка кодировки. Попробуйте другую кодировку.")

    def _extract_ids_from_line(self, line: str) -> Set[str]:
        """
        Извлекает все ID из строки.

        Args:
            line: Строка для парсинга

        Returns:
            Множество найденных ID в строке
        """
        found_ids = set()

        # Паттерны для поиска ID в разных форматах
        patterns = [
            # id=12345, id:12345
            r'[Ii][Dd][=:](\d+)',
            # "id":12345
            r'"[Ii][Dd]"[=:](\d+)',
            # id = 12345
            r'[Ii][Dd]\s*[=:]\s*(\d+)',
            # id = "12345"
            r'[Ii][Dd]\s*[=:]\s*"(\d+)"',
            # EntityID=12345
            r'[Ee]ntity[_-]?[Ii][Dd][=:](\d+)',
            # userId:12345
            r'[Uu]ser[_-]?[Ii][Dd][=:](\d+)',
            # ID в JSON: {"id": 12345}
            r'"id"\s*:\s*(\d+)',
            # ID в XML: <id>12345</id>
            r'<[Ii][Dd][^>]*>(\d+)</[Ii][Dd]>',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, line)
            for match in matches:
                # Очищаем найденный ID от кавычек и пробелов
                clean_id = match.strip().strip('"\'')
                if clean_id.isdigit():  # Проверяем, что это число
                    found_ids.add(clean_id)

        return found_ids

    def get_all_ids(self) -> Set[str]:
        """
        Возвращает множество всех найденных уникальных ID.

        Returns:
            Set[str]: Уникальные ID
        """
        return self.ids_found

    def get_ids_sorted(self) -> List[str]:
        """
        Возвращает отсортированный список всех ID.

        Returns:
            List[str]: Отсортированные ID
        """
        return sorted(self.ids_found, key=int)

    def get_id_statistics(self) -> dict:
        """
        Возвращает статистику по найденным ID.

        Returns:
            dict: Статистика
        """
        return {
            'total_unique_ids': len(self.ids_found),
            'total_occurrences': sum(self.id_counter.values()),
            'most_common': self.id_counter.most_common(10),
            'id_frequency': dict(self.id_counter)
        }

    def get_lines_for_id(self, target_id: str) -> List[Tuple[int, str]]:
        """
        Возвращает все строки, содержащие конкретный ID.

        Args:
            target_id: ID для поиска

        Returns:
            List[Tuple[int, str]]: Список (номер_строки, строка)
        """
        return [(num, line) for num, id_found, line in self.lines_with_ids
                if id_found == target_id]

    def find_ids_by_pattern(self, pattern: str) -> Set[str]:
        """
        Находит ID, соответствующие регулярному выражению.

        Args:
            pattern: Regex паттерн

        Returns:
            Set[str]: ID, соответствующие паттерну
        """
        regex = re.compile(pattern)
        return {id_val for id_val in self.ids_found if regex.search(id_val)}