#встрооенные библиотеки питона
import math
import os

#самописные функции
from additional_functions import input_output
from additional_functions import data_processing

#Константы JSON файлов с параматрами по умолчанию создаваемой конфигурации
PATH_TO_DEFAULT_VALUES = 'default_values'
JSON_FILE_SOURCES_PARAMETERS = os.path.join(PATH_TO_DEFAULT_VALUES, 'sources_parameters.json')


# посчитать генерируемый объем файлового хранилища с каждого источника
def get_generated_storage_size(tasks_per_hour: int, one_task_size: float) -> float:
    """
    Возвращает объем генерируемого дискового пространства в час одним источником.

    Параметры:
        tasks_per_hour (int): Количество статических заданий в час с этого источника.
        one_task_size (float): Размер одного задания в МБайтах.
    
    Возвращает:
        float: Объем генерируемого дискового пространства в час этим источником в ГБайтах.
    """

    tasks_per_hour = input_output.input_integer_with_default(
        f"Введите количество статических заданий в час с данного источника (по умолчаению - {tasks_per_hour}): ", tasks_per_hour)
    one_task_size = input_output.input_float_number_with_default(
        f"Введите размер одного задания в МБайтах (по умолчанию - {one_task_size}): ", one_task_size)
    
    generated_size_gb = round((tasks_per_hour * one_task_size) / 1024, 2)

    return generated_size_gb


#получить % отсечки для ПА для любого источника
def get_dynamic_cutoff(default_value: int) -> float:
    """
    Запрашивает у пользователя целое число % заданий от общего количества заданий, которые подходят под ПА. Универсальная функция.
    
    Параметры:
        default_value (int): Значение по умолчанию, которое будет использоваться, если пользователь ничего не введет.

    Возвращает:
        float: Введенное пользователем число, преобразованное в долю (от 0 до 1).
    """

    dynamic_cutoff = input_output.input_integer_with_default(f"Введите примерный % заданий от общего количества, которые пойдут на динамический анализ (по умолчанию - {default_value}%): ", default_value)
    dynamic_cutoff = float(dynamic_cutoff) / 100
    return dynamic_cutoff


#получить % отсечки по префильтру для любого источника
def get_prefilter_cutoff(default_value: int) -> float:
    """
    Запрашивает у пользователя целое число % заданий от заданий ПА, которые останутся после статической префильтрации.

    Параметры:
        default_value (int): Значение по умолчанию, которое будет использоваться, если пользователь ничего не введет.

    Возвращает:
        float: Введенное пользователем число, преобразованное в долю (от 0 до 1).
    """
    prefilter_cutoff = input_output.input_integer_with_default(f"Введите примерный % заданий от заданий ПА, которые останутся после префильтрации (по умолчанию - {default_value}%): ", default_value)
    prefilter_cutoff = float(prefilter_cutoff) / 100
    return prefilter_cutoff


#получить % отсечки по кэшированию для любого источника
def get_cache_cutoff(default_value: int) -> float:
    """
    Запрашивает у пользователя целое число % заданий от заданий ПА, которые останутся после отброса кэшированием.

    Параметры:
        default_value (int): Значение по умолчанию, которое будет использоваться, если пользователь ничего не введет.

    Возвращает:
        float: Введенное пользователем число, преобразованное в долю (от 0 до 1).
    """

    cache_cutoff = input_output.input_integer_with_default(f"Введите примерный % заданий от заданий ПА, которые останутся после отброса кэшированием (по умолчанию - {default_value }%): ", default_value)
    cache_cutoff = float(cache_cutoff) / 100
    return cache_cutoff


#получить время сканирования для любого источника
def get_time_to_scan(default_value: int):
    """
    Запрашивает у пользователя целое число количество секунд, как долго будут сканироваться задания с данного источника.

    Параметры:
        default_value (int): Значение по умолчанию, которое будет использоваться, если пользователь ничего не введет.

    Возвращает:
        int: Введенное пользователем число, количество секунд.
    """

    input_scan_time = input_output.input_integer_with_default(f"Введите время в секундах, как долго будут сканироваться задания с этого источника (по умолчанию - {default_value}): ", default_value)
    return input_scan_time


