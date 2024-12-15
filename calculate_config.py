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
import math
import os

# самописные функции
from additional_functions import input_output           # форматированный ввод и вывод данных 
from additional_functions import servers_calculation    # расчет параметров ТХ серверов
from additional_functions import sources_calculation    # расчет параметров источников
from additional_functions import data_processing        # обработка данных


#Константы JSON файлов с параматрами по умолчанию создаваемой конфигурации
PATH_TO_DEFAULT_VALUES = 'default_values'
JSON_FILE_INSTALLATION_PARAMETERS = os.path.join(PATH_TO_DEFAULT_VALUES, 'installation_parameters.json')
JSON_FILE_SOURCES_PARAMETERS = os.path.join(PATH_TO_DEFAULT_VALUES, 'sources_parameters.json')
JSON_FILE_SERVERS_PARAMETERS = os.path.join(PATH_TO_DEFAULT_VALUES, 'servers_parameters.json')
# валидация json файлов перед запуском скрипта
for json_file in [JSON_FILE_INSTALLATION_PARAMETERS, JSON_FILE_SOURCES_PARAMETERS, JSON_FILE_SERVERS_PARAMETERS]:
    if not data_processing.validate_json(json_file):
        print(f"Ошибка при валидации JSON-файла {json_file}. Проверьте синтаксис файла.\n\nПринудительная остановка скрипта.")
        exit() 

#Константы файлов, куда будут сохраняться результаты работы
PATH_TO_OUTPUT_FILES = 'output_files'
TXT_OUTPUT_FILE = os.path.join(PATH_TO_OUTPUT_FILES, 'calculated_config.txt')
CSV_OUTPUT_FILE = os.path.join(PATH_TO_OUTPUT_FILES, 'calculated_config.csv')
if os.path.exists(TXT_OUTPUT_FILE):
    try:
        os.remove(TXT_OUTPUT_FILE)
    except PermissionError:
        print(f"Ошибка при удалении файлов предыдущих расчетов.\nУбедитесь, что файл {TXT_OUTPUT_FILE} сейчас не используется и повторите запуск скрипта.\n")
        exit()
if os.path.exists(CSV_OUTPUT_FILE):
    try:
        os.remove(CSV_OUTPUT_FILE)
    except PermissionError:
        print(f"Ошибка при удалении файлов предыдущих расчетов.\nУбедитесь, что файл {CSV_OUTPUT_FILE} сейчас не используется и повторите запуск скрипта.\n")
        exit()

#Константы параметров вывода текста в output файлы (полученные значения в результате работы скрипта)
TXT_OUTPUT_ENCODING = 'utf-8'
CSV_OUTPUT_ENCODING = 'windows-1251'
CSV_OUTPUT_DELIMITER = ';'
CSV_OUTPUT_NEWLINE = ''


