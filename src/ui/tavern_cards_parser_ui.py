"""
Пользовательский интерфейс для парсера карт таверны.
Обновлен для работы с разными значениями CONTROLLER.
"""

import os
import json
from typing import Optional
from ..core.tavern_cards_parser import TavernCardsParser
from ..config.settings import DEFAULT_ENCODING


def run_tavern_cards_parser():
    """Запускает парсер карт таверны."""
    print("\n" + "=" * 70)
    print("ПАРСЕР КАРТ ТАВЕРНЫ - РАСШИРЕННАЯ ВЕРСИЯ")
    print("=" * 70)
    print("\nАнализирует карты, появляющиеся в таверне")
    print("Отслеживает все значения CONTROLLER (владелец карты)")
    print("По умолчанию value=13 - игрок, value=2 - противник и т.д.")

    # Получаем файл
    filename = input("\nВведите путь к лог-файлу: ").strip()

    if not os.path.exists(filename):
        print(f"Ошибка: Файл '{filename}' не найден.")
        return

    # Получаем кодировку
    encoding = input(f"Введите кодировку (Enter для {DEFAULT_ENCODING}): ").strip()
    if not encoding:
        encoding = DEFAULT_ENCODING

    # Спрашиваем, какое значение CONTROLLER интересует
    print("\nЗначения CONTROLLER:")
    print("   13 - Игрок")
    print("   2  - Противник")
    print("   6  - Нейтральные/объекты")
    print("   1  - Другое")
    print("   0  - Показать все значения")

    controller_input = input("\nВведите значение CONTROLLER для фильтрации (Enter для 13): ").strip()

    target_controller = None
    if controller_input:
        try:
            target_controller = int(controller_input)
        except ValueError:
            print("Неверный формат, использую значение по умолчанию (13)")
            target_controller = 13
    else:
        target_controller = 13

    print(f"\nАнализирую файл: {filename}")
    if target_controller is not None:
        print(f"Фильтр: CONTROLLER={target_controller}")
    else:
        print("Фильтр: ВСЕ значения CONTROLLER")

    try:
        # Создаем парсер
        parser = TavernCardsParser(filename, encoding, target_controller)

        # Получаем результаты
        cards = parser.get_all_cards()
        stats = parser.get_statistics()

        # Выводим результаты
        _display_results(parser, cards, stats)

        # Дополнительные опции
        _handle_parser_options(parser)

    except Exception as e:
        print(f"Ошибка при анализе файла: {e}")


def _display_results(parser: TavernCardsParser, cards: list, stats: dict):
    """Отображает результаты парсинга."""

    print("\n" + "=" * 70)
    print(" РЕЗУЛЬТАТЫ АНАЛИЗА КАРТ ТАВЕРНЫ")
    print("=" * 70)

    if not cards:
        print("\n Не найдено карт.")
        if parser.target_controller_value is not None:
            print(f"   Искал карты с CONTROLLER={parser.target_controller_value}")
        else:
            print("   Искал ВСЕ карты")

        # Показываем, какие значения CONTROLLER есть в логе
        ctrl_values = parser.get_controller_values()
        if ctrl_values:
            print(f"\nНайденные значения CONTROLLER в логе: {sorted(ctrl_values)}")
        return

    # Основная статистика
    print(f"\nСтатистика:")
    print(f"Всего карт найдено: {stats['total_cards_found']}")
    print(f"Уникальных ID сущностей: {stats['unique_entities']}")
    print(f"Уникальных CardID: {stats['unique_cards']}")

    if parser.target_controller_value is not None:
        print(f"Текущий фильтр: CONTROLLER={parser.target_controller_value}")
    else:
        print(f"Текущий фильтр: ВСЕ значения")

    # Информация о всех значениях CONTROLLER
    ctrl_values = parser.get_controller_values()
    if ctrl_values:
        print(f"\nРаспределение по значениям CONTROLLER:")
        ctrl_stats = parser.get_controller_statistics()
        for value in sorted(ctrl_values):
            count = ctrl_stats.get(value, 0)
            bar = '' * int(count / max(ctrl_stats.values()) * 20) if ctrl_stats else ''
            print(f"   value={value:2}: {count:3} карт {bar}")

    # Последние найденные карты
    print(f"\nПоследние 10 найденных карт:")
    print("-" * 50)
    start_idx = max(1, len(cards) - 9)
    for i, (entity_id, card_id) in enumerate(cards[-10:], start_idx):
        print(f"   {i:4d}. [ID: {entity_id:8}] → [Карта: {card_id}]")

    # Топ карт
    if stats['most_common_cards']:
        print(f"\n Топ-5 самых частых карт:")
        max_count = stats['most_common_cards'][0][1] if stats['most_common_cards'] else 1
        for card_id, count in stats['most_common_cards'][:5]:
            bar = '' * int(count / max_count * 20)
            print(f"   {card_id:25}: {count:3} раз {bar}")


