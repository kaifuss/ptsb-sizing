from tabulate import tabulate

# функция для фильтрации данных источников (словарей) по указанным полям
def filter_source_dict_fields(source: dict, fields_for_filter: list) -> dict:
    """
    Функция фильтрует словарь источника по указанным полям, удаляя все остальные. 

    Параметры:
        source (dict): Источник, который нужно отфильтровать, хранимый в словаре.
        fields_for_filter (list): Список полей для фильтрации.

    Возвращает:
        dict: Обновленный словарь источника. С теми полями, которые были указаны в fields_for_filter.
    """

    return {field: source[field] for field in fields_for_filter}


#генерация таблиц в TXT и CSV форматах на основании списка словарей
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