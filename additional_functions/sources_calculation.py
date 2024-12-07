import math

#получить % отсечки для ПА для любого источника
def get_dynamic_cutoff(default_value):
    dynamic_cutoff = input_integer_number(f"Введите примерный % заданий от общего количества, которые пойдут на динамический анализ (по умолчанию - {default_value}%): ")
    dynamic_cutoff = float(dynamic_cutoff) / 100 if dynamic_cutoff is not None else default_value / 100
    return dynamic_cutoff

#получить % отсечки по префильтру для любого источника
def get_prefilter_cutoff(default_value):
    prefilter_cutoff = input_integer_number(f"Введите примерный % заданий от заданий ПА, которые останутся после префильтрации (по умолчанию - {default_value}%): ")
    prefilter_cutoff = float(prefilter_cutoff) / 100 if prefilter_cutoff is not None else default_value / 100
    return prefilter_cutoff

#получить % отсечки по кэшированию для любого источника
def get_cache_cutoff(default_value):
    cache_cutoff = input_integer_number(f"Введите примерный % заданий от заданий ПА, которые останутся после отброса кэшированием (по умолчанию - {default_value }%): ")
    cache_cutoff = float(cache_cutoff) / 100 if cache_cutoff is not None else default_value / 100
    return cache_cutoff

#получить время сканирования для любого источника
def get_time_to_scan(default_value):
    input_scan_time = input_integer_number(f"Введите время в секундах, как долго будут сканироваться задания с этого источника (по умолчанию - {default_value}): ")
    input_scan_time = input_scan_time if input_scan_time is not None else default_value
    return input_scan_time

#расчет нагрузки с почтового трафика
def get_smtp_load(smtp_load_parameters):
    
    #Если количество писем в час - неизвестно, то расчет идет от количества пользователей.
    if smtp_load_parameters['mails'] == 0:
        # количество писем в час - неизвестно
        input_users_multiplier = input_integer_number(
            f"Ввведите количество писем на 1 пользователя (по умолчанию - {smtp_load_parameters['users_multiplier']}): "
        )
        smtp_load_parameters['users_multiplier'] = input_users_multiplier or smtp_load_parameters['users_multiplier']
        smtp_load_parameters['mails'] = smtp_load_parameters['users'] * smtp_load_parameters['users_multiplier']

        # процент писем с вложениями
        input_mails_with_attachments = input_integer_number(
            'Введите примерный % писем от общего количества, которые предположительно содержат вложения '
            f"(по умолчанию - {smtp_load_parameters['mails_with_attachments']}%): "
        )
        smtp_load_parameters['mails_with_attachments'] = math.ceil(
            smtp_load_parameters['mails'] *
            float(input_mails_with_attachments or smtp_load_parameters['mails_with_attachments']) / 100.0
        )
    else:
        # количество писем в час - известно
        if input_yes_no('Известно ли количетсво писем в час, содержащих вложения?'):
            # количество писем с вложениями - известно
            smtp_load_parameters['mails_with_attachments'] = input_integer_number(
                'Введите количество писем в час, которые содержат вложения: '
            )
        else:
            # количество писем с вложениями - неизвестно
            input_mails_with_attachments = input_integer_number(
                'Введите примерный % писем от общего количества, которые предположительно содержат вложения '
                f"(по умолчанию - {smtp_load_parameters['mails_with_attachments']}%): "
            )
            smtp_load_parameters['mails_with_attachments'] = math.ceil(
                smtp_load_parameters['mails'] *
                float(input_mails_with_attachments or smtp_load_parameters['mails_with_attachments']) / 100.0
            )

    input_attachments_per_mail = input_integer_number(
        'Введите количество вложений на 1 письмо, содержащее вложения '
        f"(по умолчанию - {smtp_load_parameters['attachments_per_mail']}): "
    )
    smtp_load_parameters['attachments_per_mail'] = input_attachments_per_mail or smtp_load_parameters['attachments_per_mail']
    
    smtp_load_parameters['dynamic_cutoff'] = get_dynamic_cutoff(smtp_load_parameters['dynamic_cutoff'])
    smtp_load_parameters['prefilter_cutoff'] = get_prefilter_cutoff(smtp_load_parameters['prefilter_cutoff'])
    smtp_load_parameters['cache_cutoff'] = get_cache_cutoff(smtp_load_parameters['cache_cutoff'])
    smtp_load_parameters['time_to_scan'] = get_time_to_scan(smtp_load_parameters['time_to_scan'])

    smtp_load_parameters['dynamic_load'] = ( math.ceil(
        smtp_load_parameters['mails_with_attachments'] *
        smtp_load_parameters['attachments_per_mail'] *
        smtp_load_parameters['dynamic_cutoff'] *
        smtp_load_parameters['prefilter_cutoff'] *
        smtp_load_parameters['cache_cutoff'])
    )
    smtp_load_parameters['vms_needed'] = math.ceil(smtp_load_parameters['dynamic_load'] * smtp_load_parameters['time_to_scan'] / 3600)
    
    return smtp_load_parameters

