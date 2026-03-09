"""
Парсер для поиска и анализа карт, появляющихся в таверне.
Ищет связку: FULL_ENTITY - Creating ID=... (с CardID) + следующая строка с tag=CONTROLLER value=13
"""

import re
from typing import Set, List, Tuple, Dict, Optional
from collections import Counter

class TavernCardsParser:
    """
    Парсер для поиска карт, которые появляются в таверне.
    Анализирует связку:
    - Строка 1: FULL_ENTITY - Creating ID=XXXX CardID=YYYY
    - Строка 2: ... tag=CONTROLLER value=13 ...
    Сохраняет пары (ID, CardID) для каждой карты, появившейся у игрока.
    """

    def __init__(self, file_path: str, encoding: str = 'utf-8'):
        """
        Инициализация парсера карт таверны.

        Args:
            file_path: Путь к лог-файлу
            encoding: Кодировка файла
        """
        self.file_path = file_path
        self.encoding = encoding

        # Основные данные
        self.cards_found = []  # Список всех найденных карт (ID, CardID)
        self.unique_ids = set()  # Уникальные ID сущностей
        self.unique_card_ids = set()  # Уникальные CardID

        # Статистика
        self.id_counter = Counter()  # Сколько раз встречался каждый ID
        self.card_id_counter = Counter()  # Сколько раз встречался каждый CardID

        self._parse_file()

    def _parse_file(self) -> None:
        """
        Парсит файл построчно, ища связки:
        Строка N: FULL_ENTITY - Creating ID=XXXX CardID=YYYY
        Строка N+1: ... tag=CONTROLLER value=13 ...
        """
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as file:
                lines = file.readlines()

            i = 0
            while i < len(lines) - 1:  # -1 чтобы была следующая строка
                current_line = lines[i].rstrip('\n')
                next_line = lines[i + 1].rstrip('\n')

                # Проверяем текущую строку на создание сущности
                entity_info = self._extract_entity_info(current_line)

                if entity_info:
                    entity_id, card_id = entity_info

                    # Проверяем следующую строку на CONTROLLER=13
                    if self._has_controller_13(next_line):
                        # Сохраняем карту
                        self.cards_found.append((entity_id, card_id))
                        self.unique_ids.add(entity_id)
                        self.unique_card_ids.add(card_id)
                        self.id_counter[entity_id] += 1
                        self.card_id_counter[card_id] += 1

                i += 1

        except FileNotFoundError:
            raise FileNotFoundError(f"Файл '{self.file_path}' не найден.")
        except UnicodeDecodeError:
            raise UnicodeDecodeError(f"Ошибка кодировки. Попробуйте другую кодировку.")

    def _extract_entity_info(self, line: str) -> Optional[Tuple[str, str]]:
        """
        Извлекает ID и CardID из строки создания сущности.

        Args:
            line: Строка вида: FULL_ENTITY - Creating ID=329 CardID=BGS_119

        Returns:
            Кортеж (entity_id, card_id) или None
        """
        # Паттерн для поиска: FULL_ENTITY - Creating ID=329 CardID=BGS_119
        pattern = r'FULL_ENTITY - Creating ID=(\d+).*?CardID=([A-Za-z0-9_]+)'

        match = re.search(pattern, line)
        if match:
            entity_id = match.group(1)
            card_id = match.group(2)
            return (entity_id, card_id)

        return None

    def _has_controller_13(self, line: str) -> bool:
        """
        Проверяет, содержит ли строка tag=CONTROLLER value=13.

        Args:
            line: Строка для проверки

        Returns:
            True если найден CONTROLLER=13
        """
        # Точный паттерн для tag=CONTROLLER value=13
        pattern = r'tag=CONTROLLER value=13\b'
        return bool(re.search(pattern, line))

    # ========== Методы для получения данных ==========

    def get_all_cards(self) -> List[Tuple[str, str]]:
        """
        Возвращает список всех найденных карт в порядке обнаружения.

        Returns:
            List[Tuple[entity_id, card_id]]
        """
        return self.cards_found.copy()

    def get_unique_ids(self) -> Set[str]:
        """Возвращает множество уникальных ID сущностей."""
        return self.unique_ids.copy()

    def get_unique_card_ids(self) -> Set[str]:
        """Возвращает множество уникальных CardID."""
        return self.unique_card_ids.copy()

    def get_cards_by_entity_id(self, entity_id: str) -> List[str]:
        """
        Возвращает все CardID для конкретного ID сущности.

        Args:
            entity_id: ID сущности

        Returns:
            Список CardID
        """
        return [card_id for e_id, card_id in self.cards_found if e_id == entity_id]

    def get_entities_by_card_id(self, card_id: str) -> List[str]:
        """
        Возвращает все ID сущностей для конкретной карты.

        Args:
            card_id: ID карты

        Returns:
            Список ID сущностей
        """
        return [e_id for e_id, c_id in self.cards_found if c_id == card_id]

    def get_statistics(self) -> dict:
        """
        Возвращает подробную статистику по найденным картам.
        """
        return {
            'total_cards_found': len(self.cards_found),
            'unique_entities': len(self.unique_ids),
            'unique_cards': len(self.unique_card_ids),
            'entity_frequency': dict(self.id_counter),
            'card_frequency': dict(self.card_id_counter),
            'most_common_entities': self.id_counter.most_common(10),
            'most_common_cards': self.card_id_counter.most_common(10),
        }

    def get_cards_summary(self) -> List[Tuple[str, int, List[str]]]:
        """
        Возвращает сводку по картам: (CardID, количество, список ID сущностей)
        """
        summary = []
        for card_id in sorted(self.unique_card_ids):
            count = self.card_id_counter[card_id]
            entities = self.get_entities_by_card_id(card_id)
            summary.append((card_id, count, entities))
        return summary

    def search_by_card_pattern(self, pattern: str) -> List[Tuple[str, str]]:
        """
        Поиск карт по паттерну в CardID.

        Args:
            pattern: Regex паттерн для поиска в CardID

        Returns:
            Список найденных пар (entity_id, card_id)
        """
        regex = re.compile(pattern)
        return [(e_id, c_id) for e_id, c_id in self.cards_found if regex.search(c_id)]

    def export_to_dict(self) -> dict:
        """
        Экспортирует данные в словарь для удобного сохранения.
        """
        return {
            'cards': [
                {'entity_id': e_id, 'card_id': c_id}
                for e_id, c_id in self.cards_found
            ],
            'statistics': self.get_statistics(),
            'unique_entities': list(self.unique_ids),
            'unique_cards': list(self.unique_card_ids)
        }