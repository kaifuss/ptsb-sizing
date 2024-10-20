# -*- coding: utf-8 -*-
print('''
╔═══════════════════════════════════════════════════════════════════════════╗
║                                  WELCOME                                  ║
║                              PTSB sizing tool                             ║
║                          by @github.com/kaifuss/                          ║
╚═══════════════════════════════════════════════════════════════════════════╝
''')

#DEPENDENCIES
import csv
import math
from tabulate import tabulate

#GLOBALS
#Цветовые коды
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RESET = '\033[0m'  #сброс на дефолт

#Константы параметров вывода
TXT_OUTPUT_ENCODING = 'utf-8'
CSV_OUTPUT_ENCODING = 'windows-1251'
CSV_OUTPUT_DELIMITER = ';'
CSV_OUTPUT_NEWLINE = ''

#FUNCS
#красивый заголовок
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
            #print('\n')
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


#получить % отсечки для ПА для любого источника
def get_dynamic_cutoff(default_value):
    dynamic_cutoff = input_integer_number(f"Введите примерный % заданий от общего количества, которые пойдут на динамический анализ (по умолчанию - {default_value}%): ")
    dynamic_cutoff = float(dynamic_cutoff) / 100 if dynamic_cutoff is not None else default_value / 100
    return dynamic_cutoff

#получить % отсечки по префильтру для любого источника
def get_prefilter_cutoff(default_value):
    prefilter_cutoff = input_integer_number(f"Введите примерный % заданий от заданий ПА, которые останутся после префильтрации (по умолчанию - {default_value}%): ")
    prefilter_cutoff = float(prefilter_cutoff) / 100 if prefilter_cutoff is not None else default_value / 100
    return prefilter_cutoff

#получить % отсечки по кэшированию для любого источника
def get_cache_cutoff(default_value):
    cache_cutoff = input_integer_number(f"Введите примерный % заданий от заданий ПА, которые останутся после отброса кэшированием (по умолчанию - {default_value }%): ")
    cache_cutoff = float(cache_cutoff) / 100 if cache_cutoff is not None else default_value / 100
    return cache_cutoff

#получить время сканирования для любого источника
def get_time_to_scan(default_value):
    input_scan_time = input_integer_number(f"Введите время в секундах, как долго будут сканироваться задания с этого источника (по умолчанию - {default_value}): ")
    input_scan_time = input_scan_time if input_scan_time is not None else default_value
    return input_scan_time

#расчет нагрузки с почтового трафика
def get_smtp_load(smtp_load_parameters):
    
    #Если количество писем в час - неизвестно, то расчет идет от количества пользователей.
    if smtp_load_parameters['mails'] == 0:
        # количество писем в час - неизвестно
        input_users_multiplier = input_integer_number(
            f"Ввведите количество писем на 1 пользователя (по умолчанию - {smtp_load_parameters['users_multiplier']}): "
        )
        smtp_load_parameters['users_multiplier'] = input_users_multiplier or smtp_load_parameters['users_multiplier']
        smtp_load_parameters['mails'] = smtp_load_parameters['users'] * smtp_load_parameters['users_multiplier']

        # процент писем с вложениями
        input_mails_with_attachments = input_integer_number(
            'Введите примерный % писем от общего количества, которые предположительно содержат вложения '
            f"(по умолчанию - {smtp_load_parameters['mails_with_attachments']}%): "
        )
        smtp_load_parameters['mails_with_attachments'] = math.ceil(
            smtp_load_parameters['mails'] *
            float(input_mails_with_attachments or smtp_load_parameters['mails_with_attachments']) / 100.0
        )
    else:
        # количество писем в час - известно
        if input_yes_no('Известно ли количетсво писем в час, содержащих вложения?'):
            # количество писем с вложениями - известно
            smtp_load_parameters['mails_with_attachments'] = input_integer_number(
                'Введите количество писем в час, которые содержат вложения: '
            )
        else:
            # количество писем с вложениями - неизвестно
            input_mails_with_attachments = input_integer_number(
                'Введите примерный % писем от общего количества, которые предположительно содержат вложения '
                f"(по умолчанию - {smtp_load_parameters['mails_with_attachments']}%): "
            )
            smtp_load_parameters['mails_with_attachments'] = math.ceil(
                smtp_load_parameters['mails'] *
                float(input_mails_with_attachments or smtp_load_parameters['mails_with_attachments']) / 100.0
            )

    input_attachments_per_mail = input_integer_number(
        'Введите количество вложений на 1 письмо, содержащее вложения '
        f"(по умолчанию - {smtp_load_parameters['attachments_per_mail']}): "
    )
    smtp_load_parameters['attachments_per_mail'] = input_attachments_per_mail or smtp_load_parameters['attachments_per_mail']
    
    smtp_load_parameters['dynamic_cutoff'] = get_dynamic_cutoff(smtp_load_parameters['dynamic_cutoff'])
    smtp_load_parameters['prefilter_cutoff'] = get_prefilter_cutoff(smtp_load_parameters['prefilter_cutoff'])
    smtp_load_parameters['cache_cutoff'] = get_cache_cutoff(smtp_load_parameters['cache_cutoff'])
    smtp_load_parameters['time_to_scan'] = get_time_to_scan(smtp_load_parameters['time_to_scan'])

    smtp_load_parameters['dynamic_load'] = ( math.ceil(
        smtp_load_parameters['mails_with_attachments'] *
        smtp_load_parameters['attachments_per_mail'] *
        smtp_load_parameters['dynamic_cutoff'] *
        smtp_load_parameters['prefilter_cutoff'] *
        smtp_load_parameters['cache_cutoff'])
    )
    smtp_load_parameters['vms_needed'] = math.ceil(smtp_load_parameters['dynamic_load'] * smtp_load_parameters['time_to_scan'] / 3600)
    
    return smtp_load_parameters