#INT MAIN
if __name__ == '__main__':

    servers_list = []               #списрок для хранения всех объектов dict(), содержащих конфигурацию серверов
    sources_list = []               #список всех источников dict()
    
    sources_fields_for_display = [          #список полей источников, которые будут участвовать в создании таблицы
        'files',
        'dynamic_load',
        'time_to_scan',
        'vms_needed',
        'generated_storage_size']        
    output_sources_fields_for_display = [   #тот же список, только для красивого вывода
        'Статических заданий,\nв час',
        'Динамических заданий,\nв час',
        'Время сканирования\n1 файла, в секундах',
        'Необходимо ВМ на этот источник',
        'Генерируемый объем хранилища,\nГБ в час']
    
    servers_fields_technical_characteristics = [            # список полей серверов, относящихся к таблице ТХ
        'theads_amount',
        'ram_amount',
        'ssd_size',
        'hdd_size',
    ]
    output_servers_fields_technical_characteristics = [     # тот же список, только для красивого вывода
        'Процессор 2.2 Ггц, потоков',
        'Память ОЗУ, Гб',
        'SSD, Гб',
        'HDD, Гб',
    ]

    servers_fields_partitioning = [             # список полей серверов, относящихся к таблице разметки
        'root_space',
        'opt_space',
        'minio_space',
        'home_space',
    ]
    output_servers_fields_partitioning = [      # тот же список, только для красивого вывода
        '/                    [SSD]',
        '/opt                 [SSD]',
        '/opt/ptms/var/minio  [HDD]',
        '/home                [HDD]',        
    ]

    #импорт данных по умолчанию из json-файлов в словарь
    installation_parameters = data_processing.load_data_from_json(JSON_FILE_INSTALLATION_PARAMETERS, 'installation_parameters')
    
    ## первая часть скрипта - узнаем и считаем и всякое прочее, исходную нагрузку, что повлияет на дальнейшие расчеты ТХ
    # Выбор как работать со скриптом - самый первый вопрос
    main_work_mode_choice = input_output.input_choise_digit(
        '\nДоступные варианты расчета технических характеристик под сервера PT SB:\n'
        '1. Расчет ТХ серверов (а также их количества) на основании известных или около известных показателей нагрузки с различных источников.\n'
        '2. Расчет ТХ серверов (а также их количества) на основании вручную вводимых показателей нагрузки на статику и динамику в час.\n'
        '3. Полностью ручной расчет ТХ серверов на основании вручную вводимого количества серверов и количества ВМ на сервер.',
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
                new_smtp_source_parameters = sources_calculation.get_smtp_load()
                new_smtp_source_parameters['name'] = f'SMTP-источник №{smtps_amount + 1}'
                sources_list.append(new_smtp_source_parameters)
        
        #icap источник
        input_output.print_header('Сетевой трафик по ICAP', 2)
        if input_output.input_yes_no('Будет ли использоваться проверка по ICAP?'):
            icap_sources_amount = input_output.input_integer_with_default('Введите количество icap-источников (по умолчанию - 1): ', 1)
            for icaps_amount in range(icap_sources_amount):
                input_output.print_header(f'Заполнение параметров ICAP-источника №{icaps_amount + 1}', 3)
                new_icap_source_parameters = sources_calculation.get_icap_load()
                new_icap_source_parameters['name'] = f'ICAP-источник №{icaps_amount + 1}'
                sources_list.append(new_icap_source_parameters)

        #агенты MP 10 EDR
        input_output.print_header('Агенты MP 10 EDR', 2)
        if input_output.input_yes_no('Будет ли использоваться проверка с агентов MP 10 EDR?'):
            edr_sources_amount = input_output.input_integer_with_default('Введите количество edr-источников (по умолчанию - 1): ', 1)
            for edrs_amount in range(edr_sources_amount):
                input_output.print_header(f'Заполнение параметров EDR-источника №{edrs_amount + 1}', 3)
                new_edr_source_parameters = sources_calculation.get_edr_load()
                new_edr_source_parameters['name'] = f'EDR-источник №{edrs_amount + 1}'
                sources_list.append(new_edr_source_parameters)

        #API из веб интерфейса (настраиваемый)
        input_output.print_header('Источник API c предустановленными параметрами', 2)
        if input_output.input_yes_no('Будет ли использоваться проверка по API с параметрами источника?'):
            automated_api_sources_amount = input_output.input_integer_with_default('Введите количество таких api-источников (по умолчанию - 1): ', 1)
            for automated_apis_amount in range(automated_api_sources_amount):
                input_output.print_header(f'Заполнение параметров преднастраиваемого API-источника №{automated_apis_amount + 1}', 3)
                new_automated_api_source_parameters = sources_calculation.get_automated_api_load()
                new_automated_api_source_parameters['name'] = f'API-источник №{automated_apis_amount + 1}'
                sources_list.append(new_automated_api_source_parameters)

        #API сторонеего клиента (не настраиваемый)
        input_output.print_header('Источник API c пользовательскими параметрами', 2)
        if input_output.input_yes_no('Будет ли использоваться проверка по API с параметрами источника?'):
            manual_api_sources_amount = input_output.input_integer_with_default('Введите количество таких api-источников (по умолчанию - 1): ', 1)    
            for manual_apis_amount in range(manual_api_sources_amount):
                input_output.print_header(f'Заполнение параметров ручного API-источника №{manual_apis_amount + 1}', 3)
                new_manual_api_source_parameters = sources_calculation.get_manual_api_load()
                new_manual_api_source_parameters['name'] = f'API-источник №{manual_apis_amount + 1}'
                sources_list.append(new_manual_api_source_parameters)

        #файловое хранилище
        input_output.print_header('Файловое хранилище', 2)
        if input_output.input_yes_no('Будет ли использоваться проверка файлового хранилища?'):
            storage_sources_amount = input_output.input_integer_with_default('Введите количество storage-источников (по умолчанию - 1): ', 1)
            for storages_amount in range(storage_sources_amount):
                input_output.print_header(f'Заполнение параметров Storage-источника №{storages_amount + 1}', 3)
                new_storage_source_parameters = sources_calculation.get_storage_load()
                new_storage_source_parameters['name'] = f'Storage-источник №{storages_amount + 1}'
                sources_list.append(new_storage_source_parameters)

        # складываем всю полученную необходимую нагрузку со всех источников в параметры инсталляции
        for counter, each_source in enumerate(sources_list):
            installation_parameters['overall_static'] += each_source['files']
            installation_parameters['overall_dynamic'] += each_source['dynamic_load']
            installation_parameters['overall_vms'] += each_source['vms_needed']
            installation_parameters['generated_storage_size_per_hour'] += each_source['generated_storage_size']
        # меняем точку на запятую для нагрузки в час
        sources_list = data_processing.prepare_sources_list(sources_list)

        #расчет места, занимаемого всеми источниками за N дней
        if installation_parameters['generated_storage_size_per_hour'] > 0:
            input_output.print_header('Расчет места под хранение проверенных файлов', 2, 2)
            installation_parameters['hours_of_generation_storage'] = input_output.input_integer_with_default(
                "Введите количество часов за день, в течение которых активно принимается входящий трафик (задания) системой PT SB"
                f" (по умолчанию - {installation_parameters['hours_of_generation_storage']}): ",
                installation_parameters['hours_of_generation_storage']
            )
            installation_parameters['days_to_save_data'] = input_output.input_integer_with_default(
                f"Введите количество дней, в течение которых должны сохраняться данные (по умолчанию - {installation_parameters['days_to_save_data']}): ",
                installation_parameters['days_to_save_data']
            )
            installation_parameters['overall_storage_size'] = math.ceil(
                installation_parameters['generated_storage_size_per_hour'] *
                installation_parameters['hours_of_generation_storage'] *
                installation_parameters['days_to_save_data']
            )

        # генерируем красивую таблицу со всеми источниками для вывода в консоль
        sources_fancy_table = data_processing.generate_table(
            'fancy',
            'Параметры источников',
            output_sources_fields_for_display,
            sources_list,
            'name',
            sources_fields_for_display)
        # генерируем таблицу для вывода в CSV
        sources_csv_table = data_processing.generate_table(
            'csv',
            'Параметры источников',
            output_sources_fields_for_display,
            sources_list,
            'name',
            sources_fields_for_display
        )
        # генерируем сводку для вывода в консоль
        sources_cli_results = (
            f"Суммарное количество статических заданий: {installation_parameters['overall_static']}\n"
            f"Суммарное количество динамических заданий после всех отсечек: {installation_parameters['overall_dynamic']}\n"
            f"Рекомендуемое количество виртуальных машин на всю инсталляцию: {installation_parameters['overall_vms']}\n"
            f"Генерируемый объем файлов заданий со всех источников в час (ГБ): {round(installation_parameters['generated_storage_size_per_hour'], 2)}\n"
            f"Генерируемый объем файлов заданий со всех источников за всё время (ГБ): {installation_parameters['overall_storage_size']}"
        )
        #отражаем возможность использования инсталляции AiO
        if installation_parameters['overall_vms'] > installation_parameters['vms_for_master']:
            sources_cli_results += (f"\nИспользование инсталляции AiO: Не рекомендуется")
        else:
            sources_cli_results += (f"\nИспользование инсталляции AiO: Возможно")

        #выводим красивую fancy таблицу и суммарные данные в консоль
        input_output.print_header('Итоговые показатели нагрузки', 1, 2)
        input_output.print_header('Таблица нагрузки со всех источников')
        print(sources_fancy_table)
        input_output.print_header('Объединенные результаты расчётов')
        print(sources_cli_results)

        #начинаем сохранять всё это дело в файлы
        input_output.print_header('Сохранение результатов расчётов в файлы')
        input_output.output_data_to_txt(    # таблицу + итоговое в txt файл
            "Параметры источников проверки файлов:\n" + sources_fancy_table + "\n\nОбъединенные результаты расчётов:\n" + sources_cli_results,
            'w',
            TXT_OUTPUT_FILE,
            TXT_OUTPUT_ENCODING
        )
        input_output.output_data_to_csv(    # таблицу в csv файл
            sources_csv_table + ['',''],
            'w',
            CSV_OUTPUT_FILE,
            CSV_OUTPUT_ENCODING,
            CSV_OUTPUT_DELIMITER
        )
        print('Данные сохранены в файл txt: ', TXT_OUTPUT_FILE)
        print('Данные сохранены в файл csv: ', CSV_OUTPUT_FILE)
        print('\nВсе расчеты сохранены в файлы. Если выполнение скрипта Вам далее не требуется - можете завершить его нажатием Ctrl+C.')

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
        input_output.print_header('Расчет места под хранение проверенных файлов', newline_indent=2)
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
            installation_parameters['overall_storage_size'] = math.ceil(
                installation_parameters['one_task_size'] *
                installation_parameters['overall_static'] *
                installation_parameters['hours_of_generation_storage'] *
                installation_parameters['days_to_save_data'] / 1024)
        
        #подготовка полученных результатвов к выводу в CLI и текстовый файл
        configured_cli_results = (
            f"Количество статических заданий в час: {installation_parameters['overall_static']}\n"
            f"Количество динамических заданий в час: {installation_parameters['overall_dynamic']}\n"
            f"Генерируемый объем файлов заданий за всё время (ГБ): {installation_parameters['overall_storage_size']}\n"
            f"Количество ВМ на инсталляцию: {installation_parameters['overall_vms']}\n"
        )
        # отражаем возможность использования AiO
        if installation_parameters['overall_vms'] > installation_parameters['vms_for_master']:
            configured_cli_results += f"Использование инсталляции AiO: Не рекомендуется"
        else:
            configured_cli_results += f"Использование инсталляции AiO: Возможно"
        
        # выводим всё, что насчитали по введённым параметрам
        input_output.print_header('Итоговые показатели нагрузки', header_level=1, newline_indent=2)
        print(configured_cli_results)
        
        # сохраняем в TXT файл, то что получилось
        input_output.output_data_to_txt(
            "Показатели нагрузки инсталляции:\n" + configured_cli_results,
            'w',
            TXT_OUTPUT_FILE,
            TXT_OUTPUT_ENCODING
        )

    # расчет ТХ только на основании вручную вводимого количества ВМ
    elif main_work_mode_choice == 3:
        input_output.print_header('Полностью ручная конфигурация', header_level=1, newline_indent=2)
        installation_parameters['overall_static'] = input_output.input_integer_number('Введите количество статических заданий в час, т.к. оно влияет на ТХ серверов управления: ')
        installation_parameters['overall_storage_size'] = input_output.input_integer_number('Введите размер хранилища в ГБ, если требуется: ')

    #расчет места под базовые образы в зависимости от их количества
    input_output.print_header('Расчет места под базовые образы', newline_indent=2)
    installation_parameters['iso_amount'] = input_output.input_integer_with_default(
        'Важно: образ это не то же самое, что виртуальная машина!\n'
        f"Введите количество базовых образов, которые будут установлены на стенде (по умолчанию - {installation_parameters['iso_amount']}): ",
        installation_parameters['iso_amount']
        )

    # вторая часть скрипта - считаем итоговую конфигурацию
    input_output.print_header('Создание конфигурации инсталляции', header_level=1, newline_indent=2)
    global_installation_choise = input_output.input_choise_digit(
        'Введите цифру, соответствующую необходимой конфигурации инсталляции:\n'
        '1. All-in-One на одном сервере.\n'
        '2. Высоконагруженная конфигурация. При этом, на сервере управления также поддерживаются динамические исследования.\n'
        '3. Высоконагруженная конфигурация. При этом, на сервере управления не устанавливаются компоненты Xen и не используются динамические исследования.\n'
        '4. Отказоустойчивый кластер.', 4
    )

    # расчет AiO инсталляции
    if global_installation_choise == 1:
        # проверяем, что количество ВМ не превышает количество ВМ для AiO
        if installation_parameters['overall_vms'] <= installation_parameters['vms_for_master']:
            installation_parameters['overall_vms'] = input_output.input_integer_with_default(
                '\nВведите количество ВМ для сервера AiO'
                f"(по умолчанию будет использоваться рекомендованное количество - {installation_parameters['overall_vms']}): ",
                installation_parameters['overall_vms']
            )
        #если всё же превышено, то выводим предупреждение
        else:
            installation_parameters['overall_vms'] = input_output.input_integer_with_default(
                f"\nВнимание! Для AiO инсталляции поддерживается не более {installation_parameters['vms_for_master']} ВМ.\n"
                f"Ранее расчитанное рекомендованное количество ВМ: {installation_parameters['overall_vms']}\n"
                "Введите количество ВМ, на которое расчитывается инсталляция: "
                f"(по умолчанию будет использоваться максимально возможное количество - {installation_parameters['vms_for_master']}): ",
                installation_parameters['vms_for_master']
            )

        # создаем AiO сервер и добавляем его в свой список
        servers_list.append(servers_calculation.calculate_master_with_dynamic(
            installation_parameters['overall_vms'],
            installation_parameters['iso_amount'],
            installation_parameters['overall_storage_size'])
        )
    
    # расчет сервер управления с ПА + дополнительные сервера ПА
    elif global_installation_choise == 2:
        # считаем как распределить ВМ между сервером управления и дополнительными серверами ПА
        # vms_all <= vms_for_master < vms_for_additional
        if installation_parameters['overall_vms'] <= installation_parameters['vms_for_master']:
            vms_for_master = installation_parameters['overall_vms']
            vms_for_additionals = installation_parameters['vms_for_additional']
        # vms_for_master < vms_all < vms_for_additional
        elif installation_parameters['vms_for_master'] < installation_parameters['overall_vms'] < installation_parameters['vms_for_additional']:
            vms_for_master = installation_parameters['vms_for_master']
            vms_for_additionals = installation_parameters['overall_vms'] - vms_for_master
        # vms_for_master < vms_for_additional <= vms_all <= vms_for_additional + vms_for_master
        elif installation_parameters['vms_for_additional'] <= installation_parameters['overall_vms'] <= installation_parameters['vms_for_additional'] + installation_parameters['vms_for_master']:
            vms_for_master = installation_parameters['overall_vms'] % installation_parameters['vms_for_additional']
            vms_for_additionals = installation_parameters['overall_vms'] - vms_for_master
        # vms_for_additional < vms_for_additional + vms_for_master < vms_all
        elif installation_parameters['vms_for_additional'] + installation_parameters['vms_for_master'] < installation_parameters['overall_vms']:
            vms_for_master = installation_parameters['vms_for_master']
            vms_for_additionals = installation_parameters['overall_vms'] - vms_for_master

        # спрашиваем пользователя, устраивает ли его то, что мы предложили:
        input_output.print_header('Расчет конфигурации сервера урпавления с функцией ПА')
        master_config_choise = input_output.input_choise_digit(
            f"1. Расчет ТХ под сервер управления с {installation_parameters['vms_for_master']} (максимально возможным числом) ВМ.\n"
            f"2. Расчет ТХ под сервер управления с {vms_for_master} ВМ. Оставшиеся {vms_for_additionals} ВМ будут распределены между дополнительными серверами ПА.\n"
            f"3. Вручную ввести количество ВМ для сервера управления.",3
        )

        if master_config_choise == 1:
            vms_for_master = installation_parameters['vms_for_master']
        elif master_config_choise == 3:
            vms_for_master = input_output.input_integer_number(
                'Введите количество ВМ для сервера управления с функцией ПА: '
            )
        
        # расчет 1 сервера управления с функцией ПА
        servers_list.append(servers_calculation.calculate_master_with_dynamic(
            vms_for_master,
            installation_parameters['iso_amount'],
            installation_parameters['overall_storage_size'])
        )
        # расчет всех дополнительных серверов ПА
        servers_list.extend(servers_calculation.get_all_additional_servers(
            vms_for_additionals,
            installation_parameters['vms_for_additional'],
            installation_parameters['iso_amount'])
        )

    # расчет сервер управления без ПА + дополнительные сервера ПА
    elif global_installation_choise == 3:
        # расчет 1 сервера управления без функции ПА
        servers_list.append(servers_calculation.calculate_master_without_dynamic(
            installation_parameters['iso_amount'],
            installation_parameters['overall_static'],
            installation_parameters['overall_storage_size'])
        )

        # расчет всех дополнительных серверов ПА
        servers_list.extend(servers_calculation.get_all_additional_servers(
            installation_parameters['overall_vms'],
            installation_parameters['vms_for_additional'],
            installation_parameters['iso_amount'])
        )

    # расчет отказоустойчивость + дополнительные сервера ПА
    elif global_installation_choise == 4:
        # узнаем количество серверов управления
        input_output.print_header('Параметры кластера')
        master_servers_amount = input_output.input_odd_number('Введите количество серверов управления в данной инсталляции (нечетное число): ')
        for i in range(master_servers_amount):
            servers_list.append(servers_calculation.calculate_master_without_dynamic(
                installation_parameters['iso_amount'],
                installation_parameters['overall_static'],
                installation_parameters['overall_storage_size'])
            )

        # и добавляем ноды динамики
        servers_list.extend(servers_calculation.get_all_additional_servers(
            installation_parameters['overall_vms'],
            installation_parameters['vms_for_additional'],
            installation_parameters['iso_amount'])
        )

    # обработка серверов перед выводом
    servers_list = data_processing.prepare_servers_list(servers_list)

    # создаем таблицу с техническими характеристиками для вывода в консоль
    servers_tech_cli_table = data_processing.generate_table(
        'fancy',
        'Параметры серверов',
        output_servers_fields_technical_characteristics,
        servers_list,
        'server_role',
        servers_fields_technical_characteristics
    )
    # таблицу с техническими характеристиками для csv-файла
    servers_tech_csv_table = data_processing.generate_table(
        'csv',
        'Параметры серверов',
        output_servers_fields_technical_characteristics,
        servers_list,
        'server_role',
        servers_fields_technical_characteristics
    )
    # таблицу с разметкой диска для вывода в консоль
    servers_part_cli_table = data_processing.generate_table(
        'fancy',
        'Точка монтирования',
        output_servers_fields_partitioning,
        servers_list,
        'server_role',
        servers_fields_partitioning
    )
    # таблицу с разметкой диска для вывода в csv-файл
    servers_part_csv_table = data_processing.generate_table(
        'csv',
        'Точка монтирования',
        output_servers_fields_partitioning,
        servers_list,
        'server_role',
        servers_fields_partitioning
    )

    # вывод таблиц в консоль
    input_output.print_header('Итоговые значения для серверов', header_level = 1, newline_indent = 2)
    input_output.print_header('Таблица с техническими характеристиками')
    print(servers_tech_cli_table)
    input_output.print_header('Таблица с разметкой дисков')
    print(servers_part_cli_table)

    # вывод таблиц в файлы
    input_output.print_header('Сохранение результатов расчётов в файлы')
    input_output.output_data_to_txt(
        "\n\n\nТехнические характеристики серверов:\n" + servers_tech_cli_table + "\n\nРазметка дискового пространства серверов:\n" + servers_part_cli_table,
        'a',
        TXT_OUTPUT_FILE,
        TXT_OUTPUT_ENCODING
    )
    input_output.output_data_to_csv(
        servers_tech_csv_table + ['',''] + servers_part_csv_table,
        'a',
        CSV_OUTPUT_FILE,
        CSV_OUTPUT_ENCODING,
        CSV_OUTPUT_DELIMITER
    )
    print('Данные сохранены в файл txt: ', TXT_OUTPUT_FILE)
    print('Данные сохранены в файл csv: ', CSV_OUTPUT_FILE)
    print('\nВсе расчеты сохранены в файлы. Выполнение скрипта закончено.\n')