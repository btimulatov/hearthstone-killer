import os
import re

def find_lines_with_id(file_path, target_id="5250", encoding='utf-8'):
    """
    Находит все строки в файле, содержащие указанный ID.
    
    Args:
        file_path (str): Путь к лог-файлу
        target_id (str): ID для поиска (по умолчанию "5250")
        encoding (str): Кодировка файла
    
    Returns:
        list: Список строк, содержащих искомый ID
    """
    matching_lines = []
    line_numbers = []
    
    # Создаем паттерн для поиска разных форматов записи ID
    # Ищет id=5250, id:5250, "id":"5250", ID=5250 и т.д.
    patterns = [
        f'[Ii][Dd][=:]{target_id}\\b',                    # id=5250 или id:5250
        f'"[Ii][Dd]"[=:]{target_id}\\b',                  # "id"=5250
        f'[Ii][Dd]"[=:]{target_id}\\b',                    # id"=5250
        f'[Ii][Dd]\\s*[=:]\\s*"{target_id}"',              # id = "5250"
        f'[Ee]ntity[_-]?[Ii][Dd][=:]{target_id}\\b'       # EntityID=5250
    ]
    
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            for line_num, line in enumerate(file, 1):
                # Проверяем каждый паттерн
                for pattern in patterns:
                    if re.search(pattern, line):
                        matching_lines.append(line.rstrip('\n'))  # Убираем символ переноса
                        line_numbers.append(line_num)
                        break  # Прекращаем проверку паттернов для этой строки
                        
    except FileNotFoundError:
        print(f"Ошибка: Файл '{file_path}' не найден.")
        return [], []
    except UnicodeDecodeError:
        print(f"Ошибка кодировки. Попробуйте другую кодировку.")
        return [], []
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return [], []
    
    return matching_lines, line_numbers

def print_matching_lines(lines, line_numbers, show_numbers=True):
    """
    Выводит найденные строки.
    
    Args:
        lines (list): Список строк
        line_numbers (list): Список номеров строк
        show_numbers (bool): Показывать номера строк
    """
    if not lines:
        print("Строки с указанным ID не найдены.")
        return
    
    print(f"\n{'='*60}")
    print(f"НАЙДЕНО СТРОК: {len(lines)}")
    print(f"{'='*60}")
    
    for i, (line, num) in enumerate(zip(lines, line_numbers), 1):
        print(f"\n--- Строка {i} (строка в файле: {num}) ---")
        if show_numbers:
            # Показываем строку с подсветкой найденного ID
            highlighted = re.sub(r'(id[=:]5250|ID[=:]5250|"id"[=:]5250)', 
                               '\033[93m\\1\033[0m', line, flags=re.IGNORECASE)
            print(highlighted)
        else:
            print(line)

def save_matching_lines(lines, line_numbers, output_file):
    """Сохраняет найденные строки в файл."""
    if not lines:
        return
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Найдено строк с ID=5250: {len(lines)}\n")
        f.write("#" + "="*50 + "\n\n")
        
        for i, (line, num) in enumerate(zip(lines, line_numbers), 1):
            f.write(f"[{i}] Строка {num}:\n")
            f.write(f"{line}\n")
            f.write("-"*40 + "\n")
    
    print(f"\nРезультаты сохранены в файл: {output_file}")

def simple_search():
    """Простой интерактивный поиск."""
    print("ПОИСК СТРОК С ID=5250")
    print("-"*30)
    
    # Запрашиваем имя файла
    filename = input("Введите путь к лог-файлу: ").strip()
    
    if not os.path.exists(filename):
        print(f"Ошибка: Файл '{filename}' не найден.")
        return
    
    # Запрашиваем кодировку
    encoding = input("Введите кодировку (Enter для utf-8): ").strip()
    if not encoding:
        encoding = 'utf-8'
    
    # Можно изменить ID, если нужно искать другое значение
    custom_id = input("Введите ID для поиска (Enter для 5250): ").strip()
    if not custom_id:
        custom_id = "5250"
    
    print(f"\nПоиск строк с ID={custom_id} в файле {filename}...")
    
    lines, numbers = find_lines_with_id(filename, custom_id, encoding)
    
    if lines:
        print_matching_lines(lines, numbers)
        
        # Спрашиваем о сохранении
        save_choice = input("\nСохранить результаты в файл? (y/n): ").lower()
        if save_choice == 'y':
            output = input("Имя выходного файла (по умолчанию found_lines.txt): ").strip()
            if not output:
                output = "found_lines.txt"
            save_matching_lines(lines, numbers, output)
            
        # Показываем контекст вокруг найденных строк
        show_context = input("\nПоказать контекст (строки до/после)? (y/n): ").lower()
        if show_context == 'y':
            show_lines_with_context(filename, numbers, custom_id, encoding)
    else:
        print(f"Строки с ID={custom_id} не найдены.")

def show_lines_with_context(file_path, line_numbers, target_id, encoding='utf-8', context=2):
    """
    Показывает строки с контекстом (несколько строк до и после найденной).
    
    Args:
        file_path (str): Путь к файлу
        line_numbers (list): Список номеров найденных строк
        target_id (str): Искомый ID
        encoding (str): Кодировка
        context (int): Количество строк до и после для контекста
    """
    if not line_numbers:
        return
    
    try:
        with open(file_path, 'r', encoding=encoding) as file:
            all_lines = file.readlines()
        
        print(f"\n{'='*60}")
        print("СТРОКИ С КОНТЕКСТОМ")
        print(f"{'='*60}")
        
        # Создаем множество номеров строк для контекста
        context_lines = set()
        for num in line_numbers:
            for i in range(max(1, num - context), min(len(all_lines), num + context) + 1):
                context_lines.add(i)
        
        # Сортируем номера строк
        context_lines = sorted(context_lines)
        
        prev_num = None
        for num in context_lines:
            # Добавляем разделитель, если есть пропуск
            if prev_num and num > prev_num + 1:
                print("\n" + "."*40 + "\n")
            
            # Отмечаем найденные строки
            marker = ">>>" if num in line_numbers else "   "
            line = all_lines[num-1].rstrip('\n')
            
            # Подсвечиваем ID в найденных строках
            if num in line_numbers:
                line = re.sub(f'({target_id})', '\033[91m\\1\033[0m', line, flags=re.IGNORECASE)
                print(f"{marker} {num:4d}: {line}  \033[91m<--- НАЙДЕНО\033[0m")
            else:
                print(f"{marker} {num:4d}: {line}")
            
            prev_num = num
            
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")

# Быстрая функция для поиска конкретного ID
def find_id_5250(file_path, encoding='utf-8'):
    """
    Быстрый поиск строк с id=5250.
    
    Args:
        file_path (str): Путь к файлу
        encoding (str): Кодировка
    """
    lines, numbers = find_lines_with_id(file_path, "5250", encoding)
    
    if lines:
        print(f"\nНайдено {len(lines)} строк с ID=5250:")
        print("-"*40)
        for i, (line, num) in enumerate(zip(lines, numbers), 1):
            print(f"{i:2d}. [строка {num}] {line[:100]}{'...' if len(line) > 100 else ''}")
    else:
        print("Строки с ID=5250 не найдены.")
    
    return lines, numbers

if __name__ == "__main__":
    # Простой способ - указать файл прямо здесь
    # lines, numbers = find_id_5250("logfile.log")
    
    # Или использовать интерактивный режим
    simple_search()
    
    # Или для конкретного файла:
    # result = find_lines_with_id("application.log", "5250")
    # if result[0]:
    #     for line in result[0]:
    #         print(line)
