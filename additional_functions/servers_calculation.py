# встроенны библиотеки
import math
import os

# самописные функции
from additional_functions import input_output
from additional_functions import work_with_json

# путь к файлу с параметрами по-умолчанию
PATH_TO_DEFAULT_VALUES = 'default_values'
JSON_FILE_SERVERS_PARAMETERS = os.path.join(PATH_TO_DEFAULT_VALUES, 'servers_parameters.json')

# к-фт домонжения ГиБ в ГБ
GIB_MULTIPLIER = 1.074

#расчет ТХ сервера управления с вкл функцией ПА
def calculate_master_with_dynamic(vms_amount: int, iso_amount: int, storage_increment: int) -> dict:
    """
    Расчитывает параметры ТХ сервера управления с вкл функцией ПА по количеству запускаемых ВМ, количеству ISO образов и инкременту хранилища.

    Параметры:
        vms_amount (int): Количество ВМ на сервер управления с вкл функцией ПА.
        iso_amount (int): Количество ISO на всю инсталляцию.
        storage_increment (int): Надбавка к хранилищу для сервера управления с вкл функцией ПА.
    
    Возвращает:
        dict: Cловарь с параметрами ТХ сервера управления с вкл функцией ПА.
    """
    
    # импортируем параметры по умолчанию для сервера из json-объекта
    server_parameters = work_with_json.load_data_from_json(JSON_FILE_SERVERS_PARAMETERS, 'master_with_dynamic_parameters')
    # меняем описание сервера под актуальное число ВМ
    server_parameters['server_role'] = f"Сервер управления с функцией ПА\nКоличество ВМ: {vms_amount}"

    # V_root = (N_ВМ + 118)
    server_parameters['root_space'] = vms_amount + server_parameters['root_space']
    # V_opt = (N_ВМ + 15 * N_ISO + 43)
    server_parameters['opt_space'] = vms_amount + 15 * iso_amount + server_parameters['opt_space']
    # V_minio = (8 * N_ISO + 50 + storage_increment)
    server_parameters['minio_space'] = 8 * iso_amount + server_parameters['minio_space'] + storage_increment

    # рекомендация по домножению на 8% и на 1.074 для перевода из ГиБ в ГБ
    for partition in ['root_space', 'opt_space', 'minio_space', 'home_space']:
        server_parameters[partition] = math.ceil(server_parameters[partition] * server_parameters['part_multiplier'] * GIB_MULTIPLIER)

    # складываем изначальный размер ssd со всем, что было вычислено
    server_parameters['ssd_size'] = (
        server_parameters['ssd_size'] +
        server_parameters['root_space'] +
        server_parameters['opt_space']
    )
    # складываем изначальный размер hdd со всем, что было вычислено
    server_parameters['hdd_size'] = (
        server_parameters['hdd_size'] +
        server_parameters['minio_space'] +
        server_parameters['home_space']
    )

    # CPU Threads = 3 * N_ВМ + 9
    server_parameters['theads_amount'] = 3 * vms_amount + 9
    # RAM = (4 * N_ВМ + 19) * 1.074
    server_parameters['ram_amount'] = math.ceil((4 * vms_amount + 19) * 1.074)
    
    return server_parameters


#расчет ТХ сервера управления без функции ПА  
def calculate_master_without_dynamic(iso_amount: int, static_tasks: int, storage_increment: int) -> dict:
    """
    Расчитывает параметры ТХ сервера управления без ПА по параметрам количеству заданий в час, количеству ISO образов и инкременту хранилища.

    Параметры:
        iso_amount (int): Количество ISO на всю инсталляцию.
        static_tasks (int): Количество статических заданий в час на сервер управления без ПА.
        storage_increment (int): Надбавка к хранилищу для сохранения проверенных файлов.
    
    Возвращает:
        dict: Cловарь с параметрами ТХ сервера управления без ПА.
    """

    # импортируем параметры по умолчанию для сервера из json-объекта
    server_parameters = work_with_json.load_data_from_json(JSON_FILE_SERVERS_PARAMETERS, 'master_without_dynamic_parameters')

    # V_minio = 8 * N_ISO + 50
    server_parameters['minio_space'] = 8 * iso_amount + server_parameters['minio_space']

    # рекомендация по домножению на 8% и на 1.074 для перевода из ГиБ в ГБ
    for partition in ['root_space', 'opt_space', 'minio_space', 'home_space']:
        server_parameters[partition] = math.ceil(server_parameters[partition] * server_parameters['part_multiplier'] * GIB_MULTIPLIER)

    # складываем изначальный размер ssd со всем, что было вычислено
    server_parameters['ssd_size'] = (
        server_parameters['root_space'] +
        server_parameters['opt_space']
    )
    # складываем изначальный размер hdd со всем, что было вычислено
    server_parameters['hdd_size'] = (
        server_parameters['minio_space'] +
        server_parameters['home_space']
    )    
    
    # железо задаётся по количеству статических заданий (жесткая таблица от вендрора, формул расчета нет)
    ranges_of_static_tasks = [
        (0, 100, 4, 16),
        (100, 1_000, 6, 32),
        (1_000, 5_000, 10, 32),
        (5_000, 10_000, 15, 32),
        (10_000, float('inf'), 48, 64)
    ]
    for lower, upper, threads, ram in ranges_of_static_tasks:
        if lower <= static_tasks < upper:
            server_parameters['theads_amount'] = threads
            server_parameters['ram_amount'] = ram
            break
    
    return server_parameters


