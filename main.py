#!/usr/bin/env python3
"""
Log Analyzer - Главный модуль приложения
Поддерживает несколько парсеров для анализа логов
"""

import sys
import os
from src.core.id_parser import IDParser
from src.core.tavern_cards_parser import TavernCardsParser  # Импортируем новый парсер
from src.ui.id_parser_ui import run_id_parser
from src.ui.tavern_cards_parser_ui import run_tavern_cards_parser  # Импортируем новый UI
from src.config.settings import DEFAULT_ENCODING


def clear_screen():
    """Очищает экран"""
    os.system('cls' if os.name == 'nt' else 'clear')


def show_main_menu():
    """Показывает главное меню"""
    while True:
        clear_screen()
        print("=" * 60)
        print("           LOG ANALYZER - ГЛАВНОЕ МЕНЮ")
        print("=" * 60)
        print("\nДоступные парсеры:")
        print("1.Парсер ID - поиск всех уникальных ID")
        print("2.Парсер карт таверны - поиск карт игрока")
        print("3.Выход")
        print("-" * 60)

        choice = input("\nВыберите парсер (1-3): ").strip()

        if choice == '1':
            run_id_parser()
            input("\nНажмите Enter для продолжения...")

        elif choice == '2':
            try:
                run_tavern_cards_parser()
            except Exception as e:
                print(f"\n Ошибка: {e}")
            input("\nНажмите Enter для продолжения...")

        elif choice == '3':
            print("\nДо свидания!")
            sys.exit(0)

        else:
            print("\nНеверный выбор. Нажмите Enter и попробуйте снова.")
            input()


def main():
    """Основная функция приложения."""
    print("=" * 60)
    print("           LOG ANALYZER v2.0")
    print("   Мультиинструмент для анализа логов")
    print("=" * 60)

    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        # Прямой запуск конкретного парсера
        parser_type = sys.argv[1]
        file_path = sys.argv[2] if len(sys.argv) > 2 else None

        if not file_path:
            print("Укажите путь к файлу")
            print("Пример: python main.py id log.txt")
            return

        if parser_type == 'id':
            try:
                parser = IDParser(file_path, DEFAULT_ENCODING)
                print(f"\n Статистика по файлу {file_path}:")
                print(f"Уникальных ID: {len(parser.get_all_ids())}")
                print(f"Всего вхождений: {parser.get_id_statistics()['total_occurrences']}")
            except Exception as e:
                print(f" Ошибка: {e}")

        elif parser_type == 'tavern':
            try:
                parser = TavernCardsParser(file_path, DEFAULT_ENCODING)
                cards = parser.get_all_cards()
                stats = parser.get_statistics()
                print(f"\n Статистика по файлу {file_path}:")
                print(f"  Найдено карт: {len(cards)}")
                print(f"  Уникальных карт: {stats['unique_cards']}")
                if cards:
                    print("\n Первые 10 карт:")
                    for i, (entity_id, card_id) in enumerate(cards[:10], 1):
                        print(f"   {i:2d}. ID: {entity_id} → Карта: {card_id}")
            except Exception as e:
                print(f" Ошибка: {e}")

        else:
            print(f" Неизвестный тип парсера: {parser_type}")
            print("Доступные: id, tavern")
    else:
        # Интерактивный режим с меню
        show_main_menu()


if __name__ == "__main__":
    main()