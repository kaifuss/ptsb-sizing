import json


#Функция импорта данных из json-файла. Принимает путь к файлу и имя json-объекта, data которого нужно вернуть
#Возвращает словарь полей из json-объекта
def load_data_from_json(json_file_path, json_object_name):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            return data[json_object_name]
    
    except json.JSONDecodeError:
        print(f"Ошибка при импорте JSON данных {json_object_name} из файла {json_file_path}. Проверьте синтаксис и данные.\nСкрипт остановлен.")
        exit()