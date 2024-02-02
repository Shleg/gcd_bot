import logging

import requests

from database.config_data import *

HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': WIX_API_TOKEN,
    'wix-site-id': WIX_SITE_ID
}


# Функция готова
def insert_data_item(request_body, headers=None):
    if headers is None:
        headers = HEADERS
    url = 'https://www.wixapis.com/wix-data/v2/items'

    # Отправляем POST-запрос
    response = requests.post(url, headers=headers, json=request_body)

    # Проверяем статус ответа
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}, {response.text}")


# Функция готова
def update_data_item(request_body, dataItem_id, headers=None):
    if headers is None:
        headers = HEADERS
    url = f'https://www.wixapis.com/wix-data/v2/items/{dataItem_id}'

    # Отправляем PUT-запрос
    response = requests.put(url, headers=headers, json=request_body)

    # Проверяем статус ответа
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}, {response.text}")


# Функция готова
def save_data_item(request_body, headers=None):
    if headers is None:
        headers = HEADERS
    url = 'https://www.wixapis.com/wix-data/v2/items/save'

    # Отправляем POST-запрос
    response = requests.post(url, headers=headers, json=request_body)

    # Проверяем статус ответа
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}, {response.text}")


# Функция готова
def get_data_item(data_collection_id, dataItem_id, headers=None):
    if headers is None:
        headers = HEADERS
    url = f'https://www.wixapis.com/wix-data/v2/items/{dataItem_id}?dataCollectionId={data_collection_id}'

    # Отправляем GET-запрос
    response = requests.get(url, headers=headers)

    # Проверяем статус ответа
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}, {response.text}")


# Функция готова
def remove_data_item(request_body, data_item_id, headers=None):
    if headers is None:
        headers = HEADERS
    url = f'https://www.wixapis.com/wix-data/v2/items/{data_item_id}'

    # Отправляем DELETE-запрос
    response = requests.delete(url, headers=headers, json=request_body)

    # Проверяем статус ответа
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}, {response.text}")


# Функция готова
def query_data_items(request_body, headers=None):
    try:
        if headers is None:
            headers = HEADERS
        url = 'https://www.wixapis.com/wix-data/v2/items/query'

        # Отправляем POST-запрос
        response = requests.post(url, headers=headers, json=request_body)

        # Проверяем статус ответа
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            logging.error(f"Ошибка в функции query_data_items: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        logging.exception("An error occurred while querying data items.")
        return None


# Функция готова
def query_referenced_data_items(request_body, headers=None):
    if headers is None:
        headers = HEADERS
    url = 'https://www.wixapis.com/wix-data/v2/items/query-referenced'

    # Отправляем POST-запрос
    response = requests.post(url, headers=headers, json=request_body)

    # Проверяем статус ответа
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}, {response.text}")


# Функция готова
def is_referenced_data_item(request_body, headers=None):
    if headers is None:
        headers = HEADERS
    url = 'https://www.wixapis.com/wix-data/v2/items/is-referenced'

    # Отправляем POST-запрос
    response = requests.post(url, headers=headers, json=request_body)

    # Проверяем статус ответа
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}, {response.text}")


# Функция готова
def insert_data_item_reference(request_body, headers=None):
    if headers is None:
        headers = HEADERS
    url = 'https://www.wixapis.com/wix-data/v2/items/insert-reference'

    # Отправляем POST-запрос
    response = requests.post(url, headers=headers, json=request_body)

    # Проверяем статус ответа
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}, {response.text}")


def replace_data_item_reference(request_body, headers=None):
    if headers is None:
        headers = HEADERS
    url = 'https://www.wixapis.com/wix-data/v2/items/replace-references'

    # Отправляем POST-запрос
    response = requests.post(url, headers=headers, json=request_body)

    # Проверяем статус ответа
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}, {response.text}")


# Функция готова, в теле запроса нужно передать список референсных полей
def query_full_data_item(request_body, headers=None):
    if headers is None:
        headers = HEADERS
    url = 'https://www.wixapis.com/wix-data/v2/items/query'

    # Отправляем POST-запрос
    response = requests.post(url, headers=headers, json=request_body)

    # Проверяем статус ответа
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code}, {response.text}")