def _handle_parser_options(parser: TavernCardsParser):
    """Обрабатывает дополнительные опции парсера."""

    while True:
        print("\n" + "-" * 60)
        print("ДОСТУПНЫЕ ДЕЙСТВИЯ:")
        print("1. Показать все найденные карты")
        print("2. Показать все уникальные CardID")
        print("3. Показать все уникальные ID сущностей")
        print("4. Поиск по CardID")
        print("5. Детальная статистика")
        print("6. Работа со значениями CONTROLLER")
        print("7. Сохранить результаты")
        print("8. Выйти")

        choice = input("\nВыберите действие (1-8): ").strip()

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
            _handle_controller_options(parser)
        elif choice == '7':
            _save_results(parser)
        elif choice == '8':
            break
        else:
            print("Неверный выбор.")


def _handle_controller_options(parser: TavernCardsParser):
    """Обрабатывает опции связанные с CONTROLLER."""

    while True:
        print("\n" + "-" * 50)
        print("🎮 РАБОТА СО ЗНАЧЕНИЯМИ CONTROLLER")
        print(f"Текущий фильтр: {parser.target_controller_value if parser.target_controller_value is not None else 'ВСЕ'}")

        # Показываем доступные значения
        ctrl_values = parser.get_controller_values()
        if ctrl_values:
            print("\nДоступные значения:")
            ctrl_stats = parser.get_controller_statistics()
            for value in sorted(ctrl_values):
                print(f"   value={value:2}: {ctrl_stats.get(value, 0)} карт")

        print("\nДействия:")
        print("1. Сменить фильтр CONTROLLER")
        print("2. Показать карты для конкретного значения")
        print("3. Показать статистику по всем значениям")
        print("4. Вернуться в главное меню")

        choice = input("\nВыберите действие (1-4): ").strip()

        if choice == '1':
            _change_controller_filter(parser)
        elif choice == '2':
            _show_cards_by_controller(parser)
        elif choice == '3':
            _show_controller_statistics(parser)
        elif choice == '4':
            break
        else:
            print("Неверный выбор.")


def _change_controller_filter(parser: TavernCardsParser):
    """Изменяет фильтр CONTROLLER."""
    print("\nДоступные значения:", sorted(parser.get_controller_values()))
    print("   Введите число для фильтрации")
    print("   или 'all' для показа всех значений")

    value = input("Новое значение: ").strip().lower()

    if value == 'all':
        parser.set_target_controller(None)
        print("Фильтр сброшен - показываются ВСЕ значения")
    else:
        try:
            val = int(value)
            if val in parser.get_controller_values():
                parser.set_target_controller(val)
                print(f"Фильтр изменен: CONTROLLER={val}")
            else:
                print(f"Значение {val} не найдено в логе")
                print("   Фильтр не изменен")
        except ValueError:
            print("Неверный формат")


def _show_cards_by_controller(parser: TavernCardsParser):
    """Показывает карты для конкретного значения CONTROLLER."""
    print("\nДоступные значения:", sorted(parser.get_controller_values()))

    try:
        value = int(input("Введите значение CONTROLLER: ").strip())
        cards = parser.get_cards_by_controller_value(value)

        if cards:
            print(f"\nКарты с CONTROLLER={value} (всего {len(cards)}):")
            print("-" * 50)
            for i, (entity_id, card_id) in enumerate(cards[:20], 1):
                print(f"{i:4d}. ID: {entity_id:8} → Карта: {card_id}")
            if len(cards) > 20:
                print(f"... и еще {len(cards) - 20} карт")
        else:
            print(f"Карт с CONTROLLER={value} не найдено")
    except ValueError:
        print("Неверный формат")


