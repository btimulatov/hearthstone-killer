#!/usr/bin/env python3
"""
ID Parser - инструмент для сбора всех уникальных ID из лог-файлов.
"""

import sys
from src.ui.id_parser_ui import run_id_parser
from src.core.id_parser import IDParser
from src.config.settings import DEFAULT_ENCODING


def main():
    """Основная функция приложения."""
    print("=" * 60)
    print("ID PARSER v1.0")
    print("Сбор всех уникальных ID из лог-файлов")
    print("=" * 60)

    if len(sys.argv) > 1:
        # Режим командной строки
        file_path = sys.argv[1]
        encoding = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_ENCODING

        try:
            parser = IDParser(file_path, encoding)
            all_ids = parser.get_all_ids()

            print(f"\nФайл: {file_path}")
            print(f"Найдено уникальных ID: {len(all_ids)}")

            if all_ids:
                print("\nПервые 20 ID:")
                for i, id_val in enumerate(sorted(all_ids, key=int)[:20], 1):
                    print(f"{i:4d}. {id_val}")

                # Спрашиваем, сохранить ли полный список
                if input("\nСохранить полный список в файл? (y/n): ").lower() == 'y':
                    from src.utils.id_saver import save_ids_to_file
                    save_ids_to_file(parser, "all_ids.txt")
            else:
                print("ID не найдены.")

        except Exception as e:
            print(f"Ошибка: {e}")
    else:
        # Интерактивный режим
        run_id_parser()


if __name__ == "__main__":
    main()