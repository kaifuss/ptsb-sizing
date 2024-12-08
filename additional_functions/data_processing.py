

# функция для фильтрации данных источников
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