#расчет нагрузки с ICAP
def get_icap_load(icap_load_parameters):

    icap_load_parameters['dynamic_cutoff'] = get_dynamic_cutoff(icap_load_parameters['dynamic_cutoff'])
    icap_load_parameters['prefilter_cutoff'] = get_prefilter_cutoff(icap_load_parameters['prefilter_cutoff'])
    icap_load_parameters['cache_cutoff'] = get_cache_cutoff(icap_load_parameters['cache_cutoff'])
    icap_load_parameters['time_to_scan'] = get_time_to_scan(icap_load_parameters['time_to_scan'])

    if icap_load_parameters['files'] == 0:
        icap_load_parameters['files'] = math.ceil( (7000 * icap_load_parameters['speed']) / 1024 )
    
    icap_load_parameters['dynamic_load'] = ( math.ceil(
        icap_load_parameters['files'] *
        icap_load_parameters['dynamic_cutoff'] *
        icap_load_parameters['prefilter_cutoff'] *
        icap_load_parameters['cache_cutoff'])
    )
    icap_load_parameters['vms_needed'] = math.ceil(icap_load_parameters['dynamic_load'] * icap_load_parameters['time_to_scan'] / 3600)    
    
    return icap_load_parameters

#расчет нагрузки с MP 10 EDR
def get_edr_load(edr_load_parameters):
    
    if edr_load_parameters['files'] == 0:
        agents_multiplier = input_integer_number(f"Введите примерное количество файлов с 1 агента edr (по умолчанию - {edr_load_parameters['agents_multiplier']}): ")
        edr_load_parameters['agents_multiplier'] = agents_multiplier or edr_load_parameters['agents_multiplier']
        edr_load_parameters['files'] = edr_load_parameters['agents'] * edr_load_parameters ['agents_multiplier']    

    edr_load_parameters['dynamic_cutoff'] = get_dynamic_cutoff(edr_load_parameters['dynamic_cutoff'])
    edr_load_parameters['prefilter_cutoff'] = get_prefilter_cutoff(edr_load_parameters['prefilter_cutoff'])
    edr_load_parameters['cache_cutoff'] = get_cache_cutoff(edr_load_parameters['cache_cutoff'])
    edr_load_parameters['time_to_scan'] = get_time_to_scan(edr_load_parameters['time_to_scan'])

    edr_load_parameters['dynamic_load'] = ( math.ceil(
        edr_load_parameters['files'] *
        edr_load_parameters['dynamic_cutoff'] *
        edr_load_parameters['prefilter_cutoff'] *
        edr_load_parameters['cache_cutoff'])
    )
    edr_load_parameters['vms_needed'] = math.ceil(edr_load_parameters['dynamic_load'] * edr_load_parameters['time_to_scan'] / 3600)  
    
    return edr_load_parameters

#расчет нагрузки с API-источника с выбранными параметрами проверки
def get_automated_api_load(automated_api_load_parameters):

    automated_api_load_parameters['dynamic_cutoff'] = get_dynamic_cutoff(automated_api_load_parameters['dynamic_cutoff'])
    automated_api_load_parameters['prefilter_cutoff'] = get_prefilter_cutoff(automated_api_load_parameters['prefilter_cutoff'])
    automated_api_load_parameters['cache_cutoff'] = get_cache_cutoff(automated_api_load_parameters['cache_cutoff'])
    automated_api_load_parameters['time_to_scan'] = get_time_to_scan(automated_api_load_parameters['time_to_scan'])

    automated_api_load_parameters['dynamic_load'] = ( math.ceil(
        automated_api_load_parameters['files'] *
        automated_api_load_parameters['dynamic_cutoff'] *
        automated_api_load_parameters['prefilter_cutoff'] *
        automated_api_load_parameters['cache_cutoff'])
    )
    automated_api_load_parameters['vms_needed'] = math.ceil(automated_api_load_parameters['dynamic_load'] * automated_api_load_parameters['time_to_scan'] / 3600) 

    return automated_api_load_parameters

