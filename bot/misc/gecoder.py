from bot.config import env_vars
from requests import get
import logging
import json

server_adress = 'https://geocode-maps.yandex.ru/v1/?'
apikey = env_vars['GEOCODER_APIKEY']


async def get_city_by_name(city):
    request = f'{server_adress}apikey={apikey}&geocode={city}&format=json'
    json_response = get(request).json()
    with open('zxc.json', 'w', encoding='UTF-8') as jsonfile:
        json.dump(json_response, jsonfile, ensure_ascii=False, indent=2)
    try:
        city_name = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["name"]
        return city_name if len(city_name) <= 32 else None
    except Exception as ex:
        logging.error(ex)
        return None


async def get_city_by_cords(latitude, longitude):
    request = f'{server_adress}apikey={apikey}&geocode={longitude},{latitude}&format=json'
    json_response = get(request).json()
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"]
    administrative_area = toponym["GeocoderMetaData"]["AddressDetails"]["Country"]["AdministrativeArea"]
    try:
        if "SubAdministrativeArea" in administrative_area:
            city_name = administrative_area["SubAdministrativeArea"]["Locality"]["LocalityName"]
        else:
            city_name = administrative_area["Locality"]["LocalityName"]
        return city_name if len(city_name) <= 32 else None
    except Exception as ex:
        logging.error(ex)
        return None
