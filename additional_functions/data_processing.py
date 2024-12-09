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
def generate_table(
        table_format: str,
        first_column_header: str,
        first_column_fields: list[str],
        list_of_data_dicts: list[dict],
        columns_name_key: str,
        columns_values_key: list[str]) -> str:
    """
    Функция создания таблицы из списка словарей.

    Параметры:
        table_format (str): Способ форматирования таблицы (fancy - для вывода в консоль или csv для записи в csv файл).
        first_column_header (str): Заголовок первого столбца в создаваемой таблице.
        first_column_fields (list[str]): Названия строк в таблице (значения первого столбца таблицы).
        list_of_data_dicts (list[dict]): Список словарей с данными, которыми будет заполнена таблица.
        columns_name_key (str): Ключ в словарях, значение которого будет использоваться для создания заголовков таблицы.
        columns_values_key (list[str]): Список ключей в словарях, значения которых будут использоваться для заполнения таблицы.

    Возвращает:
        str: Строка с таблицей в нужном формате.
    """

    #создание пустого словаря, в котором key - это название столбцов, а value - список значений (построчно)
    table_columns = {}
    table_columns[first_column_header] = first_column_fields
    
    #добавление каждого отдельно взятого словаря в текущий словарь для транспонирования
    for source_data_dict in list_of_data_dicts:
        table_columns[source_data_dict[columns_name_key]] = [source_data_dict[value] for value in columns_values_key] 

    #транспонирование данных
    transposed_table = list(zip(*table_columns.values()))
    
    #задание формата таблицы в csv или fancy
    if table_format == 'fancy':
        fancy_table = tabulate(transposed_table, headers=table_columns.keys(), tablefmt="fancy_grid")
        return fancy_table
    elif table_format == 'csv':
        #первая строка, заголовки
        csv_table = [list(table_columns.keys())]
        csv_table.extend(transposed_table)
        return csv_table