#расчет нагрузки с API-источника с ручными параметрами проверки
def get_manual_api_load(manual_api_load_parameters):

    manual_api_load_parameters['dynamic_cutoff'] = get_dynamic_cutoff(manual_api_load_parameters['dynamic_cutoff'])
    manual_api_load_parameters['cache_cutoff'] = get_cache_cutoff(manual_api_load_parameters['cache_cutoff'])
    manual_api_load_parameters['time_to_scan'] = get_time_to_scan(manual_api_load_parameters['time_to_scan'])

    manual_api_load_parameters['dynamic_load'] = ( math.ceil(
        manual_api_load_parameters['files'] *
        manual_api_load_parameters['dynamic_cutoff'] *
        manual_api_load_parameters['cache_cutoff'])
    )
    manual_api_load_parameters['vms_needed'] = math.ceil(manual_api_load_parameters['dynamic_load'] * manual_api_load_parameters['time_to_scan'] / 3600) 
    
    return manual_api_load_parameters

#расчет нагрузки с хранилища файлов
def get_storage_load(storage_load_parameters):
    storage_load_parameters['prefilter_cutoff'] = get_prefilter_cutoff(storage_load_parameters['prefilter_cutoff'])
    storage_load_parameters['cache_cutoff'] = get_cache_cutoff(storage_load_parameters['cache_cutoff'])
    storage_load_parameters['time_to_scan'] = get_time_to_scan(storage_load_parameters['time_to_scan'])

    storage_load_parameters['dynamic_load'] = ( math.ceil(
        storage_load_parameters['dynamic_load'] *
        storage_load_parameters['prefilter_cutoff'] *
        storage_load_parameters['cache_cutoff'])
    )
    storage_load_parameters['vms_needed'] = math.ceil(storage_load_parameters['dynamic_load'] * storage_load_parameters['time_to_scan'] / 3600)

    return storage_load_parameters

#расчет ТХ сервера управления с вкл функцией ПА
def calculate_master_with_dynamic(vms_amount, iso_amount):
    server_parameters = {
        'server_role': f"Сервер управления с функцией ПА\nКоличество ВМ: {vms_amount}",
        'root_space': 118,
        'opt_space': 43,
        'minio_space': 50,
        'home_space': 100,
        'part_multiplier': 1.08,
        'theads_amount': 0,
        'ram_amount': 0,
        'ssd_size': 0,
        'hdd_size': 0,
    }
    # V_root = N_ВМ + 118
    server_parameters['root_space'] = math.ceil((vms_amount + server_parameters['root_space']) * 1.074)
    
    # V_opt = N_ВМ + 15 * N_ISO + 43
    server_parameters['opt_space'] = math.ceil((vms_amount + 15 * iso_amount + server_parameters['opt_space']) * 1.074)

    # V_minio = 8 * N_ISO + 50
    server_parameters['minio_space'] = math.ceil((8 * iso_amount + server_parameters['minio_space']) * 1.074)
    
    # рекомендация по домножению на 8%
    for key in ['root_space', 'opt_space', 'minio_space', 'home_space']:
        server_parameters[key] = math.ceil(server_parameters[key] * server_parameters['part_multiplier'])

    server_parameters['ssd_size'] = (
        server_parameters['ssd_size'] +
        server_parameters['root_space'] +
        server_parameters['opt_space']
    )

    server_parameters['hdd_size'] = (
        server_parameters['hdd_size'] +
        server_parameters['minio_space'] +
        server_parameters['home_space']
    )

    # Threads = 3 * N_ВМ + 9
    server_parameters['theads_amount'] = 3 * vms_amount + 9

    # RAM = 4 * N_ВМ + 19
    server_parameters['ram_amount'] = math.ceil((4 * vms_amount + 19) * 1.074)
    
    return server_parameters

