from database.config_data import COLLECTION_SPECS_BODY, COLLECTION_TEMPLATE_BODY, COLLECTION_CITIES_BODY
from database.data import query_data_items


def get_specs_list_name_from_wix():
    """Получение списка наименований специализаций"""
    return [spec['data']['specializationName'] for spec in
            query_data_items(COLLECTION_SPECS_BODY)['dataItems']]


def get_specs_list_from_wix():
    """получение списка словарей специализация: id специализации"""
    return [{spec['data']['specializationName']: spec['id']} for spec in
            query_data_items(COLLECTION_SPECS_BODY)['dataItems']]


def get_specs_dict_from_wix():
    """Получение словаря специализация: id специализации"""
    return dict((k, v) for d in get_specs_list_from_wix() for k, v in d.items())


def clean_selected_specs():
    """Получение словаря специализаций с False вместо значений"""
    return {spec: False for spec in get_specs_dict_from_wix()}


def get_cities_list_name_from_wix():
    """Получение списка наименований городов"""
    return [city['data']['cityName'] for city in
            query_data_items(COLLECTION_CITIES_BODY)['dataItems']]


def get_cities_list_from_wix():
    """получение списка словарей город: id города"""
    return [{city['data']['cityName']: city['id']} for city in
            query_data_items(COLLECTION_CITIES_BODY)['dataItems']]


def get_cities_dict_from_wix():
    """Получение словаря город: id города"""
    return dict((k, v) for d in get_cities_list_from_wix() for k, v in d.items())


def clean_selected_cities():
    """Получение словаря городов с False вместо значений"""
    return {city: False for city in get_cities_dict_from_wix()}


def get_default_template_list_from_wix():
    """Получение списка словарей имя шаблоннного текста: шаблонное описание"""
    return [{template['data']['templateMessageName']: template['data']['templateMessageDescription']}
            for template in query_data_items(COLLECTION_TEMPLATE_BODY)['dataItems']]


def get_default_template_dict_from_wix(key):
    """Получение шаблонного описание по имени шаблона"""
    return dict((k, v) for d in get_default_template_list_from_wix() for k, v in d.items())[key]