#расчет нагрузки с почтового трафика
def get_smtp_load() -> dict:
    """
    Создает smtp объект-источник с параметрами по умолчанию. Обрабатывает показатели статической и динамическоой нагрузки. 

    Возвращает:
        dict: Созданный словарь с показателями нагрузки smtp источника.
    """
    
    # создаем объект-источник с параметрами по умолчанию
    smtp_source_parameters = data_processing.load_data_from_json(JSON_FILE_SOURCES_PARAMETERS, 'smtp_source_parameters')

    #Если количество писем в час - неизвестно, то расчет идет от количества пользователей.
    if not input_output.input_yes_no('Известно ли количество писем в час с данного источника?'):
        
        # запрашиаем количество пользователей
        smtp_source_parameters['users'] = input_output.input_integer_number('Введите количество пользователей почты: ')

        # количество писем в час - неизвестно
        smtp_source_parameters['users_multiplier'] = input_output.input_integer_with_default(
            f"Ввведите количество писем на 1 пользователя (по умолчанию - {smtp_source_parameters['users_multiplier']}): ",
            smtp_source_parameters['users_multiplier']
        )

        # в таком случае количество писем в час - вычисляется
        smtp_source_parameters['mails'] = smtp_source_parameters['users'] * smtp_source_parameters['users_multiplier']

        # процент писем с вложениями запрашивается
        smtp_source_parameters['mails_with_attachments_percent'] = input_output.input_integer_with_default(
            f"Введите примерный % писем от общего количества, которые предположительно содержат вложения (по умолчанию - {smtp_source_parameters['mails_with_attachments_percent']}%): ",
            smtp_source_parameters['mails_with_attachments_percent']
        )

        # количество писем с вложениями - вычисляется
        smtp_source_parameters['mails_with_attachments'] = math.ceil(
            smtp_source_parameters['mails'] *
            smtp_source_parameters['mails_with_attachments_percent'] / 100.0
        )
    
    # если всё же количество писем в час известно
    else:

        # запрашиваем количество писем в час
        smtp_source_parameters['mails'] = input_output.input_integer_number('Введите количество писем в час: ')

        if input_output.input_yes_no('Известно ли количетсво писем в час, содержащих вложения?'):
            # количество писем с вложениями - известно
            smtp_source_parameters['mails_with_attachments'] = input_output.input_integer_number(
                'Введите количество писем в час, которые содержат вложения: '
            )

        else:
            # количество писем с вложениями - неизвестно
            smtp_source_parameters['mails_with_attachments_percent'] = input_output.input_integer_with_default(
                f"Введите примерный % писем от общего количества, которые предположительно содержат вложения (по умолчанию - {smtp_source_parameters['mails_with_attachments_percent']}%): ",
                smtp_source_parameters['mails_with_attachments_percent']
            )

            # количество писем с вложениями - вычисляется
            smtp_source_parameters['mails_with_attachments'] = math.ceil(
                smtp_source_parameters['mails'] *
                smtp_source_parameters['mails_with_attachments_percent'] / 100.0
            )

    # теперь узнаем количество вложений на 1 письмо в среднем и вычисляем общее количество писем с вложениями
    smtp_source_parameters['attachments_per_mail'] = input_output.input_integer_with_default(
        f"Введите количество вложений на 1 письмо, содержащее вложения (по умолчанию - {smtp_source_parameters['attachments_per_mail']}): ",
        smtp_source_parameters['attachments_per_mail']
    )
    
    # для общего вида добавляем ключ 'files', чтобы потом обрабатывать эти показатели едино в MAIN.py
    smtp_source_parameters['files'] = smtp_source_parameters['mails']

    # получаем/обновляем все возможные отсечки
    smtp_source_parameters['dynamic_cutoff'] = get_dynamic_cutoff(smtp_source_parameters['dynamic_cutoff'])
    smtp_source_parameters['prefilter_cutoff'] = get_prefilter_cutoff(smtp_source_parameters['prefilter_cutoff'])
    smtp_source_parameters['cache_cutoff'] = get_cache_cutoff(smtp_source_parameters['cache_cutoff'])
    smtp_source_parameters['time_to_scan'] = get_time_to_scan(smtp_source_parameters['time_to_scan'])

    # вычисляем итоговое количество файлов для ПА с этого источника
    smtp_source_parameters['dynamic_load'] = ( math.ceil(
        smtp_source_parameters['mails_with_attachments'] *
        smtp_source_parameters['attachments_per_mail'] *
        smtp_source_parameters['dynamic_cutoff'] *
        smtp_source_parameters['prefilter_cutoff'] *
        smtp_source_parameters['cache_cutoff'])
    )

    # вычисляем необходимое количество ВМ для этого источника
    smtp_source_parameters['vms_needed'] = math.ceil(smtp_source_parameters['dynamic_load'] * smtp_source_parameters['time_to_scan'] / 3600)
    
    # узнаем генерируемый объем дискового пространства экземляром источника в час
    if input_output.input_yes_no('Необходимо ли рассчитать объем генерируемого дискового пространства с этого источника?'):
        smtp_source_parameters['generated_storage_size'] = get_generated_storage_size(smtp_source_parameters['files'], smtp_source_parameters['one_task_size'])

    return smtp_source_parameters


