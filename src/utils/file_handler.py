"""
Утилиты для работы с файлами.
"""

import os
from typing import List, Tuple


def validate_file(file_path: str) -> bool:
    """
    Проверяет существование файла.

    Args:
        file_path: Путь к файлу

    Returns:
        True если файл существует
    """
    return os.path.isfile(file_path)


def save_results(results: List[Tuple[int, str]], output_file: str) -> None:
    """
    Сохраняет результаты в файл.

    Args:
        results: Список результатов
        output_file: Имя выходного файла
    """
    if not results:
        print("Нет результатов для сохранения.")
        return

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Найдено строк: {len(results)}\n")
        f.write("#" + "=" * 50 + "\n\n")

        for i, (line_num, line) in enumerate(results, 1):
            f.write(f"[{i}] Строка {line_num}:\n")
            f.write(f"{line}\n")
            f.write("-" * 40 + "\n")

    print(f"\nРезультаты сохранены в файл: {output_file}")


def read_file_preview(file_path: str, num_lines: int = 10,
                      encoding: str = 'utf-8') -> List[str]:
    """
    Читает первые N строк файла для предпросмотра.

    Args:
        file_path: Путь к файлу
        num_lines: Количество строк
        encoding: Кодировка

    Returns:
        Список строк
    """
    preview = []
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            for i, line in enumerate(f):
                if i >= num_lines:
                    break
                preview.append(line.rstrip('\n'))
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")

    return preview


def save_ids_to_file(parser, filename: str):
    """
    Сохраняет все найденные ID в файл.

    Args:
        parser: Экземпляр IDParser
        filename: Имя файла для сохранения
    """
    all_ids = parser.get_ids_sorted()
    stats = parser.get_id_statistics()

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"УНИКАЛЬНЫЕ ID ИЗ ФАЙЛА: {parser.file_path}\n")
        f.write(f"Всего найдено: {len(all_ids)}\n")
        f.write("=" * 50 + "\n\n")

        for i, id_val in enumerate(all_ids, 1):
            count = stats['id_frequency'][id_val]
            f.write(f"{i:4d}. {id_val} (вхождений: {count})\n")

    print(f"Результаты сохранены в {filename}")