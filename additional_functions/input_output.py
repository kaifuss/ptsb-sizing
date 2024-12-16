# встроенные библиотеки
import csv

#GLOBALS
#Цветовые коды
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RESET = '\033[0m'  #сброс на дефолт


# напечатать красивый заголовок
def print_header(text: str, header_level: int = 2, newline_indent: int = 1) -> None:
    """
    Выводит на экран красивое оформление заголовка
    
    Параметры:
        text (str): Текст заголовка, который будет красиво оформлен.
        header_level (int): Уровень заголовка (1: '=', 2: '-', или 3: '~').
        newline_indent (int): Количество отступов выводимого текста от предыдущего текста.

    Возвращает:
        Ничего.
    """

    header_length = 80
    if header_level == 1:
        header_symbol = '═'
    elif header_level == 2:
        header_symbol = '─'
    elif header_level == 3:
        header_symbol = '~'
    
    newline = '\n'
    print(f"{newline_indent * newline}{text.center(header_length, header_symbol)}")


# согласие на ввод. возвращает True/False
def input_yes_no(question: str) -> bool:
    """
    Запрашивает у пользователя ответ 'да' или 'нет' и возвращает булево значение.
    
    Параметры:
        question (str): Вопрос, отображаемый пользователю.

    Возвращает:
        bool: True, если пользователь ввел 'да', False, если 'нет'.
    """

    while True:
        try:
            input_answer = input(f'{question} [Yes, Y, Да, Д| / [No, N, Нет, Н]: ').strip().lower()
            if input_answer in ['yes', 'y', 'да', 'д']:
                return True
            elif input_answer in ['no', 'n', 'нет', 'н', '']:
                return False
            else:
                print(f"{RED}Некорректный ввод.{RESET} Повторите попытку.\n")
        except KeyboardInterrupt:
            print('\n \nПринудительный выход из скрипта.\n')
            exit()


# ввод целого числа при выборе. возвращает целое число от 1 до N
def input_choise_digit(question: str, max_option: int) -> int:
    """
    Запрашивает у пользователя на ввод целое число. Сравнивает полученное число с допустимыми значениями (от 1 до max_option).
    
    Параметры:
        question (str): Вопрос, отображаемый пользователю.
        max_option (int): Максимальное допустимое значение вводимого числа.

    Возвращает:
        int: Введенное пользователем целое число, удовлетворяющее условию.
    """    
    
    print(question)
    while True:
        try:
            input_digit = int(input('Введите цифру, соответствующую необходимому варианту: '))
            if input_digit in range(1, max_option + 1):
                return input_digit
            else:
                print(f"{RED}Некорректный ввод.{RESET} Введите число от 1 до {max_option}.\n")
        except ValueError:
            print(f"{RED}Некорректный ввод.{RESET} Ожидалось целое число от 1 до {max_option}.\n")
        except KeyboardInterrupt:
            print('\n \nПринудительный выход из скрипта.\n')
            exit()


# ввод проверка ввода любого целого числа. возвращает целое число
def input_integer_number(question: str) -> int:
    """
    Запрашивает у пользователя на ввод любое целое число.
    
    Параметры:
        question (str): Вопрос, отображаемый пользователю.

    Возвращает:
        int: Введенное пользователем целое число.
    """
    
    while True:
        try:
            input_number = input(question)
            return int(input_number)
        except ValueError:
            print(f"{RED}Некорректный ввод.{RESET} Ожидалось целое число.\n")
        except KeyboardInterrupt:
            print('\n \nПринудительный выход из скрипта.\n')
            exit()


# ввод проверка ввода любого целого числа. возвращает целое число, либо число по умолчанию
def input_integer_with_default(question: str, default_value: int) -> int:
    """
    Запрашивает у пользователя на ввод любое целое число. Если пользователь ничего не вводит, возвращает число по умолчанию.
    
    Параметры:
        question (str): Вопрос, отображаемый пользователю.
        default_value (int): Значение по умолчанию.

    Возвращает:
        int: Введенное пользователем целое число, если пользователь ввел число. Или default_value, если пользователь ничего не ввел.
    """    
    
    while True:
        try:
            input_number = input(question)
            if input_number == '':
                return default_value
            return int(input_number)
        except ValueError:
            print(f"{RED}Некорректный ввод.{RESET} Ожидалось целое число, либо пустой ввод для использования значения {default_value} по умолчанию.\n")
        except KeyboardInterrupt:
            print('\n \nПринудительный выход из скрипта.\n')
            exit()


# ввод проверка любого числа с плавающей точкой. возвращает число с плавающей точкой, либо число по умолчанию
def input_float_number_with_default(question: str, default_value: float) -> float:
    """
    Запрашивает у пользователя на ввод любое число. Если пользователь ничего не вводит, возвращает число по умолчанию.

    Параметры:
        question (str): Вопрос, отображаемый пользователю.
        default_value (float): Значение по умолчанию.

    Возвращает:
        float: Введенное пользователем число, либо default_value, если пользователь ничего не ввел.
    """

    while True:
        try:
            input_number = input(question)
            if input_number == '':
                return default_value
            return float(input_number)
        except ValueError:
            print(f"{RED}Некорректный ввод.{RESET} Ожидалось число, либо пустой ввод для использования значения {default_value} по умолчанию.\n")
        except KeyboardInterrupt:
            print('\n \nПринудительный выход из скрипта.\n')
            exit()

# ввод проверка нечетности для отказоустойчивого кластера. возвращает нечетное число >= 3
def input_odd_number(question: str) -> int:
    """
    Запрашивает у пользователя на ввод целое нечетное число >=3 (для количества серверов отказоустойчивого кластера).
    
    Параметры:
        question (str): Вопрос, отображаемый пользователю.

    Возвращает:
        int: Введенное пользователем целое положительное нечетное число, удовлетворяющее условию >=3.
    """    

    while True:
        input_amount = input_integer_number(question)
        if (input_amount % 2 == 0) or (input_amount < 3):
            print(f"{RED}Ошибка ввода.{RESET} Число должно быть нечетным и больше 1.")
        else:
            return input_amount
        

# вывод данных в txt файл
def output_data_to_txt(
        data_to_write: str,
        write_mode: str,
        file_name: str,
        encoding: str) -> None:
    """
    Функция для первой записи в txt файл, или добавления данных в существующий файл.
    
    Параметры:
        data_to_write (str): Любые str данные для записи в txt файл.
        write_mode (str): Режим записи ('w' - первая запись или перезапись, 'a' - добавление данных).
        file_name (str): Полный путь txt файла для записи.
        encoding (str): Кодировка, в которой необходимо записать данные в файл.
    """

    with open(file_name, write_mode, encoding=encoding) as txt_file:
        txt_file.write(data_to_write)


# вывод данных в csv файл
def output_data_to_csv(
        data_to_write: list,
        write_mode: str,
        file_name: str,
        encoding: str, 
        delimiter: str) -> None:
    """
    Функция для первой записи в csv файл, или добавления данных в существующий файл.
    
    Параметры:
        data_to_write (list): Список с данными для записи в csv файл.
        write_mode (str): Режим записи ('w' - первая запись или перезапись, 'a' - добавление данных).
        file_name (str): Полный путь csv файла для записи.
        encoding (str): Кодировка, в которой необходимо записать данные в файл.
        delimiter (str): Разделитель данных между ячейками в файле.
    """

    with open(file_name, write_mode, newline='', encoding=encoding) as csv_file:
        writer = csv.writer(csv_file, delimiter=delimiter)
        writer.writerows(data_to_write)