#расчет ТХ сервера управления без функции ПА  
def calculate_master_without_dynamic(iso_amount, static_tasks):
    server_parameters = {
        'server_role': 'Сервер управления без функции ПА',
        'root_space': 140,
        'opt_space': 87,
        'minio_space': 50,
        'home_space': 100,
        'part_multiplier': 1.08,
        'theads_amount': 0,
        'ram_amount': 0,
        'ssd_size': 0,
        'hdd_size': 0,
    }

    # V_minio = 8 * N_ISO + 50
    server_parameters['minio_space'] = math.ceil((8 * iso_amount + server_parameters['minio_space']) * 1.074)

    # рекомендация по домножению на 8%
    for key in ['root_space', 'opt_space', 'minio_space', 'home_space']:
        server_parameters[key] = math.ceil(server_parameters[key] * server_parameters['part_multiplier'])

    server_parameters['ssd_size'] = (
        server_parameters['root_space'] +
        server_parameters['opt_space']
    )
    
    server_parameters['hdd_size'] = (
        server_parameters['minio_space'] +
        server_parameters['home_space']
    )    
    
    if static_tasks <= 100:
        server_parameters['theads_amount'] = 4
        server_parameters['ram_amount'] = 16
    elif (static_tasks > 100 ) and (static_tasks <= 1000):
        server_parameters['theads_amount'] = 6
        server_parameters['ram_amount'] = 32
    elif (static_tasks > 1000) and (static_tasks <= 5000):
        server_parameters['theads_amount'] = 10
        server_parameters['ram_amount'] = 32
    elif (static_tasks > 5000):
        server_parameters['theads_amount'] = 15
        server_parameters['ram_amount'] = 32
    
    return server_parameters

#расчет ТХ дополнительного сервера с функцией ПА
def calculate_additional_server_with_vms(vms_amount, iso_amount):
    server_parameters = {
        'server_role': f"Дополнительный сервер с функцией ПА\nКоличество ВМ: {vms_amount}",
        'root_space': 118,
        'opt_space': 0,
        'minio_space': 0,
        'home_space': 100,
        'part_multiplier': 1.08,
        'theads_amount': 0,
        'ram_amount': 0,
        'ssd_size': 0,
        'hdd_size': 0,
    }
    # V_root = N_ВМ + 118
    server_parameters['root_space'] = math.ceil((vms_amount + server_parameters['root_space']) * 1.074)
    
    # V_opt = N_ВМ + 15 * N_ISO - 2
    server_parameters['opt_space'] = math.ceil((vms_amount + 15 * iso_amount - 2) * 1.074)
    
    # рекомендация по домножению на 8%
    for key in ['root_space', 'opt_space', 'minio_space', 'home_space']:
        server_parameters[key] = math.ceil(server_parameters[key] * server_parameters['part_multiplier'])

    server_parameters['ssd_size'] = (
        server_parameters['root_space'] +
        server_parameters['opt_space']
    )
    
    server_parameters['hdd_size'] = (
        server_parameters['minio_space'] +
        server_parameters['home_space']
    )
    
    # Threads = 3 * N_ВМ + 4
    server_parameters['theads_amount'] = 3 * vms_amount + 4

    # RAM = 4 * N_ВМ + 5
    server_parameters['ram_amount'] = math.ceil((vms_amount * 4 + 5) * 1.074)
    
    return server_parameters

#расчет всех доп серверов с динамикой
def get_all_additional_servers(vms_all, vms_per_server, iso_amount):
    dynamic_servers_list = []
    dynamic_servers_amount = math.ceil(vms_all / vms_per_server)
    print_header('Расчет ТХ для доп. серверов динамики')
    input_calculation_type = input_choise_digit(
        f"1. Расчет ТХ для {dynamic_servers_amount} доп серверов(-а) под общее количество ВМ {vms_all} (не более {vms_per_server} ВМ на сервер)\n"
        '2. Вручную ввести количество дополнительных серверов и количество ВМ для каждого сервера', 2
    )

    if input_calculation_type == 1:
        vms_left = vms_all
        while (vms_left > 0):
            if (vms_left > vms_per_server):
                dynamic_servers_list.append(calculate_additional_server_with_vms(vms_per_server, iso_amount))
            else:
                dynamic_servers_list.append(calculate_additional_server_with_vms(vms_left, iso_amount))
            vms_left -= vms_per_server
    elif input_calculation_type == 2:
        print_header('Ручная конфигурация доп. серверов динамики', 2)
        dynamic_servers_amount = input_integer_number('Введите количество дополнительных серверов: ')
        for i in range(dynamic_servers_amount):
            vms_amount = input_integer_number(f"Введите количество ВМ для {i+1}-го доп. сервера динамики: ")
            dynamic_servers_list.append(calculate_additional_server_with_vms(vms_amount, iso_amount))
    return dynamic_servers_list

#замена всех 0 на 'Не требуется'
def replace_zero_with_message(server, message="Не требуется"):
    return {key: (message if value == 0 else value) for key, value in server.items()}

#генерация таблицы для вывода данных по всем серверам
def generate_table(table_format, servers_list, fields, first_column_header, first_column_fields):
    transposed_data = {}
    transposed_data[first_column_header] = first_column_fields
    
    #cоздание уникальных идентификаторов для серверов
    server_ids = [f"Сервер {i+1}\n{server.get('server_role')}" for i, server in enumerate(servers_list)]
    
    #проход по всем серверам и добавление их данных в словарь с уникальными ключами
    for server_id, server in zip(server_ids, servers_list):
        transposed_data[server_id] = [server.get(parameter) for parameter in fields]
    
    #транспонирование данных
    transposed_table = list(zip(*transposed_data.values()))
    
    #задание формата таблицы в csv или fancy
    if table_format == 'fancy':
        fancy_table = tabulate(transposed_table, headers=transposed_data.keys(), tablefmt="fancy_grid")
        return fancy_table
    elif table_format == 'csv':
        #первая строка, заголовки
        csv_table = [list(transposed_data.keys())]
        csv_table.extend(transposed_table)
        return csv_table