#расчет нагрузки с ICAP
def get_icap_load() -> dict:
    """
    Создает icap объект-источник с параметрами по умолчанию. Обрабатывает показатели статической и динамическоой нагрузки.

    Возвращает:
        dict: Созданный словарь с показателями нагрузки icap источника.
    """
    
    # создаем объект-источник с параметрами по умолчанию
    icap_source_parameters = data_processing.load_data_from_json(JSON_FILE_SOURCES_PARAMETERS, 'icap_source_parameters')

    # если количество файлов неизвестно, то вычисляем среднее количество из пропорции:
    if input_output.input_yes_no('Известно ли количетсво файлов в трафике за час?'):
        icap_source_parameters['files'] = input_output.input_integer_number('Введите количество файлов в час: ')
    else:
        icap_source_parameters['speed'] = input_output.input_integer_number('Введите скорость трафика в Мбит/с: ')
        icap_source_parameters['files'] = math.ceil( (7000 * icap_source_parameters['speed']) / 1024 )

    # получаем/обновляем все возможные отсечки
    icap_source_parameters['dynamic_cutoff'] = get_dynamic_cutoff(icap_source_parameters['dynamic_cutoff'])
    icap_source_parameters['prefilter_cutoff'] = get_prefilter_cutoff(icap_source_parameters['prefilter_cutoff'])
    icap_source_parameters['cache_cutoff'] = get_cache_cutoff(icap_source_parameters['cache_cutoff'])
    icap_source_parameters['time_to_scan'] = get_time_to_scan(icap_source_parameters['time_to_scan'])

    # вычисляем итоговое количество файлов для ПА с этого источника
    icap_source_parameters['dynamic_load'] = ( math.ceil(
        icap_source_parameters['files'] *
        icap_source_parameters['dynamic_cutoff'] *
        icap_source_parameters['prefilter_cutoff'] *
        icap_source_parameters['cache_cutoff'])
    )

    # вычисляем необходимое количество ВМ для этого источника
    icap_source_parameters['vms_needed'] = math.ceil(icap_source_parameters['dynamic_load'] * icap_source_parameters['time_to_scan'] / 3600)    
    
    # узнаем генерируемый объем дискового пространства экземляром источника в час
    if input_output.input_yes_no('Необходимо ли рассчитать объем генерируемого дискового пространства с этого источника?'):
        icap_source_parameters['generated_storage_size'] = get_generated_storage_size(icap_source_parameters['files'], icap_source_parameters['one_task_size'])

    return icap_source_parameters


