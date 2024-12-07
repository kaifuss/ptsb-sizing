# -*- coding: utf-8 -*-
print('''
╔═══════════════════════════════════════════════════════════════════════════╗
║                                  WELCOME                                  ║
║                              PTSB sizing tool                             ║
║                          by @github.com/kaifuss/                          ║
╚═══════════════════════════════════════════════════════════════════════════╝
''')


import csv
import math
import json
import os
from tabulate import tabulate

from additional_functions import input_output, servers_calculation, sources_calculation


#GLOBALS
#Цветовые коды
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RESET = '\033[0m'  #сброс на дефолт

#Константы параметров вывода
TXT_OUTPUT_ENCODING = 'utf-8'
CSV_OUTPUT_ENCODING = 'windows-1251'
CSV_OUTPUT_DELIMITER = ';'
CSV_OUTPUT_NEWLINE = ''

#Константы JSON файлов с конфигурацией
PATH_TO_DEFAULT_VALUES = 'default_values'
json_file_installation_parameters = os.path.join(PATH_TO_DEFAULT_VALUES, 'installation_parameters.json')
json_file_sources_parameters = os.path.join(PATH_TO_DEFAULT_VALUES, 'sources_parameters.json')
json_file_servers_parameters = os.path.join(PATH_TO_DEFAULT_VALUES, 'servers_parameters.json')


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


#INT MAIN
if __name__ == '__main__':
    
    servers_list = []   #лист для хранения всех объектов dict(), содержащих конфигурацию серверов
    sources_list = []   #лист для хранения всех объектов dict(), содержащих конфигурацию источников

    #имя output файлов с конфигурацией
    txt_file_name = 'config.txt'    
    csv_file_name = 'config.csv'

    #импорт данных по умолчанию из json-файлов в словари
    #параметры всей конфигурации целиком
    installation_parameters = load_data_from_json(json_file_installation_parameters, 'installation_parameters')
    
    #параметры источников
    smtp_load_parameters = load_data_from_json(json_file_sources_parameters, 'smtp_load_parameters')
    icap_load_parameters = load_data_from_json(json_file_sources_parameters, 'icap_load_parameters')
    edr_load_parameters = load_data_from_json(json_file_sources_parameters, 'edr_load_parameters')
    automated_api_load_parameters = load_data_from_json(json_file_sources_parameters, 'automated_api_load_parameters')
    manual_api_load_parameters = load_data_from_json(json_file_sources_parameters, 'manual_api_load_parameters')
    storage_load_parameters = load_data_from_json(json_file_sources_parameters, 'storage_load_parameters')

    print(edr_load_parameters)