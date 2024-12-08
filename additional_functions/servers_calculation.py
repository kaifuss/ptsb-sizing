import math
import input_output
import work_with_json


#расчет ТХ сервера управления с вкл функцией ПА
def calculate_master_with_dynamic(server_parameters: dict, vms_amount: int, iso_amount: int) -> dict:
    """
    Расчитывает параметры ТХ сервера управления с вкл функцией ПА по параметрам vms_amount и iso_amount

    Параметры:
        server_parameters (dict): Словарь с параметрами ТХ по-умолчанию сервера управления с вкл функцией ПА.
        vms_amount (int): Количество ВМ на сервер управления с вкл функцией ПА.
        iso_amount (int): Количество ISO на сервер управления с вкл функцией ПА.
    
    Возвращает:
        dict: Обновленный словарь с параметрами ТХ сервера управления с вкл функцией ПА.
    """

    # меняем описание сервера под актуальное число ВМ
    server_parameters['server_role'] = f"Сервер управления с функцией ПА\nКоличество ВМ: {vms_amount}"

    # V_root = N_ВМ + 118
    server_parameters['root_space'] = math.ceil((vms_amount + server_parameters['root_space']) * 1.074)
    
    # V_opt = N_ВМ + 15 * N_ISO + 43
    server_parameters['opt_space'] = math.ceil((vms_amount + 15 * iso_amount + server_parameters['opt_space']) * 1.074)

    # V_minio = 8 * N_ISO + 50
    server_parameters['minio_space'] = math.ceil((8 * iso_amount + server_parameters['minio_space']) * 1.074)
    
    # рекомендация по домножению на 8%
    for key in ['root_space', 'opt_space', 'minio_space', 'home_space']:
        server_parameters[key] = math.ceil(server_parameters[key] * server_parameters['part_multiplier'])

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

    # RAM = 4 * N_ВМ + 19
    server_parameters['ram_amount'] = math.ceil((4 * vms_amount + 19) * 1.074)
    
    return server_parameters


#расчет ТХ сервера управления без функции ПА  
def calculate_master_without_dynamic(server_parameters: dict, iso_amount: int, static_tasks: int) -> dict:
    """
    Расчитывает параметры ТХ сервера управления без ПА по параметрам iso_amount и static_tasks

    Параметры:
        server_parameters (dict): Словарь с параметрами ТХ по-умолчанию сервера управления без ПА.
        iso_amount (int): Количество ISO на сервер управления с вкл функцией ПА.
        static_tasks (int): Количество статических заданий в час на сервер управления без ПА.
    
    Возвращает:
        dict: Обновленный словарь с параметрами ТХ сервера управления без ПА.
    """

    # V_minio = 8 * N_ISO + 50
    server_parameters['minio_space'] = math.ceil((8 * iso_amount + server_parameters['minio_space']) * 1.074)

    # рекомендация по домножению на 8%
    for key in ['root_space', 'opt_space', 'minio_space', 'home_space']:
        server_parameters[key] = math.ceil(server_parameters[key] * server_parameters['part_multiplier'])

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
    if static_tasks < 100:
        server_parameters['theads_amount'] = 4
        server_parameters['ram_amount'] = 16
    elif (static_tasks >= 100 ) and (static_tasks < 1_000):
        server_parameters['theads_amount'] = 6
        server_parameters['ram_amount'] = 32
    elif (static_tasks >= 1_000) and (static_tasks < 5_000):
        server_parameters['theads_amount'] = 10
        server_parameters['ram_amount'] = 32
    elif (static_tasks >= 5_000) and (static_tasks < 10_000):
        server_parameters['theads_amount'] = 15
        server_parameters['ram_amount'] = 32
    elif (static_tasks >= 10_000):
        server_parameters['theads_amount'] = 48
        server_parameters['ram_amount'] = 64
    
    return server_parameters


#расчет ТХ дополнительного сервера с функцией ПА
def calculate_additional_server_with_vms(server_parameters: dict, vms_amount: int, iso_amount: int) -> dict:
    """
    Расчитывает параметры ТХ доп. сервера с функцией ПА по параметрам vms_amount и iso_amount.

    Параметры:
        server_parameters (dict): Словарь с параметрами ТХ по-умолчанию доп. сервера с ПА.
        vms_amount (int): Количество ВМ на этом доп. сервере с ПА.
        iso_amount (int): Количество ISO на всей инсталляции.
    
    Возвращает:
        dict: Обновленный словарь с параметрами ТХ доп. сервера с ПА.
    """

    # обновнляем название сервера под количество ВМ
    server_parameters['server_role'] = f"Дополнительный сервер с функцией ПА\nКоличество ВМ: {vms_amount}"

    # V_root = N_ВМ + 118
    server_parameters['root_space'] = math.ceil((vms_amount + server_parameters['root_space']) * 1.074)
    
    # V_opt = N_ВМ + 15 * N_ISO - 2
    server_parameters['opt_space'] = math.ceil((vms_amount + 15 * iso_amount - 2) * 1.074)
    
    # рекомендация по домножению на 8%
    for key in ['root_space', 'opt_space', 'minio_space', 'home_space']:
        server_parameters[key] = math.ceil(server_parameters[key] * server_parameters['part_multiplier'])

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