#расчет нагрузки с MP 10 EDR
def get_edr_load() -> dict:
    """
    Создает mp edr объект-источник с параметрами по умолчанию. Обрабатывает показатели статической и динамическоой нагрузки.

    Возвращает:
        dict: Созданный словарь с показателями нагрузки pt edr источника.
    """    

    # создаем объект-источник с параметрами по умолчанию
    edr_source_parameters = data_processing.load_data_from_json(JSON_FILE_SOURCES_PARAMETERS, 'edr_source_parameters')

    # если количество файлов неизвестно, то вычисляем среднее количество через multiplier
    if input_output.input_yes_no('Известно ли общее количество файлов со всех агентов в час?'):
        edr_source_parameters['files'] = input_output.input_integer_number('Введите количество файлов в час: ')
    else:
        edr_source_parameters['agents'] = input_output.input_integer_number('Введите количество агентов mp 10 edr, с которых будут проверяться файлы: ')
        edr_source_parameters['agents_multiplier'] = input_output.input_integer_with_default(
            f"Введите примерное количество файлов с 1 агента edr (по умолчанию - {edr_source_parameters['agents_multiplier']}): ",
            edr_source_parameters['agents_multiplier']
        )
        edr_source_parameters['files'] = edr_source_parameters['agents'] * edr_source_parameters ['agents_multiplier']    

    # получаем/обновляем все возможные отсечки
    edr_source_parameters['dynamic_cutoff'] = get_dynamic_cutoff(edr_source_parameters['dynamic_cutoff'])
    edr_source_parameters['prefilter_cutoff'] = get_prefilter_cutoff(edr_source_parameters['prefilter_cutoff'])
    edr_source_parameters['cache_cutoff'] = get_cache_cutoff(edr_source_parameters['cache_cutoff'])
    edr_source_parameters['time_to_scan'] = get_time_to_scan(edr_source_parameters['time_to_scan'])

    # вычисляем итоговое количество файлов для ПА с этого источника
    edr_source_parameters['dynamic_load'] = ( math.ceil(
        edr_source_parameters['files'] *
        edr_source_parameters['dynamic_cutoff'] *
        edr_source_parameters['prefilter_cutoff'] *
        edr_source_parameters['cache_cutoff'])
    )

    # вычисляем необходимое количество ВМ для этого источника
    edr_source_parameters['vms_needed'] = math.ceil(edr_source_parameters['dynamic_load'] * edr_source_parameters['time_to_scan'] / 3600)  
    
    # узнаем генерируемый объем дискового пространства экземляром источника в час
    if input_output.input_yes_no('Необходимо ли рассчитать объем генерируемого дискового пространства с этого источника?'):
        edr_source_parameters['generated_storage_size'] = get_generated_storage_size(edr_source_parameters['files'], edr_source_parameters['one_task_size'])
    
    return edr_source_parameters


#расчет нагрузки с API-источника с выбранными параметрами проверки
def get_automated_api_load() -> dict:
    """
    Создает automated api объект-источник с параметрами по умолчанию. Обрабатывает показатели статической и динамическоой нагрузки.

    Возвращает:
        dict: Созданный словарь с показателями нагрузки настроенного api источника.
    """

    # создаем объект-источник с параметрами по умолчанию
    automated_api_source_parameters = data_processing.load_data_from_json(JSON_FILE_SOURCES_PARAMETERS, 'automated_api_source_parameters')

    # получаем количество файлов в час
    automated_api_source_parameters['files'] = input_output.input_integer_number('Введите примерное количество файлов в час: ')

    # получаем/обновляем все возможные отсечки
    automated_api_source_parameters['dynamic_cutoff'] = get_dynamic_cutoff(automated_api_source_parameters['dynamic_cutoff'])
    automated_api_source_parameters['prefilter_cutoff'] = get_prefilter_cutoff(automated_api_source_parameters['prefilter_cutoff'])
    automated_api_source_parameters['cache_cutoff'] = get_cache_cutoff(automated_api_source_parameters['cache_cutoff'])
    automated_api_source_parameters['time_to_scan'] = get_time_to_scan(automated_api_source_parameters['time_to_scan'])

    # вычисляем итоговое количество файлов для ПА с этого источника
    automated_api_source_parameters['dynamic_load'] = ( math.ceil(
        automated_api_source_parameters['files'] *
        automated_api_source_parameters['dynamic_cutoff'] *
        automated_api_source_parameters['prefilter_cutoff'] *
        automated_api_source_parameters['cache_cutoff'])
    )

    # вычисляем необходимое количество ВМ для этого источника
    automated_api_source_parameters['vms_needed'] = math.ceil(automated_api_source_parameters['dynamic_load'] * automated_api_source_parameters['time_to_scan'] / 3600) 

        # узнаем генерируемый объем дискового пространства экземляром источника в час
    if input_output.input_yes_no('Необходимо ли рассчитать объем генерируемого дискового пространства с этого источника?'):
        automated_api_source_parameters['generated_storage_size'] = get_generated_storage_size(automated_api_source_parameters['files'], automated_api_source_parameters['one_task_size'])

    return automated_api_source_parameters


