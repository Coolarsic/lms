import requests

API_KEY = '40d1649f-0493-4b70-98ba-98533de7710b'

import sys

from buiseness import find_business, find_businesses
from distance import lonlat_distance
from mepapi_PG import show_map
from geocoder import get_coordinates






def main():
    toponym_to_find = " ".join(sys.argv[1:])

    lat, lon = get_coordinates(toponym_to_find)
    address_ll = f"{lat},{lon}"
    span = "0.005,0.005"

    # Получаем координаты ближайшей аптеки.
    organization = find_business(address_ll, span, "аптека")
    point = organization["geometry"]["coordinates"]
    org_lat = float(point[0])
    org_lon = float(point[1])
    point_param = f"pt={org_lat},{org_lon},pm2dgl"

    show_map(f"ll={address_ll}&spn={span}", "map", add_params=point_param)

    # Добавляем на карту точку с исходным адресом.
    points_param = point_param + f"~{address_ll},pm2rdl"

    show_map("ll={0}&spn={1}".format(address_ll, span), "map", add_params=points_param)

    # Автопозиционирование
    show_map(map_type="map", add_params=points_param)

    # Сниппет
    # Название организации.
    name = organization["properties"]["CompanyMetaData"]["name"]
    # Адрес организации.
    address = organization["properties"]["CompanyMetaData"]["address"]
    # Время работы
    time = organization["properties"]["CompanyMetaData"]["Hours"]["text"]
    # Расстояние
    distance = round(lonlat_distance((lon, lat), (org_lon, org_lat)))

    snippet = f"Название:\t{name}\nАдрес:\t{address}\nВремя работы:\t{time}\n" \
              f"Расстояние:\t{distance}м."
    print(snippet)


if __name__ == "__main__":
    main()






def get_ll_span(address):
    toponym = geocode(address)
    if not toponym:
        return (None, None)

    toponym_coodrinates = toponym["Point"]["pos"]

    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    ll = ",".join([toponym_longitude, toponym_lattitude])

    envelope = toponym["boundedBy"]["Envelope"]

    l, b = envelope["lowerCorner"].split(" ")
    r, t = envelope["upperCorner"].split(" ")

    dx = abs(float(l) - float(r)) / 2.0
    dy = abs(float(t) - float(b)) / 2.0

    span = f"{dx},{dy}"

    return ll, span


def get_nearest_object(point, kind):
    ll = "{0},{1}".format(point[0], point[1])
    geocoder_request = f"http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": API_KEY,
        "geocode": ll,
        "format": "json"}
    if kind:
        geocoder_params['kind'] = kind

    response = requests.get(geocoder_request, params=geocoder_params)
    if not response:
        raise RuntimeError(
            f"""Ошибка выполнения запроса:
            {geocoder_request}
            Http статус: {response.status_code,} ({response.reason})""")

    json_response = response.json()
    features = json_response["response"]["GeoObjectCollection"]["featureMember"]
    return features[0]["GeoObject"]["name"] if features else None

if __name__ == "__main__":
    lon = input("Введите долготу: ")
    lat = input("Введите широту: ")
    typ = "apteka"
    print(get_nearest_object((lon, lat), typ))