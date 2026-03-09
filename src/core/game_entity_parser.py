"""
Парсер для извлечения EntityID и PlayerID из логов Hearthstone.
Ищет две конкретные строки и достает по одному значению из каждой.
"""

import re
from typing import List, Tuple, Optional, Dict


class GameEntityParser:
    """
    Парсер для извлечения:
    - EntityID из строки: GameState.DebugPrintPower() -     GameEntity EntityID=
    - PlayerID из строки: GameState.DebugPrintPower() -     Player EntityID= PlayerID=
    """

    def __init__(self, file_path: str, encoding: str = 'utf-8'):
        """
        Инициализация парсера.

        Args:
            file_path: Путь к лог-файлу
            encoding: Кодировка файла
        """
        self.file_path = file_path
        self.encoding = encoding

        # Результаты
        self.game_entity_id = None  # EntityID из первой строки
        self.player_ids = []  # Список PlayerID из второй строки (может быть несколько игроков)

        # Для отслеживания позиций (опционально)
        self.game_entity_line = None
        self.player_lines = []

        self._parse_file()

    def _parse_file(self) -> None:
        """Парсит файл и извлекает нужные ID."""
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as file:
                for line_num, line in enumerate(file, 1):
                    line = line.rstrip('\n')

                    # ШАГ 1: Ищем первую строку с GameEntity
                    if self.game_entity_id is None:  # Ищем только первый раз
                        entity_id = self._extract_game_entity_id(line)
                        if entity_id:
                            self.game_entity_id = entity_id
                            self.game_entity_line = line_num
                            continue  # Переходим к следующей строке

                    # ШАГ 2: Ищем все строки с Player (их может быть несколько)
                    player_id = self._extract_player_id(line)
                    if player_id:
                        self.player_ids.append(player_id)
                        self.player_lines.append((line_num, player_id))

            # Сортируем PlayerID (если нужно)
            self.player_ids.sort()

        except FileNotFoundError:
            raise FileNotFoundError(f"Файл '{self.file_path}' не найден.")
        except UnicodeDecodeError:
            raise UnicodeDecodeError(f"Ошибка кодировки. Попробуйте другую кодировку.")

    def _extract_game_entity_id(self, line: str) -> Optional[str]:
        """
        Извлекает EntityID из строки с GameEntity.

        Формат: GameState.DebugPrintPower() -     GameEntity EntityID=XXX

        Args:
            line: Строка для парсинга

        Returns:
            EntityID или None
        """
        # Точный паттерн для GameEntity
        pattern = r'GameState\.DebugPrintPower\(\) - +\s*GameEntity EntityID=(\d+)'

        match = re.search(pattern, line)
        if match:
            return match.group(1)  # Возвращаем только EntityID

        return None

    def _extract_player_id(self, line: str) -> Optional[str]:
        """
        Извлекает PlayerID из строки с Player.

        Формат: GameState.DebugPrintPower() -     Player EntityID=XXX PlayerID=YYY

        Args:
            line: Строка для парсинга

        Returns:
            PlayerID или None
        """
        # Паттерн для Player - ищем PlayerID после EntityID
        # Используем позитивный просмотр вперед, чтобы убедиться, что это строка с Player
        pattern = r'GameState\.DebugPrintPower\(\) - +\s*Player EntityID=\d+ PlayerID=(\d+)'

        match = re.search(pattern, line)
        if match:
            return match.group(1)  # Возвращаем только PlayerID

        return None

    # ========== Методы для получения результатов ==========

    def get_game_entity_id(self) -> Optional[str]:
        """Возвращает EntityID из GameEntity (первая найденная строка)."""
        return self.game_entity_id

    def get_player_ids(self) -> List[str]:
        """Возвращает список всех PlayerID."""
        return self.player_ids.copy()

    def get_first_player_id(self) -> Optional[str]:
        """Возвращает первый PlayerID (если есть)."""
        return self.player_ids[0] if self.player_ids else None

    def get_player_count(self) -> int:
        """Возвращает количество найденных игроков."""
        return len(self.player_ids)

    def get_all_results(self) -> Dict[str, any]:
        """Возвращает все результаты в виде словаря."""
        return {
            'game_entity_id': self.game_entity_id,
            'player_ids': self.player_ids,
            'player_count': len(self.player_ids),
            'game_entity_line': self.game_entity_line,
            'player_lines': self.player_lines
        }

    def print_summary(self) -> None:
        """Выводит краткую сводку результатов."""
        print("=" * 50)
        print("РЕЗУЛЬТАТЫ ПАРСИНГА:")
        print("=" * 50)
        print(f"GameEntity ID: {self.game_entity_id or 'НЕ НАЙДЕН'}")
        print(f"Найдено игроков: {len(self.player_ids)}")
        for i, player_id in enumerate(self.player_ids, 1):
            print(f"  Игрок {i}: PlayerID={player_id}")
        print("=" * 50)

# ========== Пример использования ==========

if __name__ == "__main__":
    # Пример использования
    parser = GameEntityParser("Power.log")

    # Получаем результаты
    game_id = parser.get_game_entity_id()
    players = parser.get_player_ids()

    print(f"Game Entity ID: {game_id}")
    print(f"Players: {players}")

    # Или выводим сводку
    parser.print_summary()