#расчет нагрузки с API-источника с ручными параметрами проверки
def get_manual_api_load() -> dict:
    """
    Создает manual api объект-источник с параметрами по умолчанию. Обрабатывает показатели статической и динамическоой нагрузки.

    Возвращает:
        dict: Созданный словарь с показателями нагрузки ручного api источника.
    """

    # создаем объект-источник с параметрами по умолчанию
    manual_api_source_parameters = data_processing.load_data_from_json(JSON_FILE_SOURCES_PARAMETERS, 'manual_api_source_parameters')

    # получаем количество файлов в час
    manual_api_source_parameters['files'] = input_output.input_integer_number('Введите примерное количество файлов в час: ')

    # получаем/обновляем все возможные отсечки
    manual_api_source_parameters['dynamic_cutoff'] = get_dynamic_cutoff(manual_api_source_parameters['dynamic_cutoff'])
    manual_api_source_parameters['cache_cutoff'] = get_cache_cutoff(manual_api_source_parameters['cache_cutoff'])
    manual_api_source_parameters['time_to_scan'] = get_time_to_scan(manual_api_source_parameters['time_to_scan'])

    # вычисляем итоговое количество файлов для ПА с этого источника
    manual_api_source_parameters['dynamic_load'] = ( math.ceil(
        manual_api_source_parameters['files'] *
        manual_api_source_parameters['dynamic_cutoff'] *
        manual_api_source_parameters['cache_cutoff'])
    )

    # вычисляем необходимое количество ВМ для этого источника
    manual_api_source_parameters['vms_needed'] = math.ceil(manual_api_source_parameters['dynamic_load'] * manual_api_source_parameters['time_to_scan'] / 3600) 
    
    # узнаем генерируемый объем дискового пространства экземляром источника в час
    if input_output.input_yes_no('Необходимо ли рассчитать объем генерируемого дискового пространства с этого источника?'):
        manual_api_source_parameters['generated_storage_size'] = get_generated_storage_size(manual_api_source_parameters['files'], manual_api_source_parameters['one_task_size'])

    return manual_api_source_parameters


#расчет нагрузки с хранилища файлов
def get_storage_load() -> dict:
    """
    Создает storage объект-источник с параметрами по умолчанию. Обрабатывает показатели статической и динамическоой нагрузки.

    Возвращает:
        dict: Созданный словарь с показателями нагрузки источника файловой шары.
    """

    # создаем объект-источник с параметрами по умолчанию
    storage_source_parameters = data_processing.load_data_from_json(JSON_FILE_SOURCES_PARAMETERS, 'storage_source_parameters')

    # получаем грубые показатели (а иначе никак :/ ) 
    storage_source_parameters['files'] = input_output.input_integer_number('Введите примерное количество файлов в час, которые будут проверяться статикой: ')
    storage_source_parameters['dynamic_load'] = input_output.input_integer_number('Введите примерное количество файлов в час, которые будут проверяться динамикой: ')

    # получаем/обновляем все возможные отсечки
    storage_source_parameters['prefilter_cutoff'] = get_prefilter_cutoff(storage_source_parameters['prefilter_cutoff'])
    storage_source_parameters['cache_cutoff'] = get_cache_cutoff(storage_source_parameters['cache_cutoff'])
    storage_source_parameters['time_to_scan'] = get_time_to_scan(storage_source_parameters['time_to_scan'])

    # вычисляем итоговое количество файлов для ПА с этого источника
    storage_source_parameters['dynamic_load'] = ( math.ceil(
        storage_source_parameters['dynamic_load'] *
        storage_source_parameters['prefilter_cutoff'] *
        storage_source_parameters['cache_cutoff'])
    )

    # вычисляем необходимое количество ВМ для этого источника
    storage_source_parameters['vms_needed'] = math.ceil(storage_source_parameters['dynamic_load'] * storage_source_parameters['time_to_scan'] / 3600)

    # узнаем генерируемый объем дискового пространства экземляром источника в час
    if input_output.input_yes_no('Необходимо ли рассчитать объем генерируемого дискового пространства с этого источника?'):
        storage_source_parameters['generated_storage_size'] = get_generated_storage_size(storage_source_parameters['files'], storage_source_parameters['one_task_size'])

    return storage_source_parameters