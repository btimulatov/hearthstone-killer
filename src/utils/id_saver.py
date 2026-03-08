"""
Утилиты для сохранения результатов парсинга ID.
"""

from ..core.id_parser import IDParser


def save_ids_to_file(parser: IDParser, filename: str):
    """
    Сохраняет все найденные ID в файл.

    Args:
        parser: Экземпляр IDParser
        filename: Имя файла для сохранения
    """
    all_ids = parser.get_ids_sorted()
    stats = parser.get_id_statistics()

    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("РЕЗУЛЬТАТЫ ПАРСИНГА ID\n")
        f.write("=" * 60 + "\n\n")

        # Статистика
        f.write("📊 СТАТИСТИКА:\n")
        f.write(f"   Уникальных ID: {stats['total_unique_ids']}\n")
        f.write(f"   Всего вхождений: {stats['total_occurrences']}\n\n")

        # Все ID
        f.write("🔍 НАЙДЕННЫЕ ID:\n")
        f.write("-" * 40 + "\n")

        for i, id_val in enumerate(all_ids, 1):
            count = parser.id_counter[id_val]
            f.write(f"{i:4d}. ID: {id_val:8} (вхождений: {count})\n")

        # Топ частых ID
        if stats['most_common']:
            f.write("\n📈 ТОП-10 САМЫХ ЧАСТЫХ ID:\n")
            f.write("-" * 40 + "\n")
            for id_val, count in stats['most_common'][:10]:
                percentage = (count / stats['total_occurrences']) * 100
                f.write(f"   ID {id_val}: {count} раз ({percentage:.1f}%)\n")

    print(f"\n✅ Результаты сохранены в файл: {filename}")


def save_id_lines_to_file(parser: IDParser, target_id: str, filename: str = None):
    """
    Сохраняет все строки с конкретным ID в файл.

    Args:
        parser: Экземпляр IDParser
        target_id: ID для поиска
        filename: Имя файла (если None, генерируется автоматически)
    """
    if filename is None:
        filename = f"id_{target_id}_lines.txt"

    lines = parser.get_lines_for_id(target_id)

    if not lines:
        print(f"ID {target_id} не найден.")
        return

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Строки, содержащие ID {target_id}\n")
        f.write(f"Всего найдено: {len(lines)} строк\n")
        f.write("=" * 60 + "\n\n")

        for line_num, line in lines:
            f.write(f"[Строка {line_num}]\n")
            f.write(f"{line}\n")
            f.write("-" * 40 + "\n")

    print(f"\n✅ Строки сохранены в файл: {filename}")