def _show_controller_statistics(parser: TavernCardsParser):
    """Показывает детальную статистику по значениям CONTROLLER."""
    stats = parser.get_controller_statistics()
    values = sorted(stats.keys())

    if not values:
        print("Нет данных по значениям CONTROLLER")
        return

    print("\n" + "=" * 60)
    print("СТАТИСТИКА ПО ЗНАЧЕНИЯМ CONTROLLER")
    print("=" * 60)

    total_cards = sum(stats.values())
    max_count = max(stats.values())

    for value in values:
        count = stats[value]
        percentage = (count / total_cards) * 100 if total_cards > 0 else 0
        bar = '' * int(count / max_count * 20) if max_count > 0 else ''

        print(f"\nCONTROLLER={value:2}:")
        print(f"   Карт: {count:3} ({percentage:5.1f}%)")
        print(f"   Распределение: {bar}")

        # Показываем топ карт для этого значения
        cards = parser.get_cards_by_controller_value(value)
        if cards:
            card_counter = {}
            for _, card_id in cards:
                card_counter[card_id] = card_counter.get(card_id, 0) + 1

            top_cards = sorted(card_counter.items(), key=lambda x: x[1], reverse=True)[:3]
            if top_cards:
                print(f"   Топ-3 карты:")
                for card_id, cnt in top_cards:
                    print(f"      {card_id}: {cnt} раз")


def _show_all_cards(parser: TavernCardsParser):
    """Показывает все найденные карты."""
    cards = parser.get_all_cards()

    if not cards:
        print("Карты не найдены.")
        return

    print(f"\nВсе найденные карты (всего {len(cards)}):")
    print("-" * 50)

    for i, (entity_id, card_id) in enumerate(cards, 1):
        print(f"{i:4d}. [ID: {entity_id:8}] → [Карта: {card_id}]")

        if i % 20 == 0 and i < len(cards):
            if input("\nПродолжить? (Enter для продолжения, q для выхода): ").lower() == 'q':
                break


def _show_unique_card_ids(parser: TavernCardsParser):
    """Показывает все уникальные CardID."""
    card_ids = sorted(parser.get_unique_card_ids())

    if not card_ids:
        print("CardID не найдены.")
        return

    print(f"\nУникальные CardID (всего {len(card_ids)}):")
    print("-" * 50)

    for i, card_id in enumerate(card_ids, 1):
        count = parser.card_id_counter[card_id]
        bar = '' * int(count / max(parser.card_id_counter.values()) * 10) if parser.card_id_counter else ''
        print(f"{i:4d}. {card_id:25} {count:3} раз {bar}")


def _show_unique_entity_ids(parser: TavernCardsParser):
    """Показывает все уникальные ID сущностей."""
    entity_ids = sorted(parser.get_unique_ids(), key=int)

    if not entity_ids:
        print("ID сущностей не найдены.")
        return

    print(f"\nУникальные ID сущностей (всего {len(entity_ids)}):")
    print("-" * 50)

    for i, entity_id in enumerate(entity_ids, 1):
        count = parser.id_counter[entity_id]
        print(f"{i:4d}. ID: {entity_id:8} (карт: {count})")


def _search_by_card(parser: TavernCardsParser):
    """Поиск по CardID."""
    print("\nПоиск по CardID")
    print("Примеры: AT_001, LOOT_*, *_t, BGS_*")

    pattern = input("\nВведите CardID или паттерн: ").strip()

    if not pattern:
        return

    # Определяем тип поиска
    if '*' in pattern:
        # Конвертируем * в regex
        regex_pattern = pattern.replace('*', '.*')
        results = parser.search_by_card_pattern(regex_pattern)
        search_type = "паттерну"
    else:
        # Точный поиск
        results = [(e_id, c_id) for e_id, c_id in parser.get_all_cards() if c_id == pattern]
        search_type = "точному совпадению"

    if results:
        print(f"\nНайдено карт по {search_type} '{pattern}': {len(results)}")

        # Группируем по значениям CONTROLLER
        by_controller = {}
        for e_id, c_id in results:
            # Находим значение контроллера для этой карты
            for ctrl_val, cards in parser.cards_by_controller.items():
                if (e_id, c_id) in cards:
                    if ctrl_val not in by_controller:
                        by_controller[ctrl_val] = []
                    by_controller[ctrl_val].append((e_id, c_id))
                    break

        # Показываем результаты
        for ctrl_val in sorted(by_controller.keys()):
            cards = by_controller[ctrl_val]
            print(f"\n   CONTROLLER={ctrl_val} ({len(cards)} карт):")
            for e_id, c_id in cards[:5]:
                print(f"      ID: {e_id} → {c_id}")
            if len(cards) > 5:
                print(f"      ... и еще {len(cards) - 5}")
    else:
        print(f"Ничего не найдено по {search_type} '{pattern}'.")


