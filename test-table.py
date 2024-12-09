from tabulate import tabulate
import csv

def generate_table(
        table_format: str,
        first_column_header: str,
        first_column_fields: list[str],
        list_of_data_dicts: list[dict],
        columns_name_key: str,
        columns_values_key: list[str]):
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


# Пример использования
data_dicts = [
    {'name': 'SMTP-источник №1', 'files': 10000, 'dynamic_load': 272, 'time_to_scan': 150, 'vms_needed': 12},
    {'name': 'SMTP-источник №2', 'files': 3702, 'dynamic_load': 13, 'time_to_scan': 150, 'vms_needed': 1},
    {'name': 'SMTP-источник №3', 'files': 30000, 'dynamic_load': 102, 'time_to_scan': 150, 'vms_needed': 5},
    {'name': 'ICAP-источник №1', 'files': 47852, 'dynamic_load': 958, 'time_to_scan': 150, 'vms_needed': 40},
    {'name': 'ICAP-источник №2', 'files': 45801, 'dynamic_load': 7787, 'time_to_scan': 150, 'vms_needed': 325},
]


table_format = 'fancy'
first_column_header = 'Показатели источников'
names_of_rows = ['Статических заданий,\nв час', 'Динамических заданий,\nв час', 'Время сканирования\n1 файла, в секундах', 'Нужно ВМ на этот источник']
fields_to_display = ['files', 'dynamic_load', 'time_to_scan', 'vms_needed']
unic_name_from_dicts = 'name'

print(generate_table(table_format, first_column_header, names_of_rows, data_dicts, unic_name_from_dicts, fields_to_display))

exit()

with open('output.csv', mode='w', newline= '', encoding='windows-1251') as file:
    writer = csv.writer(file, delimiter=';')
    writer.writerows(generate_table(table_format, first_column_header, names_of_rows, data_dicts, unic_name_from_dicts, fields_to_display))
