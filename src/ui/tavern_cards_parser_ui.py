"""
Пользовательский интерфейс для парсера карт таверны.
"""

import os
import re
import json
from typing import Optional
from ..core.tavern_cards_parser import TavernCardsParser
from ..config.settings import DEFAULT_ENCODING, COLORS


def run_tavern_cards_parser():
    """Запускает парсер карт таверны."""
    print("\n" + "=" * 70)
    print("ПАРСЕР КАРТ ТАВЕРНЫ - ПОИСК КАРТ ИГРОКА")
    print("=" * 70)
    print("\nИщет карты, которые появляются у игрока (CONTROLLER=13)")
    print("Анализирует связку: FULL_ENTITY + следующая строка с CONTROLLER=13")

    # Получаем файл
    filename = input("\n Введите путь к лог-файлу: ").strip()

    if not os.path.exists(filename):
        print(f" Ошибка: Файл '{filename}' не найден.")
        return

    # Получаем кодировку
    encoding = input(f" Введите кодировку (Enter для {DEFAULT_ENCODING}): ").strip()
    if not encoding:
        encoding = DEFAULT_ENCODING

    print(f"\n Анализирую файл: {filename}")
    print(" Ищу карты игрока...")

    try:
        # Создаем парсер
        parser = TavernCardsParser(filename, encoding)

        # Получаем результаты
        cards = parser.get_all_cards()
        stats = parser.get_statistics()

        # Выводим результаты
        _display_results(parser, cards, stats)

        # Дополнительные опции
        _handle_parser_options(parser)

    except Exception as e:
        print(f" Ошибка при анализе файла: {e}")


def _display_results(parser: TavernCardsParser, cards: list, stats: dict):
    """Отображает результаты парсинга."""

    print("\n" + "=" * 70)
    print(" РЕЗУЛЬТАТЫ АНАЛИЗА КАРТ ТАВЕРНЫ")
    print("=" * 70)

    if not cards:
        print("\n Не найдено карт игрока.")
        print("   Искал связку: FULL_ENTITY + следующая строка с CONTROLLER=13")
        return

    print(f"\n Статистика:")
    print(f" Всего карт найдено: {stats['total_cards_found']}")
    print(f" Уникальных ID сущностей: {stats['unique_entities']}")
    print(f" Уникальных CardID: {stats['unique_cards']}")

    print(f"\n🔍 Последние 10 найденных карт:")
    print("-" * 50)
    for i, (entity_id, card_id) in enumerate(cards[-10:], max(1, len(cards) - 9)):
        print(f"   {i:4d}. ID: {entity_id:8} → Карта: {card_id}")

    if stats['most_common_cards']:
        print(f"\n🏆 Топ-5 самых частых карт:")
        for card_id, count in stats['most_common_cards'][:5]:
            bar = '' * count
            print(f"   {card_id:20}: {count} раз {bar}")


def _handle_parser_options(parser: TavernCardsParser):
    """Обрабатывает дополнительные опции парсера."""

    while True:
        print("\n" + "-" * 60)
        print(" ДОСТУПНЫЕ ДЕЙСТВИЯ:")
        print("1. Показать все найденные карты")
        print("2. Показать все уникальные CardID")
        print("3. Показать все уникальные ID сущностей")
        print("4. Поиск по CardID")
        print("5. Детальная статистика")
        print("6. Сохранить результаты")
        print("7. Выйти")

        choice = input("\nВыберите действие (1-7): ").strip()

        if choice == '1':
            _show_all_cards(parser)
        elif choice == '2':
            _show_unique_card_ids(parser)
        elif choice == '3':
            _show_unique_entity_ids(parser)
        elif choice == '4':
            _search_by_card(parser)
        elif choice == '5':
            _show_detailed_stats(parser)
        elif choice == '6':
            _save_results(parser)
        elif choice == '7':
            break
        else:
            print(" Неверный выбор.")


def _show_all_cards(parser: TavernCardsParser):
    """Показывает все найденные карты."""
    cards = parser.get_all_cards()

    if not cards:
        print(" Карты не найдены.")
        return

    print(f"\n Все найденные карты (всего {len(cards)}):")
    print("-" * 50)

    for i, (entity_id, card_id) in enumerate(cards, 1):
        print(f"{i:4d}. [ID: {entity_id:8}] → [Карта: {card_id}]")

        if i % 20 == 0:
            if input("\nПродолжить? (Enter для продолжения, q для выхода): ").lower() == 'q':
                break


def _show_unique_card_ids(parser: TavernCardsParser):
    """Показывает все уникальные CardID."""
    card_ids = sorted(parser.get_unique_card_ids())

    if not card_ids:
        print(" CardID не найдены.")
        return

    print(f"\n Уникальные CardID (всего {len(card_ids)}):")
    print("-" * 50)

    for i, card_id in enumerate(card_ids, 1):
        count = parser.card_id_counter[card_id]
        print(f"{i:4d}. {card_id:25} (встречается: {count} раз)")


