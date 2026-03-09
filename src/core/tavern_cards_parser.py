"""
Парсер для поиска и анализа карт, появляющихся в таверне.
Ищет связку: FULL_ENTITY - Creating ID=... (с CardID) + следующая строка с tag=CONTROLLER value=X
где X - любое числовое значение, обозначающее владельца карты.
"""

import re
from typing import Set, List, Tuple, Dict, Optional, Any
from collections import Counter

class TavernCardsParser:
    """
    Парсер для поиска карт, которые появляются в таверне.
    Анализирует связку:
    - Строка 1: FULL_ENTITY - Creating ID=XXXX CardID=YYYY
    - Строка 2: ... tag=CONTROLLER value=X ... (где X - любое число)

    По умолчанию ищет value=13 (игрок), но можно настроить на любое значение.
    """

    def __init__(self, file_path: str, encoding: str = 'utf-8', target_controller_value: Optional[int] = 13):
        """
        Инициализация парсера карт таверны.

        Args:
            file_path: Путь к лог-файлу
            encoding: Кодировка файла
            target_controller_value: Значение CONTROLLER для фильтрации (None - не фильтровать)
        """
        self.file_path = file_path
        self.encoding = encoding
        self.target_controller_value = target_controller_value

        # Основные данные
        self.cards_found = []  # Список всех найденных карт (ID, CardID)
        self.unique_ids = set()  # Уникальные ID сущностей
        self.unique_card_ids = set()  # Уникальные CardID

        # Статистика
        self.id_counter = Counter()  # Сколько раз встречался каждый ID
        self.card_id_counter = Counter()  # Сколько раз встречался каждый CardID

        # Для отслеживания всех значений CONTROLLER
        self.controller_values_found = set()
        self.cards_by_controller = {}  # Словарь {controller_value: список карт}

        self._parse_file()

    def _parse_file(self) -> None:
        """
        Парсит файл построчно, ища связки:
        Строка N: FULL_ENTITY - Creating ID=XXXX CardID=YYYY
        Строка N+1: ... tag=CONTROLLER value=X ...
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

                    # Проверяем следующую строку на CONTROLLER и извлекаем его значение
                    controller_value = self._extract_controller_value(next_line)

                    if controller_value is not None:
                        # Сохраняем информацию о значении CONTROLLER
                        self.controller_values_found.add(controller_value)

                        # Сохраняем карту в общий словарь по значениям контроллера
                        if controller_value not in self.cards_by_controller:
                            self.cards_by_controller[controller_value] = []
                        self.cards_by_controller[controller_value].append((entity_id, card_id))

                        # Если указан конкретный target_controller_value, фильтруем по нему
                        if (self.target_controller_value is None or
                            controller_value == self.target_controller_value):
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
        except Exception as e:
            raise Exception(f"Ошибка при парсинге файла: {e}")

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

    def _extract_controller_value(self, line: str) -> Optional[int]:
        """
        Извлекает значение CONTROLLER из строки.

        Args:
            line: Строка для проверки

        Returns:
            Значение CONTROLLER или None, если не найдено
        """
        # Новый паттерн для поиска tag=CONTROLLER value=X, где X - любое число
        pattern = r'tag=CONTROLLER value=(\d+)\b'

        match = re.search(pattern, line)
        if match:
            return int(match.group(1))

        return None

    def _has_controller_13(self, line: str) -> bool:
        """
        Устаревший метод. Оставлен для обратной совместимости.
        Проверяет, содержит ли строка tag=CONTROLLER value=13.
        """
        return self._extract_controller_value(line) == 13

    # ========== Новые методы для работы с разными значениями CONTROLLER ==========

    def get_controller_values(self) -> Set[int]:
        """
        Возвращает все найденные значения CONTROLLER.
        """
        return self.controller_values_found.copy()

    def get_cards_by_controller_value(self, controller_value: int) -> List[Tuple[str, str]]:
        """
        Возвращает карты для конкретного значения CONTROLLER.

        Args:
            controller_value: Значение CONTROLLER для фильтрации

        Returns:
            Список пар (entity_id, card_id)
        """
        return self.cards_by_controller.get(controller_value, []).copy()

    def get_controller_statistics(self) -> Dict[int, int]:
        """
        Возвращает статистику по значениям CONTROLLER.

        Returns:
            Словарь {controller_value: количество карт}
        """
        return {
            value: len(cards)
            for value, cards in self.cards_by_controller.items()
        }

    def set_target_controller(self, value: Optional[int]) -> None:
        """
        Изменяет целевое значение CONTROLLER для основного списка cards_found.

        Args:
            value: Новое значение CONTROLLER (None - не фильтровать)
        """
        self.target_controller_value = value

        # Обновляем основной список карт
        self.cards_found = []
        self.unique_ids = set()
        self.unique_card_ids = set()
        self.id_counter = Counter()
        self.card_id_counter = Counter()

        for controller_value, cards in self.cards_by_controller.items():
            if self.target_controller_value is None or controller_value == self.target_controller_value:
                for entity_id, card_id in cards:
                    self.cards_found.append((entity_id, card_id))
                    self.unique_ids.add(entity_id)
                    self.unique_card_ids.add(card_id)
                    self.id_counter[entity_id] += 1
                    self.card_id_counter[card_id] += 1

    # ========== Существующие методы (обновлены) ==========

    def get_all_cards(self) -> List[Tuple[str, str]]:
        """Возвращает список всех найденных карт в порядке обнаружения."""
        return self.cards_found.copy()

    def get_unique_ids(self) -> Set[str]:
        """Возвращает множество уникальных ID сущностей."""
        return self.unique_ids.copy()

    def get_unique_card_ids(self) -> Set[str]:
        """Возвращает множество уникальных CardID."""
        return self.unique_card_ids.copy()

    def get_cards_by_entity_id(self, entity_id: str) -> List[str]:
        """Возвращает все CardID для конкретного ID сущности."""
        return [card_id for e_id, card_id in self.cards_found if e_id == entity_id]

    def get_entities_by_card_id(self, card_id: str) -> List[str]:
        """Возвращает все ID сущностей для конкретной карты."""
        return [e_id for e_id, c_id in self.cards_found if c_id == card_id]

    def get_statistics(self) -> dict:
        """Возвращает подробную статистику по найденным картам."""
        return {
            'total_cards_found': len(self.cards_found),
            'unique_entities': len(self.unique_ids),
            'unique_cards': len(self.unique_card_ids),
            'target_controller': self.target_controller_value,
            'controller_values_found': list(self.controller_values_found),
            'controller_statistics': self.get_controller_statistics(),
            'entity_frequency': dict(self.id_counter),
            'card_frequency': dict(self.card_id_counter),
            'most_common_entities': self.id_counter.most_common(10),
            'most_common_cards': self.card_id_counter.most_common(10),
        }

    def get_cards_summary(self) -> List[Tuple[str, int, List[str]]]:
        """Возвращает сводку по картам: (CardID, количество, список ID сущностей)"""
        summary = []
        for card_id in sorted(self.unique_card_ids):
            count = self.card_id_counter[card_id]
            entities = self.get_entities_by_card_id(card_id)
            summary.append((card_id, count, entities))
        return summary

    def search_by_card_pattern(self, pattern: str) -> List[Tuple[str, str]]:
        """Поиск карт по паттерну в CardID."""
        regex = re.compile(pattern)
        return [(e_id, c_id) for e_id, c_id in self.cards_found if regex.search(c_id)]

    def export_to_dict(self) -> dict:
        """Экспортирует данные в словарь для удобного сохранения."""
        return {
            'cards': [
                {'entity_id': e_id, 'card_id': c_id}
                for e_id, c_id in self.cards_found
            ],
            'cards_by_controller': {
                str(controller): [
                    {'entity_id': e_id, 'card_id': c_id}
                    for e_id, c_id in cards
                ]
                for controller, cards in self.cards_by_controller.items()
            },
            'statistics': self.get_statistics(),
            'unique_entities': list(self.unique_ids),
            'unique_cards': list(self.unique_card_ids),
            'controller_values': list(self.controller_values_found)
        }


# ========== Примеры использования ==========

def example_usage():
    """Примеры использования обновленного парсера."""

    # Создаем парсер с настройкой по умолчанию (value=13)
    parser = TavernCardsParser('Power.log', target_controller_value=13)

    # Получаем все найденные значения CONTROLLER
    print("Найденные значения CONTROLLER:", parser.get_controller_values())

    # Статистика по значениям CONTROLLER
    print("\nСтатистика по CONTROLLER:")
    for value, count in parser.get_controller_statistics().items():
        print(f"  value={value}: {count} карт")

    # Меняем целевое значение
    parser.set_target_controller(2)  # Например, для противника
    print(f"\nПосле смены target на 2: {len(parser.get_all_cards())} карт")

    # Получаем карты для конкретного значения
    cards_for_13 = parser.get_cards_by_controller_value(13)
    print(f"\nКарты с CONTROLLER=13: {len(cards_for_13)}")

    # Возвращаемся к value=13
    parser.set_target_controller(13)

    return parser


if __name__ == "__main__":
    # Пример использования
    parser = example_usage()