#расчет нагрузки с ICAP
def get_icap_load(icap_load_parameters):

    icap_load_parameters['dynamic_cutoff'] = get_dynamic_cutoff(icap_load_parameters['dynamic_cutoff'])
    icap_load_parameters['prefilter_cutoff'] = get_prefilter_cutoff(icap_load_parameters['prefilter_cutoff'])
    icap_load_parameters['cache_cutoff'] = get_cache_cutoff(icap_load_parameters['cache_cutoff'])
    icap_load_parameters['time_to_scan'] = get_time_to_scan(icap_load_parameters['time_to_scan'])

    if icap_load_parameters['files'] == 0:
        icap_load_parameters['files'] = math.ceil( (7000 * icap_load_parameters['speed']) / 1024 )
    
    icap_load_parameters['dynamic_load'] = ( math.ceil(
        icap_load_parameters['files'] *
        icap_load_parameters['dynamic_cutoff'] *
        icap_load_parameters['prefilter_cutoff'] *
        icap_load_parameters['cache_cutoff'])
    )
    icap_load_parameters['vms_needed'] = math.ceil(icap_load_parameters['dynamic_load'] * icap_load_parameters['time_to_scan'] / 3600)    
    
    return icap_load_parameters

#расчет нагрузки с MP 10 EDR
def get_edr_load(edr_load_parameters):
    
    if edr_load_parameters['files'] == 0:
        agents_multiplier = input_integer_number(f"Введите примерное количество файлов с 1 агента edr (по умолчанию - {edr_load_parameters['agents_multiplier']}): ")
        edr_load_parameters['agents_multiplier'] = agents_multiplier or edr_load_parameters['agents_multiplier']
        edr_load_parameters['files'] = edr_load_parameters['agents'] * edr_load_parameters ['agents_multiplier']    

    edr_load_parameters['dynamic_cutoff'] = get_dynamic_cutoff(edr_load_parameters['dynamic_cutoff'])
    edr_load_parameters['prefilter_cutoff'] = get_prefilter_cutoff(edr_load_parameters['prefilter_cutoff'])
    edr_load_parameters['cache_cutoff'] = get_cache_cutoff(edr_load_parameters['cache_cutoff'])
    edr_load_parameters['time_to_scan'] = get_time_to_scan(edr_load_parameters['time_to_scan'])

    edr_load_parameters['dynamic_load'] = ( math.ceil(
        edr_load_parameters['files'] *
        edr_load_parameters['dynamic_cutoff'] *
        edr_load_parameters['prefilter_cutoff'] *
        edr_load_parameters['cache_cutoff'])
    )
    edr_load_parameters['vms_needed'] = math.ceil(edr_load_parameters['dynamic_load'] * edr_load_parameters['time_to_scan'] / 3600)  
    
    return edr_load_parameters

#расчет нагрузки с API-источника с выбранными параметрами проверки
def get_automated_api_load(automated_api_load_parameters):

    automated_api_load_parameters['dynamic_cutoff'] = get_dynamic_cutoff(automated_api_load_parameters['dynamic_cutoff'])
    automated_api_load_parameters['prefilter_cutoff'] = get_prefilter_cutoff(automated_api_load_parameters['prefilter_cutoff'])
    automated_api_load_parameters['cache_cutoff'] = get_cache_cutoff(automated_api_load_parameters['cache_cutoff'])
    automated_api_load_parameters['time_to_scan'] = get_time_to_scan(automated_api_load_parameters['time_to_scan'])

    automated_api_load_parameters['dynamic_load'] = ( math.ceil(
        automated_api_load_parameters['files'] *
        automated_api_load_parameters['dynamic_cutoff'] *
        automated_api_load_parameters['prefilter_cutoff'] *
        automated_api_load_parameters['cache_cutoff'])
    )
    automated_api_load_parameters['vms_needed'] = math.ceil(automated_api_load_parameters['dynamic_load'] * automated_api_load_parameters['time_to_scan'] / 3600) 

    return automated_api_load_parameters

#расчет нагрузки с API-источника с ручными параметрами проверки
def get_manual_api_load(manual_api_load_parameters):

    manual_api_load_parameters['dynamic_cutoff'] = get_dynamic_cutoff(manual_api_load_parameters['dynamic_cutoff'])
    manual_api_load_parameters['cache_cutoff'] = get_cache_cutoff(manual_api_load_parameters['cache_cutoff'])
    manual_api_load_parameters['time_to_scan'] = get_time_to_scan(manual_api_load_parameters['time_to_scan'])

    manual_api_load_parameters['dynamic_load'] = ( math.ceil(
        manual_api_load_parameters['files'] *
        manual_api_load_parameters['dynamic_cutoff'] *
        manual_api_load_parameters['cache_cutoff'])
    )
    manual_api_load_parameters['vms_needed'] = math.ceil(manual_api_load_parameters['dynamic_load'] * manual_api_load_parameters['time_to_scan'] / 3600) 
    
    return manual_api_load_parameters

#расчет нагрузки с хранилища файлов
def get_storage_load(storage_load_parameters):
    storage_load_parameters['prefilter_cutoff'] = get_prefilter_cutoff(storage_load_parameters['prefilter_cutoff'])
    storage_load_parameters['cache_cutoff'] = get_cache_cutoff(storage_load_parameters['cache_cutoff'])
    storage_load_parameters['time_to_scan'] = get_time_to_scan(storage_load_parameters['time_to_scan'])

    storage_load_parameters['dynamic_load'] = ( math.ceil(
        storage_load_parameters['dynamic_load'] *
        storage_load_parameters['prefilter_cutoff'] *
        storage_load_parameters['cache_cutoff'])
    )
    storage_load_parameters['vms_needed'] = math.ceil(storage_load_parameters['dynamic_load'] * storage_load_parameters['time_to_scan'] / 3600)

    return storage_load_parameters