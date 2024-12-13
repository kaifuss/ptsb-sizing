import json
from tabulate import tabulate


#Функция импорта данных из json-файла
def load_data_from_json(json_file_path: str, json_object_name: str) -> dict:
    """
    Функция импорта данных из json-файла. Принимает на вход путь к файлу и имя json-объекта, data которого нужно вернуть.

    Параметры:
        json_file_path (str): Путь к json-файлу.
        json_object_name (str): Имя json-объекта, data которого нужно вернуть.

    Возвращает:
        dict: Словарь, сформированный из json-объекта.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            return data[json_object_name]
    
    except json.JSONDecodeError:
        print(f"Ошибка при импорте JSON данных {json_object_name} из файла {json_file_path}. Проверьте синтаксис и данные.\nСкрипт остановлен.")
        exit()


# TODO валидация всех json файлов
def validate_json(json_file_path: str) -> bool:
    """
    Проверяет корректность заполенения json-файлов по умолчанию через попытку создать словарь.

    Параметры:
        json_file_path (str): Путь к json-файлу, содержащему объекты.

    Возвращает:
        bool: True, если json-файл корректен, иначе False.
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            json.load(json_file)
            return True
    except json.JSONDecodeError:
        return False


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
    

# функция создания уникальных имён для серверов
def prepare_servers_list(servers_list: list[dict]) -> list[str]:
    """
    Заменяет value "0" на "Не требуется" для каждого параметра серверов.
    Добавляет серверам порядковые имена для создания уникальных идентификаторов.

    Параметры:
        servers_list (list[dict]): Список словарей с данными о серверах.

    Возвращает:
        list[str]: Обновленный список словарей.
    """

    # уникальные имена для серверов
    for number, server in enumerate(servers_list, start=1):
        server['server_role'] = f"Сервер {number}\n{server.get('server_role')}"    
    # замена на "не требуется"
    for server in servers_list:
        for parameter, value in server.items():
            server[parameter] = "Не требуется" if value == 0 else value