"""
Пользовательский интерфейс для парсера ID.
"""

import os
from typing import Optional
from ..core.id_parser import IDParser
from ..utils.file_handler import save_ids_to_file
from ..config.settings import DEFAULT_ENCODING


def run_id_parser():
    """Запускает парсер ID в интерактивном режиме."""
    print("\n" + "=" * 60)
    print("ПАРСЕР ID - СБОР ВСЕХ УНИКАЛЬНЫХ ID")
    print("=" * 60)

    # Получаем файл
    filename = input("\nВведите путь к лог-файлу: ").strip()

    if not os.path.exists(filename):
        print(f"Ошибка: Файл '{filename}' не найден.")
        return

    # Получаем кодировку
    encoding = input(f"Введите кодировку (Enter для {DEFAULT_ENCODING}): ").strip()
    if not encoding:
        encoding = DEFAULT_ENCODING

    print(f"\nАнализирую файл: {filename}")
    print("Это может занять некоторое время...")

    try:
        # Создаем парсер и анализируем файл
        parser = IDParser(filename, encoding)

        # Получаем результаты
        all_ids = parser.get_all_ids()
        stats = parser.get_id_statistics()

        # Выводим результаты
        _display_results(parser, all_ids, stats)

        # Дополнительные опции
        _handle_parser_options(parser)

    except Exception as e:
        print(f"Ошибка при анализе файла: {e}")


def _display_results(parser: IDParser, all_ids: set, stats: dict):
    """Отображает результаты парсинга."""

    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ АНАЛИЗА")
    print("=" * 60)

    print(f"\n📊 Статистика:")
    print(f"   • Найдено уникальных ID: {stats['total_unique_ids']}")
    print(f"   • Всего вхождений ID: {stats['total_occurrences']}")

    if all_ids:
        print(f"\n🔍 Найденные ID (первые 20 из {len(all_ids)}):")

        # Сортируем ID как числа
        sorted_ids = sorted(all_ids, key=int)

        for i, id_val in enumerate(sorted_ids[:20], 1):
            count = stats['id_frequency'][id_val]
            print(f"   {i:2d}. ID: {id_val:8} (встречается: {count} раз)")

        if len(sorted_ids) > 20:
            print(f"   ... и еще {len(sorted_ids) - 20} ID")

        # Показываем топ-10 самых частых ID
        if stats['most_common']:
            print(f"\n📈 Топ-10 самых частых ID:")
            for id_val, count in stats['most_common'][:10]:
                print(f"   • ID {id_val}: {count} раз")
    else:
        print("\n❌ ID не найдены в файле.")


def _handle_parser_options(parser: IDParser):
    """Обрабатывает дополнительные опции парсера."""

    while True:
        print("\n" + "-" * 40)
        print("Доступные действия:")
        print("1. Показать все ID")
        print("2. Найти строки с конкретным ID")
        print("3. Поиск ID по шаблону")
        print("4. Сохранить результаты в файл")
        print("5. Показать статистику")
        print("6. Выйти")

        choice = input("\nВыберите действие (1-6): ").strip()

        if choice == '1':
            _show_all_ids(parser)
        elif choice == '2':
            _find_lines_for_id(parser)
        elif choice == '3':
            _search_by_pattern(parser)
        elif choice == '4':
            _save_results(parser)
        elif choice == '5':
            _show_detailed_stats(parser)
        elif choice == '6':
            break
        else:
            print("Неверный выбор. Попробуйте снова.")


def _show_all_ids(parser: IDParser):
    """Показывает все найденные ID."""
    all_ids = parser.get_ids_sorted()

    if not all_ids:
        print("ID не найдены.")
        return

    print(f"\nВсе найденные ID (всего {len(all_ids)}):")
    print("-" * 40)

    # Показываем ID с группировкой
    for i, id_val in enumerate(all_ids, 1):
        count = parser.id_counter[id_val]
        print(f"{i:4d}. ID: {id_val:8} (вхождений: {count})")

        # Делаем паузу каждые 20 строк
        if i % 20 == 0:
            if input("\nПродолжить? (Enter для продолжения, q для выхода): ").lower() == 'q':
                break


def _find_lines_for_id(parser: IDParser):
    """Ищет строки с конкретным ID."""
    target_id = input("\nВведите ID для поиска: ").strip()

    if not target_id:
        return

    lines = parser.get_lines_for_id(target_id)

    if not lines:
        print(f"ID {target_id} не найден в файле.")
        return

    print(f"\nНайдено {len(lines)} строк с ID {target_id}:")
    print("-" * 40)

    for i, (line_num, line) in enumerate(lines[:10], 1):
        print(f"\n[{i}] Строка {line_num}:")
        print(f"{line[:200]}{'...' if len(line) > 200 else ''}")

    if len(lines) > 10:
        print(f"\n... и еще {len(lines) - 10} строк")

    # Спрашиваем, сохранить ли результаты
    if lines and input("\nСохранить все строки в файл? (y/n): ").lower() == 'y':
        filename = f"id_{target_id}_lines.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            for line_num, line in lines:
                f.write(f"[Строка {line_num}] {line}\n")
        print(f"Сохранено в {filename}")


def _search_by_pattern(parser: IDParser):
    """Поиск ID по регулярному выражению."""
    print("\nПоиск ID по шаблону (регулярное выражение)")
    print("Примеры:")
    print("  ^1    - ID начинающиеся с 1")
    print("  5$    - ID заканчивающиеся на 5")
    print("  123   - ID содержащие 123")

    pattern = input("\nВведите шаблон: ").strip()

    if not pattern:
        return

    matching_ids = parser.find_ids_by_pattern(pattern)

    if not matching_ids:
        print("ID, соответствующие шаблону, не найдены.")
        return

    print(f"\nНайдено ID: {len(matching_ids)}")
    sorted_ids = sorted(matching_ids, key=int)

    for i, id_val in enumerate(sorted_ids[:20], 1):
        print(f"{i:4d}. {id_val}")

    if len(sorted_ids) > 20:
        print(f"... и еще {len(sorted_ids) - 20} ID")


def _save_results(parser: IDParser):
    """Сохраняет результаты в файл."""
    filename = input("Имя файла для сохранения (по умолчанию ids_results.txt): ").strip()
    if not filename:
        filename = "ids_results.txt"

    save_ids_to_file(parser, filename)


def _show_detailed_stats(parser: IDParser):
    """Показывает детальную статистику."""
    stats = parser.get_id_statistics()

    print("\n" + "=" * 50)
    print("ДЕТАЛЬНАЯ СТАТИСТИКА")
    print("=" * 50)

    print(f"\n📊 Общая статистика:")
    print(f"   • Уникальных ID: {stats['total_unique_ids']}")
    print(f"   • Всего вхождений: {stats['total_occurrences']}")

    if stats['total_unique_ids'] > 0:
        print(f"   • Среднее вхождений на ID: {stats['total_occurrences'] / stats['total_unique_ids']:.2f}")

    print(f"\n📈 Распределение:")
    id_counts = list(stats['id_frequency'].values())
    if id_counts:
        print(f"   • Минимум вхождений: {min(id_counts)}")
        print(f"   • Максимум вхождений: {max(id_counts)}")

    if stats['most_common']:
        print(f"\n🏆 Топ-5 самых частых ID:")
        for id_val, count in stats['most_common'][:5]:
            percentage = (count / stats['total_occurrences']) * 100
            print(f"   {id_val}: {count} раз ({percentage:.1f}%)")