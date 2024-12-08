from tabulate import tabulate

def transpose_table(data, fields):
    # Создаем заголовок таблицы: первая колонка - названия полей, остальные - имена источников
    headers = ["Field"] + [d["name"] for d in data]

    # Извлекаем значения для каждого поля и источника
    transposed_data = [[field] + [d[field] for d in data] for field in fields]

    return tabulate(transposed_data, headers=headers, tablefmt="fancy_grid")

def generate_table(
        table_format: str,
        first_column_header: str,
        first_column_fields: list[str],
        list_of_data_dicts: list[dict],
        fields: list[str]):
    
    #создание пустого словаря, в котором key - это название столбцов, а value - список значений (построчно)
    transposed_data = {}
    transposed_data[first_column_header] = first_column_fields
    
    #добавление каждого отдельно взятого словаря в текущий словарь для транспонирования
    for each_dict in list_of_data_dicts:
        transposed_data[each_dict['name']] = [each_dict[field] for field in fields] 

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

print(generate_table(table_format, first_column_header, names_of_rows, data_dicts, fields_to_display))
