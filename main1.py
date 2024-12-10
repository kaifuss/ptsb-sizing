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
TXT_OUTPUT_FILE = os.path.join(PATH_TO_OUTPUT_FILES, 'calculated_config.txt')
CSV_OUTPUT_FILE = os.path.join(PATH_TO_OUTPUT_FILES, 'calculated_sources.csv')

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
    
    original_sources_fields_for_display = [   #список полей источников, которые будут участвовать в создании таблицы
        'files',
        'dynamic_load',
        'time_to_scan',
        'vms_needed',
        'generated_storage_size']        

    russian_sources_fields_for_display = [   #тот же список, только названия на русском, для красивого чтения и понимания
        'Статических заданий,\nв час',
        'Динамических заданий,\nв час',
        'Время сканирования\n1 файла, в секундах',
        'Необходимо ВМ на этот источник',
        'Генерируемый объем хранилища,\nГБ в час']

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

        # складываем всю полученную необходимую нагрузку со всех источников в параметры инсталляции
        for counter, each_source in enumerate(unfiltred_sources_list):
            installation_parameters['overall_static'] += each_source['files']
            installation_parameters['overall_dynamic'] += each_source['dynamic_load']
            installation_parameters['overall_vms'] += each_source['vms_needed']
            installation_parameters['generated_storage_size_per_hour'] += each_source['generated_storage_size']

        #TODO спрашивать - надо ли впринципе производить расчеты или нет 
        #расчет места, занимаемого всеми источниками за N дней
        input_output.print_header('Расчет места, занимаемого заданиями со всех источников', 2, 2)
        installation_parameters['hours_of_generation_storage'] = input_output.input_integer_with_default(
            "Введите количество часов за день, в течение которых активно принимается входящий трафик (задания) системой PT SB"
            f" (по умолчанию - {installation_parameters['hours_of_generation_storage']}): ",
            installation_parameters['hours_of_generation_storage']
        )
        installation_parameters['days_to_save_data'] = input_output.input_integer_with_default(
            f"Введите количество дней, в течение которых должны сохраняться данные (по умолчанию - {installation_parameters['days_to_save_data']}): ",
            installation_parameters['days_to_save_data']
        )
        installation_parameters['overall_storage_size'] = (
            installation_parameters['generated_storage_size_per_hour'] *
            installation_parameters['hours_of_generation_storage'] *
            installation_parameters['days_to_save_data']
        )

        #TODO не генерировать таблицу, если источник один?
        # генерируем красивую таблицу со всеми источниками для вывода в консоль
        sources_fancy_table = data_processing.generate_table(
            'fancy',
            'Параметры источников',
            russian_sources_fields_for_display,
            unfiltred_sources_list,
            'name',
            original_sources_fields_for_display)
        # генерируем таблицу для вывода в CSV
        sources_csv_table = data_processing.generate_table(
            'csv',
            'Параметры источников',
            russian_sources_fields_for_display,
            unfiltred_sources_list,
            'name',
            original_sources_fields_for_display
        )
        # генерируем сводку для вывода в консоль
        sources_cli_results = (
            f"Суммарное количество статических заданий: {installation_parameters['overall_static']}\n"
            f"Суммарное количество динамических заданий после всех отсечек: {installation_parameters['overall_dynamic']}\n"
            f"Рекомендуемое количество виртуальных машин на всю инсталляцию: {installation_parameters['overall_vms']}\n"
            f"Генерируемый объем файлов заданий со всех источников в час (ГБ): {installation_parameters['generated_storage_size_per_hour']}\n"
            f"Генерируемый объем файлов заданий со всех источников за всё время (ГБ): {installation_parameters['overall_storage_size']}"
        )
        #отражаем возможность использования инсталляции AiO
        if installation_parameters['overall_vms'] > installation_parameters['vms_for_master']:
            sources_cli_results += (f"\nИспользование инсталляции AiO: Не рекомендуется")
        else:
            sources_cli_results += (f"\nИспользование инсталляции AiO: Возможно")

        #выводим красивую fancy таблицу и суммарные данные в консоль
        input_output.print_header('Итоговые показатели нагрузки со всех источников', 1, 2)
        input_output.print_header('Таблица нагрузки со всех источников')
        print(sources_fancy_table)
        input_output.print_header('Объединенные результаты расчётов')
        print(sources_cli_results)

        #начинаем сохранять всё это дело в файлы
        input_output.print_header('Сохранение результатов расчётов в файлы')
        input_output.output_data_to_txt(sources_fancy_table, 'w', TXT_OUTPUT_FILE, TXT_OUTPUT_ENCODING) # таблицу в txt файл
        input_output.output_data_to_txt("\n\n" + sources_cli_results, 'a', TXT_OUTPUT_FILE, TXT_OUTPUT_ENCODING) # суммарные данные в txt файл
        input_output.output_data_to_csv(sources_csv_table, 'w', CSV_OUTPUT_FILE, CSV_OUTPUT_ENCODING, CSV_OUTPUT_DELIMITER) # таблицу в csv файл
        print('Данные сохранены в файл txt: ', TXT_OUTPUT_FILE)
        print('Данные сохранены в файл csv: ', CSV_OUTPUT_FILE)
        print('\nВсе расчеты сорхранены в файлы. Если выполнение скрипта Вам далее не требуется - можете завершить его нажатием Ctrl+C.')

    # расчет ТХ на основании вручную вводимой нагрузки
    elif main_work_mode_choice == 2:
        input_output.print_header('Ручной ввод показателей инсталляции', header_level=1, newline_indent=2)
        input_output.print_header('Ввод показателей нагрузки')
        
        # количество заданий
        installation_parameters['overall_static'] = input_output.input_integer_number('Введите примерное количество статических заданий в час: ')
        installation_parameters['overall_dynamic'] = input_output.input_integer_number('Ввведите примерное количество динамических заданий в час после всех отсечек: ')

        # количество ВМ
        input_output.print_header('Ввод количества ВМ')
        vm_calculation_type = input_output.input_choise_digit(
            'Доступные варианты выбора количества виртуальных машин на инсталляцию:\n'
            '1. Ввести общее количество ВМ на всю инсталляцию вручную\n'
            '2. Рассчитать количество ВМ на основании нагрузки на динамику и времени сканирования на 1 файла', 2
        )
        if vm_calculation_type == 1:    # указание количества вручную
            installation_parameters['overall_vms'] = input_output.input_integer_number('Введите общее количество ВМ на всю инсталляцию: ')
        elif vm_calculation_type == 2:  # расчет количества на основе времени сканирования 1 файла
            installation_parameters['time_to_scan'] = input_output.input_integer_number('Введите время сканирования 1 файла в секундах: ')
            installation_parameters['overall_vms'] = math.ceil(installation_parameters['overall_dynamic'] * installation_parameters['time_to_scan'] / 3600)
            print('\nРасчитанное количество ВМ на инсталляцию: ', installation_parameters['overall_vms'])
        
        # расчет количества места под хранение проверенных файлов
        input_output.print_header('Расчет места под хранение проверенных файлов')
        if input_output.input_yes_no('Необходимо ли расчитать место под хранение проверенных файлов?'):
            # узнаем размер одного проверенного задания в МБайтах
            installation_parameters['one_task_size'] = input_output.input_float_number_with_default(
                f"Введите примерный размер одного проверенного задания в МБ (по умолчанию: {installation_parameters['one_task_size']}): ",
                installation_parameters['one_task_size']
            )
            # узнаем сколько часов в день принимаются задания
            installation_parameters['hours_of_generation_storage'] = input_output.input_integer_with_default(
                "Введите количество часов за день, в течение которых активно принимается входящий трафик (задания) системой PT SB"
                f" (по умолчанию - {installation_parameters['hours_of_generation_storage']}): ",
            installation_parameters['hours_of_generation_storage']
            )
            # узнаем сколько дней сохранять всё это добро
            installation_parameters['days_to_save_data'] = input_output.input_integer_with_default(
                f"Введите количество дней, в течение которых должны сохраняться данные (по умолчанию - {installation_parameters['days_to_save_data']}): ",
                installation_parameters['days_to_save_data']
            )
            # итоговое место = ( (размер_файла * количество_статических_заданий * количество_часов * количество_дней) / 1024 )
            installation_parameters['overall_storage_size'] = round( (
                installation_parameters['one_task_size'] *
                installation_parameters['overall_static'] *
                installation_parameters['hours_of_generation_storage'] *
                installation_parameters['days_to_save_data'] / 1024) , 2)
            
        # выводим всё, что насчитали по введённым параметрам
        input_output.print_header('Итоговые показатели', 2)
        print(f"Количество статических заданий в час: {installation_parameters['overall_static']}")
        print(f"Количество динамических заданий в час: {installation_parameters['overall_dynamic']}")
        print(f"Количество ВМ на инсталляцию: {installation_parameters['overall_vms']}")
        # отражаем возможность использования AiO
        if installation_parameters['overall_vms'] > installation_parameters['vms_for_master']:
            print(f"Использование инсталляции AiO: Не рекомендуется")
        else:
            print(f"Использование инсталляции AiO: Возможно")
        # выводим дисковое пространство 
        print(f"Генерируемый объем файлов заданий за всё время (ГБ): {installation_parameters['overall_storage_size']}")

    # расчет ТХ на основании вручную вводимого количества ВМ
    elif main_work_mode_choice == 3:
        input_output.print_header('Полностью ручная конфигурация', header_level=1, newline_indent=2)
        installation_parameters['overall_static'] = input_output.input_integer_number('Введите количество статических заданий в час, т.к. оно влияет на ТХ серверов управления: ')
        