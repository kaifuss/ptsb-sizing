#GLOBALS
#Цветовые коды
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RESET = '\033[0m'  #сброс на дефолт


#напечатать красивый заголовок
def print_header(text: str, header_level: int = 2, newline_indent: int = 1):
    header_length = 80
    if header_level == 1:
        header_symbol = '═'
    elif header_level == 2:
        header_symbol = '─'
    elif header_level == 3:
        header_symbol = '~'
    
    newline = '\n'
    print(f"{newline_indent * newline}{text.center(header_length, header_symbol)}")

#согласие на ввод
def input_yes_no(question):
    #print(question)
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

#ввод целого числа при выборе
def input_choise_digit(question, max_option):
    print(question)
    while True:
        try:
            input_digit = int(input('Введите цифру, соответствующую необходимому варианту: '))
            if input_digit in range(1, max_option + 1):
                return input_digit
            else:
                print(f"{RED}Некорректный ввод.{RESET} Введите число от 1 до {max_option}: ")
        except ValueError:
            print(f"{RED}Некорректный ввод.{RESET} Ожидалось целое число от 1 до {max_option}: ")
        except KeyboardInterrupt:
            print('\n \nПринудительный выход из скрипта.\n')
            exit()

#ввод проверка ввода любого целого числа
def input_integer_number(question):
    while True:
        try:
            input_number = input(question)
            if input_number == '':
                return None
            return int(input_number)
        except ValueError:
            print(f"{RED}Некорректный ввод.{RESET} Ожидалось целое число.\n")
        except KeyboardInterrupt:
            print('\n \nПринудительный выход из скрипта.\n')
            exit()

#проверка нечетности для отказоустойчивого кластера
def input_odd_number(question):
    while True:
        input_amount = input_integer_number(question)
        if (input_amount % 2 == 0) or (input_amount < 3):
            print(f"{RED}Ошибка ввода.{RESET} Число должно быть нечетным и больше 1.")
        else:
            return input_amount