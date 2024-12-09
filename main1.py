# -*- coding: utf-8 -*-
print('''
╔═══════════════════════════════════════════════════════════════════════════╗
║                                  WELCOME                                  ║
║                              PTSB sizing tool                             ║
║                          by @github.com/kaifuss/                          ║
╚═══════════════════════════════════════════════════════════════════════════╝
''')

## DEPENDENCIES
# встроенные библиотеки python
import csv
import math
import json
import os
from tabulate import tabulate

# самописные функции
from additional_functions import input_output
#from additional_functions import servers_calculation
from additional_functions import sources_calculation
from additional_functions import data_processing
from additional_functions import work_with_json

##GLOBALS
#Цветовые коды
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RESET = '\033[0m'  #сброс на дефолт


#Константы JSON файлов с параматрами по-умолчанию создаваемой конфигурации
PATH_TO_DEFAULT_VALUES = 'default_values'
JSON_FILE_INSTALLATION_PARAMETERS = os.path.join(PATH_TO_DEFAULT_VALUES, 'installation_parameters.json')
JSON_FILE_SOURCES_PARAMETERS = os.path.join(PATH_TO_DEFAULT_VALUES, 'sources_parameters.json')
JSON_FILE_SERVERS_PARAMETERS = os.path.join(PATH_TO_DEFAULT_VALUES, 'servers_parameters.json')

#Константы файлов, куда будут сохраняться результаты работы
PATH_TO_OUTPUT_FILES = 'output_files'
TXT_OUTRPUT_FILE_SOURCES = os.path.join(PATH_TO_OUTPUT_FILES, 'calculated_sources.txt')
CSV_OUTPUT_FILE_SOURCES = os.path.join(PATH_TO_OUTPUT_FILES, 'calculated_sources.csv')
TXT_OUTPUT_FILE_SERVERS = os.path.join(PATH_TO_OUTPUT_FILES, 'calculated_servers.txt')
CSV_OUTPUT_FILE_SERVERS = os.path.join(PATH_TO_OUTPUT_FILES, 'calculated_servers.csv')

#Константы параметров вывода текста в output файлы (полученные значения в результате работы скрипта)
TXT_OUTPUT_ENCODING = 'utf-8'
CSV_OUTPUT_ENCODING = 'windows-1251'
CSV_OUTPUT_DELIMITER = ';'
CSV_OUTPUT_NEWLINE = ''


