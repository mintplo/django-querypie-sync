from django.conf import settings


class QuerypieAPIBase:
    BASE_URL = f"https://{settings.QUERYPIE_URL}/api/external"
    QUERYPIE_API_TOKEN = settings.QUERYPIE_API_TOKEN
    HEADERS = {"Authorization": QUERYPIE_API_TOKEN}
    DATABASE_NAME = "querypie"