# DEFAULT_ROLE = [role['data']['roleName'] for role in query_data_items(COLLECTION_ROLES_BODY)['dataItems']]
DEFAULT_ROLE_LIST = [{role['data']['roleName']: role['id']} for role in
                     query_data_items(COLLECTION_ROLES_BODY)['dataItems']]
DEFAULT_ROLE_DICT = dict((k, v) for d in DEFAULT_ROLE_LIST for k, v in d.items())

# DEFAULT_SPEC = [spec['data']['specializationName'] for spec in query_data_items(COLLECTION_SPECS_BODY)['dataItems']]
DEFAULT_SPEC_LIST = [{spec['data']['specializationName']: spec['id']} for spec in
                     query_data_items(COLLECTION_SPECS_BODY)['dataItems']]
DEFAULT_SPEC_DICT = dict((k, v) for d in DEFAULT_SPEC_LIST for k, v in d.items())

# DEFAULT_CITIES = [city['data']['cityName'] for city in query_data_items(COLLECTION_CITIES_BODY)['dataItems']]
DEFAULT_CITIES_LIST = [{city['data']['cityName']: city['id']} for city in
                       query_data_items(COLLECTION_CITIES_BODY)['dataItems']]
DEFAULT_CITY_DICT = dict((k, v) for d in DEFAULT_CITIES_LIST for k, v in d.items())

# DEFAULT_RESEARCH = [research['data']['clinicalStudiesName'] for research in query_data_items(COLLECTION_RESEARCHES_BODY)['dataItems']]
DEFAULT_RESEARCH_LIST = [{research['data']['clinicalStudiesName']: research['id']} for research in
                         query_data_items(COLLECTION_RESEARCHES_BODY)['dataItems']]
DEFAULT_RESEARCH_DICT = dict((k, v) for d in DEFAULT_RESEARCH_LIST for k, v in d.items())

# DEFAULT_PHASES = [phase['data']['researchPhasesName'] for phase in query_data_items(COLLECTION_PHASES_BODY)['dataItems']]
DEFAULT_PHASES_LIST = [{phase['data']['researchPhasesName']: phase['id']} for phase in
                       query_data_items(COLLECTION_PHASES_BODY)['dataItems']]
DEFAULT_PHASES_DICT = dict((k, v) for d in DEFAULT_PHASES_LIST for k, v in d.items())

# DEFAULT_DRUGS = [drug['data']['drugGroupsName'] for drug in query_data_items(COLLECTION_DRUGS_BODY)['dataItems']]
DEFAULT_DRUGS_LIST = [{drug['data']['drugGroupsName']: drug['id']} for drug in
                      query_data_items(COLLECTION_DRUGS_BODY)['dataItems']]
DEFAULT_DRUGS_DICT = dict((k, v) for d in DEFAULT_DRUGS_LIST for k, v in d.items())

# DEFAULT_METHODS = [method['data']['contactPreferencesName'] for method in query_data_items(COLLECTION_METHODS_BODY)['dataItems']]
DEFAULT_METHODS_LIST = [{method['data']['contactPreferencesName']: method['id']} for method in
                        query_data_items(COLLECTION_METHODS_BODY)['dataItems']]
DEFAULT_METHODS_DICT = dict((k, v) for d in DEFAULT_METHODS_LIST for k, v in d.items())

test = query_data_items(COLLECTION_TEMPLATE_BODY)['dataItems']


# DEFAULT_TEMPLATE_LIST = [{template['data']['templateMessageName']: template['data']['templateMessageDescription']} for
#                          template in query_data_items(COLLECTION_TEMPLATE_BODY)['dataItems']]


# DEFAULT_TEMPLATE_DICT = dict((k, v) for d in DEFAULT_METHODS_LIST for k, v in d.items())

def generate_template_dict():
    for template in query_data_items(COLLECTION_TEMPLATE_BODY)['dataItems']:
        yield {template['data']['templateMessageName']: template['data']['templateMessageDescription']}


DEFAULT_TEMPLATE_DICT = dict((k, v) for d in generate_template_dict() for k, v in d.items())