#вывод данных по стенду в файл txt
def output_to_txt(tech_req_table, partition_table, filename):
    with open(filename, 'w', encoding=TXT_OUTPUT_ENCODING) as output_file:
        output_file.write('Таблица с техническими требованиями к серверам:\n')
        output_file.write(tech_req_table)
        output_file.write('\n\nТаблица с разметкой дискового пространства серверов:\n')
        output_file.write(partition_table)
    pass

#вывод данных по стенду в файл csv
def output_to_csv(tech_req_table, partition_table, filename):
    with open(filename, mode='w', newline=CSV_OUTPUT_NEWLINE, encoding=CSV_OUTPUT_ENCODING) as output_file:
        writer = csv.writer(output_file, delimiter=CSV_OUTPUT_DELIMITER)
        writer.writerow(['Таблица с техническими требованиями к серверам:'])
        writer.writerows(tech_req_table)
        writer.writerow([''])
        writer.writerow(['Таблица с разметкой дискового пространства серверов:'])
        writer.writerows(partition_table)

#INT MAIN
if __name__ == '__main__':
    
    servers_list = []   #лист для хранения всех объектов dict(), содержащих конфигурацию серверов
    sources_list = []   #лист для хранения всех объектов dict(), содержащих конфигурацию источников

    #имя output файлов с конфигурацией
    txt_file_name = 'config.txt'    
    csv_file_name = 'config.csv'

    #основные параметры конфигурации
    installation_parameters = {
        'vms_all': 15,
        'vms_for_master': 15,
        'vms_for_additional': 30,
        'iso_amount': 7,
        'time_to_scan': 150,
        'overall_static': 0,
        'overall_dynamic': 0,
    }

    #smtp источник
    smtp_load_parameters = {
        'mails': 0,
        'users': 0,
        'users_multiplier': 3,
        'mails_with_attachments': 10,
        'attachments_per_mail': 1,
        'dynamic_cutoff': 10,
        'prefilter_cutoff': 40,
        'cache_cutoff': 85,
        'time_to_scan': 150,
        'dynamic_load': 0,
        'vms_needed': 0,
    }

    #icap источник
    icap_load_parameters = {
        'speed': 0,
        'files': 0,
        'dynamic_cutoff': 5,
        'prefilter_cutoff': 40,
        'cache_cutoff': 85,
        'time_to_scan': 150,
        'dynamic_load': 0,
        'vms_needed': 0,
    }

    #MP 10 EDR источник
    edr_load_parameters = {
        'agents': 0,
        'files': 0,
        'agents_multiplier': 3,
        'dynamic_cutoff': 1,
        'prefilter_cutoff': 40,
        'cache_cutoff': 85,
        'time_to_scan': 150,
        'dynamic_load': 0,
        'vms_needed': 0,
    }

    #API с предустановленынми параметрами проверки
    automated_api_load_parameters = {
        'files': 0,
        'dynamic_cutoff': 50,
        'prefilter_cutoff': 40,
        'cache_cutoff': 95,
        'time_to_scan': 150,
        'dynamic_load': 0,
        'vms_needed': 0,
    }

    #API с пользовательскими параметрами проверки
    manual_api_load_parameters = {
        'files': 0,
        'dynamic_cutoff': 50,
        'cache_cutoff': 95,
        'time_to_scan': 150,
        'dynamic_load': 0,
        'vms_needed': 0,
    }

    #Файловое хранилище
    storage_load_parameters = {
        'files': 0,
        'prefilter_cutoff': 40,
        'cache_cutoff': 50,
        'time_to_scan': 150,
        'dynamic_load': 0,
        'vms_needed': 0,
    }

    #вопрос о выборе типа расчета инсталляции
    input_calculation_type = input_choise_digit(
        '\nДоступные варианты расчета технических характеристик под сервера PT SB:\n'
        '1. Расчет ТХ серверов (а также их количества) на основании известных или около известных показателей нагрузки с различных источников\n'
        '2. Расчет ТХ серверов (а также их количества) на основании вручную вводимых показателей нагрузки на статику и динамику в час\n'
        '3. Полностью ручной расчет ТХ серверов на основании вручную вводимого количества ВМ на сервер и количества серверов', 3
    )

    if input_calculation_type == 1:
        print_header('Расчет нагрузки с источников', header_level=1, newline_indent=2)

        #smtp источник
        print_header('Электронная почта организации')
        if input_yes_no('Будет ли использоваться проверка почты?'):
            if(input_yes_no('Известно ли количество писем в час?')):
                smtp_load_parameters['mails'] = input_integer_number('Ввведите количество писем в час: ')
            else:
                smtp_load_parameters['users'] = input_integer_number('Ввведите количество пользователей: ')
            smtp_load_parameters = get_smtp_load(smtp_load_parameters)

        #сетевой ICAP источник
        print_header('Сетевой трафик по ICAP', 2)
        if input_yes_no('Будет ли использоваться проверка по ICAP?'):
            if input_yes_no('Известно ли количество файлов в трафике в час?'):
                icap_load_parameters['files'] = input_integer_number('Введите количество файлов в час: ')
            else:
                icap_load_parameters['speed'] = input_integer_number('Введите скорость трафика в Мбит/с: ')
            icap_load_parameters = get_icap_load(icap_load_parameters)

        #агенты MP 10 EDR
        print_header('Файлы с агентов MP 10 EDR', 2)
        if input_yes_no('Будет ли использоваться проверка с агентов MP 10 EDR?'):
            if input_yes_no('Известно ли общее количество файлов со всех агентов в час?'):
                edr_load_parameters['files'] = input_integer_number('Введите количество файлов в час: ')
            else:
                edr_load_parameters['agents'] = input_integer_number('Введите количество агентов: ')
            edr_load_parameters = get_edr_load(edr_load_parameters)

        #API с предустановленными параметрами проверки
        print_header('Источник API c предустановленными параметрами', 2)
        if input_yes_no('Будет ли использоваться проверка по API с параметрами источника?'):
            automated_api_load_parameters['files'] = input_integer_number('Введите примерное количество файлов в час: ')
            automated_api_load_parameters = get_automated_api_load(automated_api_load_parameters)
        
        #API с пользовательскими параметрами проверки
        print_header('Источник API c пользовательскими параметрами', 2)
        if input_yes_no('Будет ли использоваться проверка по API с пользовательскими параметрами?'):
            manual_api_load_parameters['files'] = input_integer_number('Ввведите примерное количество файлов в час: ')
            manual_api_load_parameters = get_manual_api_load(manual_api_load_parameters)
        
        #Файловое хранилище
        print_header('Файловое хранилище', 2)
        if input_yes_no('Будет ли использоваться проверка файлового хранилища?'):
            storage_load_parameters['files'] = input_integer_number('Введите количество файлов в час, которые будут проверяться статикой: ')
            storage_load_parameters['dynamic_load'] = input_integer_number('Введите количество файлов, которые будут проверяться динамикой: ')
            storage_load_parameters = get_storage_load(storage_load_parameters)
            pass

        #расчет общей статической нагрузки
        installation_parameters['overall_static'] = (
            smtp_load_parameters['mails'] +
            icap_load_parameters['files'] +
            edr_load_parameters['files'] +
            automated_api_load_parameters['files'] +
            manual_api_load_parameters['files'] +
            storage_load_parameters['files']
        )

        #расчет общей динамической нагрузки
        installation_parameters['overall_dynamic'] = (
            smtp_load_parameters['dynamic_load'] +
            icap_load_parameters['dynamic_load'] +
            edr_load_parameters['dynamic_load'] +
            automated_api_load_parameters['dynamic_load'] +
            manual_api_load_parameters['dynamic_load'] +
            storage_load_parameters['dynamic_load']
        )

        #расчет общего необходимого количества виртуальных машин на всю инсталляцию
        installation_parameters['vms_all'] = (
            smtp_load_parameters['vms_needed'] +
            icap_load_parameters['vms_needed'] +
            edr_load_parameters['vms_needed'] +
            automated_api_load_parameters['vms_needed'] +
            manual_api_load_parameters['vms_needed'] +
            storage_load_parameters['vms_needed']
        )
        
        print_header('Вычисленные показатели', header_level=1, newline_indent=2)
        print(
            f"Количество статических заданий: {installation_parameters['overall_static']}"
            f"\nКоличество динамических заданий после всех отсечек: {installation_parameters['overall_dynamic']}"
            f"\nРекомендуемое количество виртуальных машин на всю инсталляцию: {installation_parameters['vms_all']}"
        )

        if installation_parameters['vms_all'] > installation_parameters['vms_for_master']:
            print(f"Использование инсталляции AiO: {RED}Не рекомендуется{RESET}")
        else:
            print(f"Использование инсталляции AiO: {GREEN}Возможно{RESET}")

    elif input_calculation_type == 2:
        print_header('Ручной ввод показателей', header_level=1, newline_indent=2)
        print_header('Показатели нагрузки')
        installation_parameters['overall_static'] = input_integer_number('Ввведите примерное количество статических заданий в час: ')
        installation_parameters['overall_dynamic'] = input_integer_number('Ввведите примерное количество динамических заданий в час после всех отсечек: ')

        print_header('Количество ВМ на стенде', 2)
        input_vm_calculation_type = input_choise_digit(
            'Доступные варианты выбора количества виртуальных машин на инсталляцию:\n'
            '1. Ввести общее количество ВМ на всю инсталляцию вручную\n'
            '2. Рассчитать на основании нагрузки на динамику и времени сканирования на 1 файл', 2
        )
        
        if input_vm_calculation_type == 1:
            installation_parameters['vms_all'] = input_integer_number('Ввведите общее количество ВМ на всю инсталляцию: ')
        elif input_vm_calculation_type == 2:
            installation_parameters['time_to_scan'] = input_integer_number('Введите время сканирования 1 файла в секундах: ')
            installation_parameters['vms_all'] = math.ceil(installation_parameters['overall_dynamic'] * installation_parameters['time_to_scan'] / 3600)
            print('\nРасчитанное количество ВМ на стенде: ', installation_parameters['vms_all'])
        
        if installation_parameters['vms_all'] > installation_parameters['vms_for_master']:
            print(f"Использование инсталляции AiO: {RED}Не рекомендуется{RESET}")
        else:
            print(f"Использование инсталляции AiO: {GREEN}Возможно{RESET}")

    elif input_calculation_type == 3:
        print_header('Ручной ввод показателей', header_level=1, newline_indent=2)
        print_header('Показатели нагрузки')
        if installation_parameters['overall_static'] == 0:
            input_overall_static = input_integer_number('Для расчета ТХ серверов управления требуется указать примерное количество статических заданий в час: ')
            installation_parameters['overall_static'] = input_overall_static   
        pass
    
    print_header('Расчет конфигурации серверов', header_level=1, newline_indent=2)

    #вопрос про iso для расчета необходимого места
    print_header('Расчет места под образы', 2)
    input_iso_amount = input_integer_number(
        "Введите количество базовых образов, которые будут установлены на стенде."
        f"\nВажно: образ это не то же самое, что виртуальная машина. (По умолчанию - {installation_parameters['iso_amount']}): "
    )

    if input_iso_amount is not None:
        installation_parameters['iso_amount'] = input_iso_amount

    #вопрос о выборе конфигурации
    print_header('Выбор конфигурации инсталляции', 2)
    inpit_installation_type = input_choise_digit(
        '1. All in one на одном сервере;\n'
        '2. Высоконагруженная конфигурация. При этом, на сервере управления также поддерживаются динамические исследования;\n'
        '3. Высоконагруженная конфигурация. При этом, на сервере управления не устанавливаются компоненты Xen и не используются динамические исследования;\n'
        '4. Отказоустойчивый кластер.', 4
    )
    
    #расчет конфигурации AiO инсталляции
    if inpit_installation_type == 1:
        #проверка, что количество вм выходит за ограничения вендора
        if (installation_parameters['vms_all'] <= installation_parameters['vms_for_master']):
            input_vms_all = input_integer_number(
                "\nВведите количество ВМ для сервера AiO"
                f"(по умолчанию будет использоваться рекомендованное значение - {installation_parameters['vms_all']}): "
            )

            installation_parameters['vms_all'] = input_vms_all or installation_parameters['vms_all']

        else:
            input_vms_all = input_integer_number(
                f"\n{RED}Внимание!{RESET} Для AiO инсталляции поддерживается не более {installation_parameters['vms_for_master']} ВМ на сервер. "
                f"Рассчитанное рекомендованное ранее значние: {RED}{installation_parameters['vms_all']}{RESET}.\n"
                "Введите количество ВМ, на которое рассчитывается AiO инсталляция"
                f" (по умолчанию будет использоваться максимальное возможное значение - {installation_parameters['vms_for_master']}): "
            )

            installation_parameters['vms_all'] = input_vms_all or installation_parameters['vms_for_master']
        
        servers_list.append(calculate_master_with_dynamic(installation_parameters['vms_all'], installation_parameters['iso_amount']))
    
    #расчет конфигурации высоконагруженной инсталляции, узел управления с ПА    
    elif inpit_installation_type == 2:
        
        # если пользователь выбрал этот вариант, но этот вариант нелогичен
        if installation_parameters['vms_all'] <= installation_parameters['vms_for_additional']:
            vms_on_master = installation_parameters['vms_for_master']
        else:
            #нужно серверов динамики
            dynamic_servers_needed = math.ceil((installation_parameters['vms_all'] - installation_parameters['vms_for_master']) / installation_parameters['vms_for_additional'])
        
            #тогда на сервере управления будет количество ВМ:
            vms_on_master = installation_parameters['vms_all'] - dynamic_servers_needed * installation_parameters['vms_for_additional'] 
        
        #расчет ТХ сервера управления с функцией ПА
        print_header('Расчет ТХ для сервера управления', 2)
        input_masters_installation_type = input_choise_digit(
            f"1. Расчет ТХ под сервер управления с {installation_parameters['vms_for_master']} ВМ (максимально возможным числом);\n"
            f"2. Расчет ТХ под сервер управления с {vms_on_master} ВМ (тогда на каждом доп. сервере будет равное максимально количество ВМ);\n"
            f"3. Вручную ввести количество ВМ для сервера управления с функцией ПА", 3
        )
        
        if input_masters_installation_type == 1:
            vms_on_master = installation_parameters['vms_for_master']
        elif input_masters_installation_type == 3:
            vms_on_master = input_integer_number('Введите количество ВМ для сервера управления с функцией ПА: ')
        
        #расчет ТХ 1 сервера управления с функцией ПА
        servers_list.append(calculate_master_with_dynamic(vms_on_master, installation_parameters['iso_amount']))
        
        #тогда всего ВМ для динамик останется
        all_vms_on_dynamics = installation_parameters['vms_all'] - vms_on_master

        #расчет ТХ доп. серверов с функцией ПА
        servers_list.extend(get_all_additional_servers(all_vms_on_dynamics, installation_parameters['vms_for_additional'], installation_parameters['iso_amount']))
    
    #расчет конфигурации высоконагруженной инсталляции, узел управления без ПА
    elif inpit_installation_type == 3:
        #расчет ТХ 1 сервера управления без функции ПА
        servers_list.append(calculate_master_without_dynamic(installation_parameters['iso_amount'], installation_parameters['overall_static']))
        
        #расчет ТХ доп. серверов с функцией ПА
        servers_list.extend(get_all_additional_servers(installation_parameters['vms_all'], installation_parameters['vms_for_additional'], installation_parameters['iso_amount']))

    #расчет конфигурации отказоуйстойчивого кластера
    elif inpit_installation_type == 4:
        #расчет серверов управления без динамики в отказоустойчивом кластере
        print_header('Расчет кол-ва серверов управления')
        input_masters_amount = input_odd_number('Введите количество серверов управления в данной инсталляции (нечетное число): ')
        for i in range(input_masters_amount):
            servers_list.append(calculate_master_without_dynamic(installation_parameters['iso_amount'], installation_parameters['overall_static']))
        
        #расчет дополнительных серверов с динамикой
        servers_list.extend(get_all_additional_servers(installation_parameters['vms_all'], installation_parameters['vms_for_additional'], installation_parameters['iso_amount']))

    #предварительная обработка серверов перед выводом
    servers_list = [replace_zero_with_message(server) for server in servers_list]

    #генерация таблицы с ТХ для вывода в консоль и txt файл
    fields_for_parameters = ['theads_amount', 'ram_amount', 'ssd_size', 'hdd_size']
    first_column_fields_parameters = ['Процессор 2.2 Ггц, потоков', 'Память ОЗУ, Гб', 'SSD, Гб', 'HDD, Гб']
    technical_requirements_table = generate_table('fancy', servers_list, fields_for_parameters, '\nПараметры сервера', first_column_fields_parameters)
    
    #генерация таблицы с разметкой для вывода в консоль и txt файл
    fields_for_partitioning = ['root_space', 'opt_space', 'minio_space', 'home_space']
    first_column_fields_partitioning = ['/                    [SSD]', '/opt                 [SSD]', '/opt/ptms/var/minio  [HDD]', '/home                [HDD]'] 
    partitioning_table = generate_table('fancy', servers_list, fields_for_partitioning, '\nТочка монтирования', first_column_fields_partitioning)

    #генерация таблицы с ТХ для вывода в csv файл
    csv_technical_requirements_table = generate_table('csv', servers_list, fields_for_parameters, '\nПараметры сервера', first_column_fields_parameters)

    #генерация таблицы с разметкой для вывода в csv файл
    csv_partitioning_table = generate_table('csv', servers_list, fields_for_partitioning, '\nТочка монтирования', first_column_fields_partitioning)

    #вывод данных в консоль о серверах по общем ТХ серверов системы
    print_header('Итоговые значения для серверов', header_level= 1, newline_indent=2)
    print_header('Таблица с техническими характеристиками')
    print(technical_requirements_table)

    #вывод данных в консоль о серверах по разметке дискового пространства
    print_header('Таблица с разметкой дискового пространства (Гб)')
    print(partitioning_table)

    #вывод данных в txt файл по серверам
    output_to_txt(technical_requirements_table, partitioning_table, txt_file_name)
    print(f"Данные о серверах были сохранены в файл {txt_file_name}")

    #вывод данных в csv файл по серверам
    output_to_csv(csv_technical_requirements_table, csv_partitioning_table, csv_file_name)
    print(f"Данные о серверах были сохранены в файл {csv_file_name}")