def _show_detailed_stats(parser: TavernCardsParser):
    """Показывает детальную статистику."""
    stats = parser.get_statistics()

    print("\n" + "=" * 60)
    print("ДЕТАЛЬНАЯ СТАТИСТИКА")
    print("=" * 60)

    print(f"\nОбщая статистика:")
    print(f"   • Всего карт: {stats['total_cards_found']}")
    print(f"   • Уникальных ID: {stats['unique_entities']}")
    print(f"   • Уникальных CardID: {stats['unique_cards']}")
    print(f"   • Значений CONTROLLER: {len(stats['controller_values_found'])}")

    if stats['most_common_cards']:
        print(f"\Топ-10 самых частых карт:")
        total = stats['total_cards_found']
        for card_id, count in stats['most_common_cards']:
            percentage = (count / total) * 100
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
    print("3. CSV файл (.csv)")

    choice = input("Выберите формат (1-3): ").strip()

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
    elif choice == '3':
        filename = input("Имя файла (по умолчанию tavern_cards.csv): ").strip()
        if not filename:
            filename = "tavern_cards.csv"
        _save_as_csv(parser, filename)
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
        f.write(f"Фильтр CONTROLLER: {parser.target_controller_value if parser.target_controller_value is not None else 'ВСЕ'}\n")
        f.write("=" * 70 + "\n\n")

        f.write("СТАТИСТИКА:\n")
        f.write(f"   Всего карт: {stats['total_cards_found']}\n")
        f.write(f"   Уникальных ID: {stats['unique_entities']}\n")
        f.write(f"   Уникальных CardID: {stats['unique_cards']}\n\n")

        f.write("РАСПРЕДЕЛЕНИЕ ПО CONTROLLER:\n")
        ctrl_stats = parser.get_controller_statistics()
        for value, count in sorted(ctrl_stats.items()):
            f.write(f"   value={value}: {count} карт\n")
        f.write("\n")

        f.write("ВСЕ НАЙДЕННЫЕ КАРТЫ:\n")
        f.write("-" * 50 + "\n")
        for i, (entity_id, card_id) in enumerate(cards, 1):
            f.write(f"{i:4d}. ID: {entity_id:8} → Карта: {card_id}\n")

        f.write("\nТОП-10 САМЫХ ЧАСТЫХ КАРТ:\n")
        for card_id, count in stats['most_common_cards'][:10]:
            f.write(f"   {card_id}: {count} раз\n")

    print(f"Результаты сохранены в {filename}")


def _save_as_json(parser: TavernCardsParser, filename: str):
    """Сохраняет результаты в JSON файл."""
    data = parser.export_to_dict()

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Результаты сохранены в {filename}")


def _save_as_csv(parser: TavernCardsParser, filename: str):
    """Сохраняет результаты в CSV файл."""
    cards = parser.get_all_cards()

    with open(filename, 'w', encoding='utf-8') as f:
        # Заголовки
        f.write("entity_id,card_id,controller_value\n")

        # Данные
        for entity_id, card_id in cards:
            # Находим значение контроллера для этой карты
            controller_value = "unknown"
            for ctrl_val, ctrl_cards in parser.cards_by_controller.items():
                if (entity_id, card_id) in ctrl_cards:
                    controller_value = ctrl_val
                    break
            f.write(f"{entity_id},{card_id},{controller_value}\n")

    print(f"Результаты сохранены в {filename}")