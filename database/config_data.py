import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

BOT_FORM = 'https://www.gcd-russia.com/botselect'

WIX_API_TOKEN = os.getenv("WIX_API_TOKEN")
WIX_SITE_ID = os.getenv("WIX_SITE_ID")


# Описание коллекции Пользователи
COLLECTION_USERS = 'botUsers'
COLLECTION_USERS_BODY = {
    "dataCollectionId": COLLECTION_USERS
}
# Описание полей коллекции Пользователи
USER_TG_NAME = 'tgName'  # text
USER_ROLE_IDs = 'idUserRoles'  # reference
USER_CHAT_ID = 'tgChatId'  # text
USER_SPEC_IDs = 'specializationId'  # multi-reference
USER_CITY_ID = 'cityId'  # reference
USER_NAME = 'doctorName'  # text
USER_CONTACT_INFO = 'contactInfo'  # text
USER_PREF_CONTACT = 'contactPreferencesId'  # reference
USER_RESEARCH_IDs = 'clinicalStudiesIds'  # multi-reference
USER_STATE = 'newField'  # multi-reference

# Описание таблицы Роли пользователей
COLLECTION_ROLES = 'botUserRoles'
COLLECTION_ROLES_BODY = {
    "dataCollectionId": COLLECTION_ROLES
}
ROLE_NAME = 'roleName'  # text
ROLE_DESCRIPTION = 'roleDescription'  # text
ROLE_NAME_LATIN = 'roleNameLatin'  # text

ROLE_REFERAL = 'Врач-реферал'
ROLE_REFERAL_ID = 'e18b7220-272f-402b-8f09-674d426df9e9'
ROLE_RESEARCHER = 'Врач-исследователь'
ROLE_RESEARCHER_ID = '813296b0-dc24-45cf-84d7-eb81b9173a1c'

# Описание таблицы Специализации пользователей
COLLECTION_SPEC = 'botSpecializationsCatalog'
COLLECTION_SPECS_BODY = {
    "dataCollectionId": COLLECTION_SPEC
}
SPEC_NAME = 'specializationName'  # text
SPEC_ID = 'botUsers-specializationId'  # text

# Описание коллекции Города
COLLECTION_CITY = 'botCitiesCatalog'
COLLECTION_CITIES_BODY = {
    "dataCollectionId": COLLECTION_CITY
}
# Описание полей коллекции Города
CITY_NAME = 'cityName'


# Описание коллекции Клинические исследования
COLLECTION_RESEARCHES = 'botClinicalStudiesLeads'
COLLECTION_RESEARCHES_BODY = {
    "dataCollectionId": COLLECTION_RESEARCHES,
    "query": {
        "filter": {
            "isModerationApproved": True,
        }
    },
    "includeReferencedItems": ['specializationsId', 'citiyId', 'researcherDoctorId']
}

RESEARCH_NAME = 'clinicalStudiesName'
RESEARCH_DOCTOR_ID = 'researcherDoctorId'
RESEARCH_SPEC_ID = 'specializationsId'
RESEARCH_CITY_ID = 'citiyId'
RESEARCH_DIAG_NAME = 'diagnosisName'
RESEARCH_CRITERIA_DESC = 'researchCriteriaDescription'
RESEARCH_CONDITION_IDS = 'studyConditionId'
RESEARCH_PHASE_IDS = 'researchPhaseId'
RESEARCHES_DRUGS = 'drugGroupId'
# isModerationApproved
# botUsers-clinicalStudiesIds

# Описание коллекции Фазы исследований
COLLECTION_PHASES = 'botResearchPhasesCatalog'
COLLECTION_PHASES_BODY = {
    "dataCollectionId": COLLECTION_PHASES
}
PHASE_NAME = 'researchPhasesName'

# Описание коллекции Препараты
COLLECTION_DRUGS = 'botDrugGroupsCatalog'
COLLECTION_DRUGS_BODY = {
    "dataCollectionId": COLLECTION_DRUGS
}
DRUG_NAME = 'drugGroupsName'

COLLECTION_METHODS = 'botContactPreferencesCatalog'
COLLECTION_METHODS_BODY = {
    "dataCollectionId": COLLECTION_METHODS
}

COLLECTION_TEMPLATE = 'botTemplateMessageSettings'
COLLECTION_TEMPLATE_BODY = {
    "dataCollectionId": COLLECTION_TEMPLATE
}

COLLECTION_CONDITION = 'botStudyConditionsCatalog'
COLLECTION_CONDITION_BODY = {
    "dataCollectionId": COLLECTION_CONDITION
}