#INT MAIN
if __name__ == '__main__':
    
    servers_list = []               #лист для хранения всех объектов dict(), содержащих конфигурацию серверов
    unfiltred_sources_list = []     #список всех источников (объекты класса dict()), до фильтрации
    filtred_sources_list = []       #список всех источников с отфильтрованными параметрами (определенными выбранными полями)
    sources_fields_for_filter = [   #список полей источников, которые будут участвовать в фильтрации
        'name',
        'files',
        'dynamic_load',
        'time_to_scan',
        'vms_needed',
        'generated_storage_size']
    
    original_sources_fields_for_display = [   #список полей источников, которые будут выводииться на экран
        'files',
        'dynamic_load',
        'time_to_scan',
        'vms_needed',
        'generated_storage_size']        

    russian_sources_fields_for_display = [   #тот же список, только названия на русском, для красивого вывода
        'Статических заданий,\nв час',
        'Динамических заданий,\nв час',
        'Время сканирования\n1 файла, в секундах',
        'Необходимо ВМ на этот источник',
        'Генерируемый объем хранилища,\nМБ в час']

    #имя output файлов с конфигурацией
    txt_file_name = 'config.txt'    
    csv_file_name = 'config.csv'

    #импорт данных по умолчанию из json-файлов в словари
    installation_parameters = work_with_json.load_data_from_json(JSON_FILE_INSTALLATION_PARAMETERS, 'installation_parameters')
    

    ## НАЧАЛО РАБОТЫ СО СКРИПТОМ
    # Выбор как работать со скриптом - самый первый вопрос
    main_work_mode_choice = input_output.input_choise_digit(
        '\nДоступные варианты расчета технических характеристик под сервера PT SB:\n'
        '1. Расчет ТХ серверов (а также их количества) на основании известных или около известных показателей нагрузки с различных источников\n'
        '2. Расчет ТХ серверов (а также их количества) на основании вручную вводимых показателей нагрузки на статику и динамику в час\n'
        '3. Полностью ручной расчет ТХ серверов на основании вручную вводимого количества ВМ на сервер и количества серверов',
        3
    )

    # расчет ТХ через расчет нагрузки с источников 
    if main_work_mode_choice == 1:
        input_output.print_header('Расчет нагрузки с источников', header_level=1, newline_indent=2)

        #smtp источник
        input_output.print_header('Электронная почта организации', 2)
        if input_output.input_yes_no('Будет ли проверяться почтовый трафик?'):
            smtp_sources_amount = input_output.input_integer_with_default('Введите количество smtp-источников (по умолчанию - 1): ', 1)
            for smtps_amount in range(smtp_sources_amount):
                input_output.print_header(f'Заполнение параметров SMTP-источника №{smtps_amount + 1}', 3)
                smtp_source_template = work_with_json.load_data_from_json(JSON_FILE_SOURCES_PARAMETERS, 'smtp_source_parameters')
                new_smtp_source_parameters = sources_calculation.get_smtp_load(smtp_source_template)
                new_smtp_source_parameters['name'] = f'SMTP-источник №{smtps_amount + 1}'
                unfiltred_sources_list.append(new_smtp_source_parameters)
        
        #icap источник
        input_output.print_header('Сетевой трафик по ICAP', 2)
        if input_output.input_yes_no('Будет ли использоваться проверка по ICAP?'):
            icap_sources_amount = input_output.input_integer_with_default('Введите количество icap-источников (по умолчанию - 1): ', 1)
            for icaps_amount in range(icap_sources_amount):
                input_output.print_header(f'Заполнение параметров ICAP-источника №{icaps_amount + 1}', 3)
                icap_source_template = work_with_json.load_data_from_json(JSON_FILE_SOURCES_PARAMETERS, 'icap_source_parameters')
                new_icap_source_parameters = sources_calculation.get_icap_load(icap_source_template)
                new_icap_source_parameters['name'] = f'ICAP-источник №{icaps_amount + 1}'
                unfiltred_sources_list.append(new_icap_source_parameters)

        #агенты MP 10 EDR
        input_output.print_header('Агенты MP 10 EDR', 2)
        if input_output.input_yes_no('Будет ли использоваться проверка с агентов MP 10 EDR?'):
            edr_sources_amount = input_output.input_integer_with_default('Введите количество edr-источников (по умолчанию - 1): ', 1)
            for edrs_amount in range(edr_sources_amount):
                input_output.print_header(f'Заполнение параметров EDR-источника №{edrs_amount + 1}', 3)
                edr_source_template = work_with_json.load_data_from_json(JSON_FILE_SOURCES_PARAMETERS, 'edr_source_parameters')
                new_edr_source_parameters = sources_calculation.get_edr_load(edr_source_template)
                new_edr_source_parameters['name'] = f'EDR-источник №{edrs_amount + 1}'
                unfiltred_sources_list.append(new_edr_source_parameters)

        #API из веб интерфейса (настраиваемый)
        input_output.print_header('Источник API c предустановленными параметрами', 2)
        if input_output.input_yes_no('Будет ли использоваться проверка по API с параметрами источника?'):
            automated_api_sources_amount = input_output.input_integer_with_default('Введите количество таких api-источников (по умолчанию - 1): ', 1)
            for automated_apis_amount in range(automated_api_sources_amount):
                input_output.print_header(f'Заполнение параметров преднастраиваемого API-источника №{automated_apis_amount + 1}', 3)
                automated_api_source_template = work_with_json.load_data_from_json(JSON_FILE_SOURCES_PARAMETERS, 'automated_api_source_parameters')
                new_automated_api_source_parameters = sources_calculation.get_automated_api_load(automated_api_source_template)
                new_automated_api_source_parameters['name'] = f'API-источник №{automated_apis_amount + 1}'
                unfiltred_sources_list.append(new_automated_api_source_parameters)

        #API сторонеего клиента (не настраиваемый)
        input_output.print_header('Источник API c пользовательскими параметрами', 2)
        if input_output.input_yes_no('Будет ли использоваться проверка по API с параметрами источника?'):
            manual_api_sources_amount = input_output.input_integer_with_default('Введите количество таких api-источников (по умолчанию - 1): ', 1)    
            for manual_apis_amount in range(manual_api_sources_amount):
                input_output.print_header(f'Заполнение параметров ручного API-источника №{manual_apis_amount + 1}', 3)
                manual_api_source_template = work_with_json.load_data_from_json(JSON_FILE_SOURCES_PARAMETERS, 'manual_api_source_parameters')
                new_manual_api_source_parameters = sources_calculation.get_manual_api_load(manual_api_source_template)
                new_manual_api_source_parameters['name'] = f'API-источник №{manual_apis_amount + 1}'
                unfiltred_sources_list.append(new_manual_api_source_parameters)

        #файловое хранилище
        input_output.print_header('Файловое хранилище', 2)
        if input_output.input_yes_no('Будет ли использоваться проверка файлового хранилища?'):
            storage_sources_amount = input_output.input_integer_with_default('Введите количество storage-источников (по умолчанию - 1): ', 1)
            for storages_amount in range(storage_sources_amount):
                input_output.print_header(f'Заполнение параметров Storage-источника №{storages_amount + 1}', 3)
                storage_source_template = work_with_json.load_data_from_json(JSON_FILE_SOURCES_PARAMETERS, 'storage_source_parameters')
                new_storage_source_parameters = sources_calculation.get_storage_load(storage_source_template)
                new_storage_source_parameters['name'] = f'Storage-источник №{storages_amount + 1}'
                unfiltred_sources_list.append(new_storage_source_parameters)


        #после того, как обработали все источники, фильтруем их, создавая словарь с единым наполнением для будущей красивой таблицы
        filtred_sources_list = [
            data_processing.filter_source_dict_fields(each_source, sources_fields_for_filter) for each_source in unfiltred_sources_list
        ]

        # складываем всю полученную необходимую нагрузку со всех источников в параметры инсталляции
        for counter, each_source in enumerate(filtred_sources_list):
            installation_parameters['overall_static'] += each_source['files']
            installation_parameters['overall_dynamic'] += each_source['dynamic_load']
            installation_parameters['overall_vms'] += each_source['vms_needed']
            installation_parameters['generated_storage_size_per_hour'] += each_source['generated_storage_size']


        # выводим красивой таблицей всё что насчитали про источники
        sources_fancy_table = data_processing.generate_table(
            'fancy',
            'Параметры источников',
            russian_sources_fields_for_display,
            filtred_sources_list,
            'name',
            original_sources_fields_for_display)

        input_output.print_header('Посчитанные параметры источников', 2)
        print(sources_fancy_table)

        input_output.print_header('Объединенные результаты расчётов', 2)
        print(f"Количество статических заданий: {installation_parameters['overall_static']}")
        print(f"Количество динамических заданий после всех отсечек: {installation_parameters['overall_dynamic']}")
        print(f"Рекомендуемое количество виртуальных машин на всю инсталляцию: {installation_parameters['overall_vms']}")
        print(f"Генерируемый объем файлов заданий со всех источников в час: {installation_parameters['generated_storage_size_per_hour']}")

        exit()

    # расчет ТХ на основании вручную вводимой нагрузки
    elif main_work_mode_choice == 2:
        pass

    # расчет ТХ на основании вручную вводимого количества ВМ
    elif main_work_mode_choice == 3:
        pass