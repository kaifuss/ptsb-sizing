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

##GLOBALS
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

#Константы JSON файлов с конфигурацией
PATH_TO_DEFAULT_VALUES = 'default_values'
json_file_installation_parameters = os.path.join(PATH_TO_DEFAULT_VALUES, 'installation_parameters.json')
json_file_sources_parameters = os.path.join(PATH_TO_DEFAULT_VALUES, 'sources_parameters.json')
json_file_servers_parameters = os.path.join(PATH_TO_DEFAULT_VALUES, 'servers_parameters.json')


#Функция импорта данных из json-файла. Принимает путь к файлу и имя json-объекта, data которого нужно вернуть
#Возвращает словарь полей из json-объекта
def load_data_from_json(json_file_path, json_object_name):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            return data[json_object_name]
    
    except json.JSONDecodeError:
        print(f"Ошибка при импорте JSON данных {json_object_name} из файла {json_file_path}. Проверьте синтаксис и данные.\nСкрипт остановлен.")
        exit()


#INT MAIN
if __name__ == '__main__':
    
    servers_list = []           #лист для хранения всех объектов dict(), содержащих конфигурацию серверов
    unfiltred_sources_list = [] #список всех источников (объекты класса dict()), до фильтрации
    filtred_sources_list = []   #список всех источников с отфильтрованными параметрами (определенными выбранными полями)
    sources_fields_for_filter = ['name', 'files', 'dynamic_load', 'time_to_scan', 'vms_needed']    #список полей источников, которые будут участвовать в фильтрации

    #имя output файлов с конфигурацией
    txt_file_name = 'config.txt'    
    csv_file_name = 'config.csv'

    #импорт данных по умолчанию из json-файлов в словари
    #параметры всей конфигурации целиком
    installation_parameters = load_data_from_json(json_file_installation_parameters, 'installation_parameters')
    
    #параметры источников


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
                smtp_source_template = load_data_from_json(json_file_sources_parameters, 'smtp_source_parameters')
                new_smtp_source_parameters = sources_calculation.get_smtp_load(smtp_source_template)
                new_smtp_source_parameters['name'] = f'SMTP-источник №{smtps_amount + 1}'
                unfiltred_sources_list.append(new_smtp_source_parameters)
        
        #icap источник
        input_output.print_header('Сетевой трафик по ICAP', 2)
        if input_output.input_yes_no('Будет ли использоваться проверка по ICAP?'):
            icap_sources_amount = input_output.input_integer_with_default('Введите количество icap-источников (по умолчанию - 1): ', 1)
            for icaps_amount in range(icap_sources_amount):
                icap_source_template = load_data_from_json(json_file_sources_parameters, 'icap_source_parameters')
                new_icap_source_parameters = sources_calculation.get_icap_load(icap_source_template)
                new_icap_source_parameters['name'] = f'ICAP-источник №{icaps_amount + 1}'
                unfiltred_sources_list.append(new_icap_source_parameters)

        #агенты MP 10 EDR
        input_output.print_header('Агенты MP 10 EDR', 2)
        if input_output.input_yes_no('Будет ли использоваться проверка с агентов MP 10 EDR?'):
            edr_sources_amount = input_output.input_integer_with_default('Введите количество edr-источников (по умолчанию - 1): ', 1)
            for edrs_amount in range(edr_sources_amount):
                edr_source_template = load_data_from_json(json_file_sources_parameters, 'edr_source_parameters')
                new_edr_source_parameters = sources_calculation.get_edr_load(edr_source_template)
                new_edr_source_parameters['name'] = f'EDR-источник №{edrs_amount + 1}'
                unfiltred_sources_list.append(new_edr_source_parameters)

        #API из веб интерфейса (настраиваемый)
        input_output.print_header('Источник API c предустановленными параметрами', 2)
        if input_output.input_yes_no('Будет ли использоваться проверка по API с параметрами источника?'):
            automated_api_sources_amount = input_output.input_integer_with_default('Введите количество таких api-источников (по умолчанию - 1): ', 1)
            for automated_apis_amount in range(automated_api_sources_amount):
                automated_api_source_template = load_data_from_json(json_file_sources_parameters, 'automated_api_source_parameters')
                new_automated_api_source_parameters = sources_calculation.get_automated_api_load(automated_api_source_template)
                new_automated_api_source_parameters['name'] = f'API-источник №{automated_apis_amount + 1}'
                unfiltred_sources_list.append(new_automated_api_source_parameters)

        #API сторонеего клиента (не настраиваемый)
        input_output.print_header('Источник API c пользовательскими параметрами', 2)
        if input_output.input_yes_no('Будет ли использоваться проверка по API с параметрами источника?'):
            manual_api_sources_amount = input_output.input_integer_with_default('Введите количество таких api-источников (по умолчанию - 1): ', 1)    
            for manual_apis_amount in range(manual_api_sources_amount):
                manual_api_source_template = load_data_from_json(json_file_sources_parameters, 'manual_api_source_parameters')
                new_manual_api_source_parameters = sources_calculation.get_manual_api_load(manual_api_source_template)
                new_manual_api_source_parameters['name'] = f'API-источник №{manual_apis_amount + 1}'
                unfiltred_sources_list.append(new_manual_api_source_parameters)

        #файловое хранилище
        input_output.print_header('Файловое хранилище', 2)
        if input_output.input_yes_no('Будет ли использоваться проверка файлового хранилища?'):
            storage_sources_amount = input_output.input_integer_with_default('Введите количество storage-источников (по умолчанию - 1): ', 1)
            for storages_amount in range(storage_sources_amount):
                storage_source_template = load_data_from_json(json_file_sources_parameters, 'storage_source_parameters')
                new_storage_source_parameters = sources_calculation.get_storage_load(storage_source_template)
                new_storage_source_parameters['name'] = f'Storage-источник №{storages_amount + 1}'
                unfiltred_sources_list.append(new_storage_source_parameters)


        #после того, как обработали все источники, фильтруем их, создавая словарь с единым наполнением
        filtred_sources_list = [
            data_processing.filter_source_dict_fields(each_source, sources_fields_for_filter) for each_source in unfiltred_sources_list
        ]

        #выводим на экран результат
        input_output.print_header('Результат работы', 2)
        for source in filtred_sources_list:
            print(source)
            print("\n")

        exit()
        

    # расчет ТХ на основании вручную вводимой нагрузки
    elif main_work_mode_choice == 2:
        pass

    # расчет ТХ на основании вручную вводимого количества ВМ
    elif main_work_mode_choice == 3:
        pass

    # TODO расчет только количества ВМ по нагрузке с источников
    elif main_work_mode_choice == 4:
        pass

