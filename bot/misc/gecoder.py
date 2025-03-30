from bot.config import env_vars
from requests import get
import json

server_adress = 'https://geocode-maps.yandex.ru/v1/?'
apikey = env_vars['GEOCODER_APIKEY']


async def get_city_by_name(city):
    request = f'{server_adress}apikey={apikey}&geocode=Россия, {city}&format=json'
    json_response = get(request).json()
    # with open('response1.json', 'w', encoding='UTF-8') as response_file:
    #     json.dump(json_response, response_file,  ensure_ascii=False, indent=4)
    # print()
    zxc = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["name"]
    print('city_name:', zxc)
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"]
    region = toponym["GeocoderMetaData"]["AddressDetails"]["Country"]["AdministrativeArea"]["SubAdministrativeArea"]
    city_name = region["Locality"]["LocalityName"]
    return city_name


async def get_city_by_cords(latitude, longitude):
    request = f'{server_adress}apikey={apikey}&geocode={longitude},{latitude}&format=json'
    json_response = get(request).json()
    # with open('response2.json', 'w', encoding='UTF-8') as response_file:
    #     json.dump(json_response, response_file,  ensure_ascii=False, indent=4)
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["metaDataProperty"]
    region = toponym["GeocoderMetaData"]["AddressDetails"]["Country"]["AdministrativeArea"]["SubAdministrativeArea"]
    city_name = region["Locality"]["LocalityName"]

    # city_point = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
    return city_name