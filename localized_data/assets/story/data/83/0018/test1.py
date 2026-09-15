import json
import os
import sys

def split_text(text, max_len=42):
    """Разбивает текст на строки до max_len символов, вставляя   в пробелы."""
    if len(text) <= max_len:
        return text
    
    words = text.split()
    result_lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        # Проверяем длину текущей строки с добавлением нового слова
        # Учитываем пробел между словами, если это не первое слово в строке
        word_len = len(word)
        if current_line:
            # Если есть слова в текущей строке, добавляем пробел
            potential_length = current_length + 1 + word_len
        else:
            potential_length = word_len
        
        if potential_length <= max_len:
            # Добавляем слово к текущей строке
            if current_line:
                current_line.append(' ' + word)
                current_length += 1 + word_len
            else:
                current_line.append(word)
                current_length = word_len
        else:
            # Сохраняем текущую строку и начинаем новую
            if current_line:
                result_lines.append(''.join(current_line))
                current_line = [word]
                current_length = word_len
            else:
                # Если слово само по себе длиннее max_len (редкий случай)
                result_lines.append(word)
                current_line = []
                current_length = 0
    
    # Добавляем последнюю строку, если она есть
    if current_line:
        result_lines.append(''.join(current_line))
    
    # Соединяем строки через  
    return ' '.join(result_lines)

def process_json_file(input_file, output_file):
    """Обрабатывает JSON файл и сохраняет результат."""
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Обрабатываем каждый текстовый блок
    for block in data.get('text_block_list', []):
        # Обрабатываем основной текст
        if 'text' in block:
            block['text'] = split_text(block['text'])
        
        # Обрабатываем варианты выбора, если они есть
        if 'choice_data_list' in block:
            processed_choices = []
            for choice in block['choice_data_list']:
                processed_choices.append(split_text(choice))
            block['choice_data_list'] = processed_choices
    
    # Сохраняем результат
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"\n✅ Обработка завершена. Результат сохранен в {output_file}")

def find_json_files():
    """Находит все JSON файлы в текущей папке."""
    json_files = []
    for file in os.listdir('.'):
        if file.endswith('.json'):
            json_files.append(file)
    return json_files

def main():
    print("=" * 50)
    print("Обработчик текста для разделения на строки до 42 символов")
    print("=" * 50)
    
    # Ищем JSON файлы в текущей папке
    json_files = find_json_files()
    
    if not json_files:
        print("\n❌ В текущей папке не найдено JSON файлов!")
        print(f"Текущая папка: {os.getcwd()}")
        input("\nНажмите Enter для выхода...")
        return
    
    print(f"\nНайдено JSON файлов в папке: {len(json_files)}")
    print("-" * 50)
    
    # Показываем список файлов
    for i, file in enumerate(json_files, 1):
        file_size = os.path.getsize(file)
        print(f"{i:2}. {file} ({file_size} байт)")
    
    print("-" * 50)
    
    # Запрашиваем выбор файла
    while True:
        try:
            choice = input("\nВведите номер файла или имя файла (с расширением .json): ").strip()
            
            if not choice:
                print("❌ Введите номер или имя файла!")
                continue
            
            # Проверяем, ввели ли номер
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(json_files):
                    input_file = json_files[choice_num - 1]
                    break
                else:
                    print(f"❌ Номер должен быть от 1 до {len(json_files)}!")
                    continue
            
            # Проверяем, ввели ли имя файла
            if choice.endswith('.json'):
                if choice in json_files:
                    input_file = choice
                    break
                else:
                    print(f"❌ Файл '{choice}' не найден в папке!")
                    # Предлагаем показать список еще раз
                    show_list = input("Показать список файлов еще раз? (y/n): ").lower()
                    if show_list == 'y':
                        print("\nСписок файлов:")
                        for i, file in enumerate(json_files, 1):
                            print(f"{i:2}. {file}")
                    continue
            else:
                # Пробуем добавить .json
                if choice + '.json' in json_files:
                    input_file = choice + '.json'
                    break
                else:
                    print(f"❌ Файл '{choice}.json' не найден в папке!")
                    continue
                
        except KeyboardInterrupt:
            print("\n\nПрервано пользователем.")
            return
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            continue
    
    # Предлагаем имя для выходного файла
    print(f"\nВыбран файл: {input_file}")
    
    # Создаем имя для выходного файла по умолчанию
    base_name = os.path.splitext(input_file)[0]
    default_output = f"{base_name}_processed.json"
    
    output_file = input(f"Введите имя выходного файла [по умолчанию: {default_output}]: ").strip()
    
    if not output_file:
        output_file = default_output
    
    # Проверяем, не перезаписываем ли мы исходный файл
    if output_file == input_file:
        overwrite = input(f"⚠️  Выходной файл совпадает с входным! Перезаписать? (y/n): ").lower()
        if overwrite != 'y':
            print("❌ Отменено пользователем.")
            return
    
    # Проверяем, существует ли уже выходной файл
    if os.path.exists(output_file) and output_file != input_file:
        overwrite = input(f"⚠️  Файл '{output_file}' уже существует! Перезаписать? (y/n): ").lower()
        if overwrite != 'y':
            print("❌ Отменено пользователем.")
            return
    
    # Обрабатываем файл
    try:
        process_json_file(input_file, output_file)
    except FileNotFoundError:
        print(f"❌ Ошибка: Файл '{input_file}' не найден!")
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка при чтении JSON: {e}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
    
    input("\nНажмите Enter для выхода...")

# Пример использования
if __name__ == "__main__":
    main()