#расчет ТХ дополнительного сервера с функцией ПА
def calculate_additional_server_with_vms(vms_amount: int, iso_amount: int) -> dict:
    """
    Расчитывает параметры ТХ доп. сервера с функцией ПА по количеству запускаемых ВМ и количеству ISO образов.

    Параметры:
        vms_amount (int): Количество ВМ на этом доп. сервере с ПА.
        iso_amount (int): Количество ISO на всей инсталляции.
    
    Возвращает:
        dict: Обновленный словарь с параметрами ТХ доп. сервера с ПА.
    """

    # импортируем параметры по умолчанию для сервера из json-объекта
    server_parameters = work_with_json.load_data_from_json(JSON_FILE_SERVERS_PARAMETERS, 'additional_dynamic_parameters')
    # обновнляем название сервера под количество ВМ
    server_parameters['server_role'] = f"Дополнительный сервер с функцией ПА\nКоличество ВМ: {vms_amount}"

    # V_root = N_ВМ + 118
    server_parameters['root_space'] = vms_amount + server_parameters['root_space']
    # V_opt = N_ВМ + 15 * N_ISO - 2
    server_parameters['opt_space'] = vms_amount + 15 * iso_amount - 2

    # рекомендация по домножению на 8% и на 1.074 для перевода из ГиБ в ГБ
    for partition in ['root_space', 'opt_space', 'minio_space', 'home_space']:
        server_parameters[partition] = math.ceil(server_parameters[partition] * server_parameters['part_multiplier'] * GIB_MULTIPLIER)

    # складываем изначальный размер ssd со всем, что было вычислено
    server_parameters['ssd_size'] = (
        server_parameters['root_space'] +
        server_parameters['opt_space']
    )
    # складываем изначальный размер hdd со всем, что было вычислено
    server_parameters['hdd_size'] = (
        server_parameters['minio_space'] +
        server_parameters['home_space']
    )
    
    # Threads = 3 * N_ВМ + 4
    server_parameters['theads_amount'] = 3 * vms_amount + 4
    # RAM = 4 * N_ВМ + 5
    server_parameters['ram_amount'] = math.ceil((vms_amount * 4 + 5) * 1.074)
    
    return server_parameters


#TODO переписать?
#расчет всех доп серверов с динамикой
def get_all_additional_servers(vms_all: int, vms_per_server: int, iso_amount: int) -> list[dict]:
    """
    Создает необходимое количество доп. серверов динамики по известной, либо вводимой нагрузке.

    Параметры:
        vms_all (int): Общее количество ВМ, которые относятся к серверам динамики.
        vms_per_server (int): Количество ВМ на один доп. сервер.
        iso_amount (int): Количество ISO на всю инсталляцию.

    Возвращает:
        list[dict]: Список словарей с параметрами всех дополнительных серверов динамики.
    """

    # создаем лист для хранения будущих серверов и узнаем необходимое количество таких серверочков
    dynamic_servers_list = []
    dynamic_servers_amount = math.ceil(vms_all / vms_per_server)

    input_output.print_header('Расчет ТХ для всех доп. серверов динамики')
    calculation_choise = input_output.input_choise_digit(
        f"1. Расчет ТХ для {dynamic_servers_amount} доп серверов(-а) под общее количество ВМ {vms_all} (не более {vms_per_server} ВМ на сервер)\n"
        '2. Вручную ввести количество дополнительных серверов и количество ВМ для каждого сервера', 2
    )

    # расчет красиво автоматически под общее количество ВМ на все доп. сервера. количество серверов также автоматически
    if calculation_choise == 1:
        vms_left = vms_all
        while (vms_left > 0):
            if (vms_left > vms_per_server):
                dynamic_servers_list.append(calculate_additional_server_with_vms(vms_per_server, iso_amount))
            else:
                dynamic_servers_list.append(calculate_additional_server_with_vms(vms_left, iso_amount))
            vms_left -= vms_per_server
    # расчет некрасиво, на основании того, что юзверь введет сам
    elif calculation_choise == 2:
        input_output.print_header('Ручная конфигурация доп. серверов динамики', 2)
        dynamic_servers_amount = input_output.input_integer_number('Введите количество дополнительных серверов: ')
        for i in range(dynamic_servers_amount):
            vms_amount = input_output.input_integer_number(f"Введите количество ВМ для {i+1}-го доп. сервера динамики: ")
            dynamic_servers_list.append(calculate_additional_server_with_vms(vms_amount, iso_amount))
    
    return dynamic_servers_list