def _show_unique_entity_ids(parser: TavernCardsParser):
    """Показывает все уникальные ID сущностей."""
    entity_ids = sorted(parser.get_unique_ids(), key=int)

    if not entity_ids:
        print(" ID сущностей не найдены.")
        return

    print(f"\n Уникальные ID сущностей (всего {len(entity_ids)}):")
    print("-" * 50)

    for i, entity_id in enumerate(entity_ids, 1):
        count = parser.id_counter[entity_id]
        print(f"{i:4d}. ID: {entity_id:8} (карт: {count})")


def _search_by_card(parser: TavernCardsParser):
    """Поиск по CardID."""
    print("\n Поиск по CardID")
    print("Примеры: AT_001, LOOT_*, *_t")

    pattern = input("\nВведите CardID или паттерн: ").strip()

    if not pattern:
        return

    # Точный поиск
    if '*' not in pattern and not any(c in pattern for c in '.*+?[]{}()'):
        cards = [(e_id, c_id) for e_id, c_id in parser.get_all_cards() if c_id == pattern]
        if cards:
            print(f"\n Найдено карт с CardID '{pattern}': {len(cards)}")
            for e_id, c_id in cards[:10]:
                print(f"   ID: {e_id} → Карта: {c_id}")
        else:
            print(f" CardID '{pattern}' не найден.")
    else:
        # Поиск по паттерну
        results = parser.search_by_card_pattern(pattern)
        if results:
            print(f"\n Найдено карт по паттерну '{pattern}': {len(results)}")
            for e_id, c_id in results[:10]:
                print(f"   ID: {e_id} → Карта: {c_id}")
        else:
            print(f" Ничего не найдено по паттерну '{pattern}'.")


def _show_detailed_stats(parser: TavernCardsParser):
    """Показывает детальную статистику."""
    stats = parser.get_statistics()

    print("\n" + "=" * 60)
    print(" ДЕТАЛЬНАЯ СТАТИСТИКА")
    print("=" * 60)

    print(f"\n Общая статистика:")
    print(f"   • Всего карт: {stats['total_cards_found']}")
    print(f"   • Уникальных ID: {stats['unique_entities']}")
    print(f"   • Уникальных CardID: {stats['unique_cards']}")

    if stats['most_common_cards']:
        print(f"\n Топ-10 самых частых карт:")
        for card_id, count in stats['most_common_cards']:
            percentage = (count / stats['total_cards_found']) * 100
            bar = '' * int(percentage / 2)
            print(f"   {card_id:25}: {count:3} раз {bar} {percentage:5.1f}%")

    if stats['most_common_entities']:
        print(f"\nТоп-10 самых активных ID сущностей:")
        for entity_id, count in stats['most_common_entities']:
            print(f"   ID {entity_id:8}: {count} карт")


def _save_results(parser: TavernCardsParser):
    """Сохраняет результаты в файл."""
    print("\nСохранение результатов")
    print("1. Текстовый файл (.txt)")
    print("2. JSON файл (.json)")

    choice = input("Выберите формат (1-2): ").strip()

    if choice == '1':
        filename = input("Имя файла (по умолчанию tavern_cards.txt): ").strip()
        if not filename:
            filename = "tavern_cards.txt"
        _save_as_text(parser, filename)
    elif choice == '2':
        filename = input("Имя файла (по умолчанию tavern_cards.json): ").strip()
        if not filename:
            filename = "tavern_cards.json"
        _save_as_json(parser, filename)
    else:
        print("Неверный выбор.")


def _save_as_text(parser: TavernCardsParser, filename: str):
    """Сохраняет результаты в текстовый файл."""
    cards = parser.get_all_cards()
    stats = parser.get_statistics()

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write(" РЕЗУЛЬТАТЫ ПАРСЕРА КАРТ ТАВЕРНЫ\n")
        f.write(f"Файл: {parser.file_path}\n")
        f.write("=" * 70 + "\n\n")

        f.write(" СТАТИСТИКА:\n")
        f.write(f"   Всего карт: {stats['total_cards_found']}\n")
        f.write(f"   Уникальных ID: {stats['unique_entities']}\n")
        f.write(f"   Уникальных CardID: {stats['unique_cards']}\n\n")

        f.write(" ВСЕ НАЙДЕННЫЕ КАРТЫ:\n")
        f.write("-" * 50 + "\n")
        for i, (entity_id, card_id) in enumerate(cards, 1):
            f.write(f"{i:4d}. ID: {entity_id:8} → Карта: {card_id}\n")

        f.write("\n ТОП-10 САМЫХ ЧАСТЫХ КАРТ:\n")
        for card_id, count in stats['most_common_cards'][:10]:
            f.write(f"   {card_id}: {count} раз\n")

    print(f"Результаты сохранены в {filename}")


def _save_as_json(parser: TavernCardsParser, filename: str):
    """Сохраняет результаты в JSON файл."""
    data = parser.export_to_dict()

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Результаты сохранены в {filename}")