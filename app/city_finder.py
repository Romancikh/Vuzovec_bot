import requests
from app.parser import cities

URL = "https://htmlweb.ru/api/geo/city_coming/"


def find_city(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "country": "RU",
        "level": 1,
        "perpage": 1,
        "json": True
    }
    response = requests.get(URL, params=params)
    data = response.json()
    if data.get("limit") != 0:
        city = data.get("items")[0].get("name")
        for i in cities:
            if city == i.get("name"):
                return [city]
        return find_city(latitude, longitude - 2)
    return False


def find_city_list(latitude, longitude, length):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "length": length,
        "country": "RU",
        "level": 1,
        "perpage": 10,
        "json": True
    }
    response = requests.get(URL, params=params)
    data = response.json()
    if data.get("limit") != 0:
        city_list = []
        for city in data.get("items"):
            for i in cities:
                if city.get("name") in i.get("name"):
                    city_list.append(city.get("name"))
        city_list = list(set(city_list))
        if len(city_list) > 0:
            return city_list
        return find_city_list(latitude, longitude, length + 500)
    return False


if __name__ == "__main__":
    latitude = input("Введите широту: ")
    longitude = input("Введите долготу: ")
    length = input("Введите радиус: ")
    print(find_city_list(latitude, longitude, length))
    print(find_city(latitude, longitude))
