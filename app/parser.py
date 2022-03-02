import os
import json
import pprint

import requests
from bs4 import BeautifulSoup

CITY_URL = "https://vuzoteka.ru/вузы/города"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "accept": "*/*"
}

AVAILABLE_SUBJECTS = ("русский язык", "математика", "физика", "химия", "история", "обществознание", "информатика и ИКТ",
                      "биология", "география", "литература", "иностранный язык")

data = {}
cities = []


def save_info():
    global data
    if "config" in os.listdir():
        with open("config/list.json", "w") as res_list:
            json.dump(data, res_list, indent=4)
    else:
        os.mkdir("config")
        return save_info()


def get_html(url, params=None):
    response = requests.get(url, headers=HEADERS, params=params)
    return response


def get_pages_count(html):
    soup = BeautifulSoup(html.text, 'html.parser')
    page_numbering = soup.find_all("a", class_="second")
    if page_numbering:
        return int(page_numbering[-1].get_text(strip=True))
    else:
        return 1


def get_cities():
    html = get_html(CITY_URL)
    if html.status_code == 200:
        soup = BeautifulSoup(html.text, 'html.parser')
        items = soup.find_all("div", class_="first")
        cities = []
        for item in items[1:]:
            cities.append({
                "name": item.find("div", class_="label-value").get_text(strip=True),
                "link": "https:" + item.find("div", class_="label-value").find_next("a").get('href')
            })
        return sorted(cities, key=lambda x: x.get("name"))


def add_cities_info(cities):
    global data
    for city in cities:
        data[city.get("name")] = {}
    return cities


def get_page_universities(html):
    soup = BeautifulSoup(html.text, 'html.parser')
    items = soup.find_all("div", class_="institute-search")
    universities = []
    for item in items:
        universities.append({
            "name": item.find("a").get_text(strip=True).split(" – ")[0],
            "link": "https:" + item.find("a").get("href")
        })
    return universities


def get_city_universities(city):
    html = get_html(city.get("link"))
    if html.status_code == 200:
        universities = []
        pages_count = get_pages_count(html)
        universities.extend(get_page_universities(html))
        for page in range(2, pages_count + 1):
            html = get_html(city.get("link"), params={"page": page})
            universities.extend(get_page_universities(html))
        return universities


def add_city_universities_info(universities, city):
    global data
    for university in universities:
        data[city.get("name")][university.get("name")] = {}
        add_university_params_info(university, city)
    return universities


def get_university_params(university):
    html = get_html(university.get("link"))
    if html.status_code == 200:
        try:
            params = []
            soup = BeautifulSoup(html.text, 'html.parser')
            items = soup.find_all("div", class_="tab-links-static")
            degree = []
            for item in items:
                degree.append(
                    item.find("span", class_="degree-tab").get_text(strip=True))
            if "магистратура" in degree:
                params.append(True)
            else:
                params.append(False)
            barrack = soup.find("div", class_="number-1")
            barrack = barrack.find("div", class_="institute-view-value")
            barrack = barrack.find("div")["class"][1]
            if barrack == "glyphicon-ok":
                params.append(True)
            else:
                params.append(False)
            un_license = soup.find("div", class_="number-2")
            un_license = un_license.find("div", class_="institute-view-value")
            un_license = un_license.find("div")["class"][1]
            if un_license == "glyphicon-ok":
                params.append(True)
            else:
                params.append(False)
            accreditation = soup.find("div", class_="number-3")
            accreditation = accreditation.find(
                "div", class_="institute-view-value")
            accreditation = accreditation.find("div")["class"][1]
            if accreditation == "glyphicon-ok":
                params.append(True)
            else:
                params.append(False)
            rating = soup.find("div", class_="number-8").find("div", class_="institute-view-value")
            rating = rating.find("div").find_all("div")[0].get_text(strip=True)
            params.append(int(rating))
        except AttributeError:
            params = [False, False, False, False, False]
        return params


def add_university_params_info(university, city):
    global data
    params = get_university_params(university)
    if params[2] and params[3]:
        data[city.get("name")][university.get(
            "name")]["magistracy"] = params[0]
        data[city.get("name")][university.get("name")]["barrack"] = params[1]
        data[city.get("name")][university.get("name")]["license"] = params[2]
        data[city.get("name")][university.get("name")]["accreditation"] = params[3]
        data[city.get("name")][university.get("name")]["rating"] = params[4]
    else:
        data[city.get("name")].pop(university.get("name"))


def get_university_specialities(university):
    html = get_html(university.get("link"))
    if html.status_code == 200:
        result = []
        soup = BeautifulSoup(html.text, 'html.parser')
        directions = soup.find_all(
            "div", class_="specialities-spoiler-content")
        for direction in directions:
            specialities = direction.find_all("div", class_="speciality-row-wrap")
            for speciality in specialities:
                speciality = speciality.find("ul")
                caption = speciality.find(
                    "li", class_="speciality-caption").find("div", class_="speciality-full")
                properties = speciality.find(
                    "li", class_="speciality-properties")
                spec_id, name, ege = get_caption(caption.get_text())
                places, points, price = get_properties(properties.get_text())
                if type(points) == tuple and type(places) == tuple:
                    result.append({
                        "id": spec_id,
                        "name": name,
                        "ege_subjects": ege,
                        "budget_points": points[0],
                        "contractual_points": points[1],
                        "budget_place": places[0],
                        "contractual_place": places[1],
                        "price": price
                    })
        return result


def get_caption(caption):
    if "егэ" in caption:
        subjects = caption.split("егэ")[1].strip()
        ege = get_ege_subjects(subjects)
    else:
        ege = False
    if "профиль" in caption:
        name = caption.split("профиль")[0].strip()
    elif "отделение" in caption:
        name = caption.split("отделение")[0].strip()
    else:
        name = caption.split("егэ")[0].strip()
    name = name.split("–")
    spec_id = name[0].strip()
    name = name[1].strip()
    return spec_id, name, ege


def get_ege_subjects(subjects):
    subjects = subjects.split(", ")
    ege = []
    for i in range(len(subjects)):
        if "или" in subjects[i]:
            subjects[i] = tuple(subjects[i].split(" или "))
    for subject in subjects:
        if type(subject) == str:
            if subject in AVAILABLE_SUBJECTS:
                ege.append(subject)
        else:
            sub_choice = []
            for i in subject:
                if i in AVAILABLE_SUBJECTS:
                    sub_choice.append(i)
            if len(sub_choice) > 0:
                if len(sub_choice) == 1:
                    ege.append(sub_choice[0])
                else:
                    ege.append(tuple(sub_choice))
    return ege


def get_properties(properties):
    if "места" in properties:
        if "баллы" in properties:
            places = properties.split("баллы")[0].strip()
            properties = properties.split("баллы")[1].strip()
            if "егэ" in properties:
                if "стоим" in properties:
                    points = properties.split("стоим")[0].strip()
                    properties = properties.split("стоим")[1].strip()
                    if "ость" in properties:
                        if "обуч" in properties:
                            price = "стоим" + properties.split("обуч")[0].strip()
                            places = get_places(places)
                            points = get_points(points)
                            price = get_price(price)
                            return places, points, price
    return False, False, False


def get_price(price):
    price = price.split("  ")[1].strip()
    if "–" in price:
        price = "0"
    else:
        price = price.split("/")[0].replace(" ", "")
    price = int(price)
    return price


def get_points(points):
    points = points.split(" ")
    b_point = points[3]
    c_point = points[5]
    if b_point == "–":
        if c_point != "–":
            b_point = c_point
        else:
            b_point = "0"
    if c_point == "–":
        c_point = b_point
    b_point = int(b_point)
    c_point = int(c_point)
    return b_point, c_point


def get_places(places):
    places = places.split(" ")
    b_place = places[3]
    c_place = places[5]
    if b_place == "–":
        b_place = "0"
    if c_place == "–":
        c_place = "0"
    b_place = int(b_place)
    c_place = int(c_place)
    return b_place, c_place


def add_university_specialities_info(specialities, university, city):
    global data
    if len(specialities) == 0:
        pass
    else:
        for speciality in specialities:
            if university.get("name") in data[city.get("name")].keys():
                if speciality.get("id") in data[city.get("name")][university.get("name")].keys():
                    old_spec = data[city.get("name")][university.get(
                        "name")][speciality.get("id")]
                    for key in ("budget_points", "contractual_points", "budget_place", "contractual_place"):
                        if speciality.get(key) > old_spec.get(key):
                            old_spec[key] = speciality.get(key)
                else:
                    data[city.get("name")][university.get("name")
                    ][speciality.get("id")] = delete_id(speciality)
                spec = data[city.get("name")][university.get(
                    "name")][speciality.get("id")]
                if spec.get("budget_place") == 0 and spec.get("contractual_place") == 0:
                    data[city.get("name")][university.get(
                        "name")].pop(speciality.get("id"))
                elif spec.get("budget_points") == 0 and spec.get("contractual_points") == 0:
                    data[city.get("name")][university.get(
                        "name")].pop(speciality.get("id"))
                elif not spec.get("ege_subjects"):
                    data[city.get("name")][university.get(
                        "name")].pop(speciality.get("id"))
        try:
            if len(data[city.get("name")][university.get("name")].keys()) == 5:
                data[city.get("name")].pop(university.get("name"))
        except KeyError:
            pass
        return specialities


def delete_id(speciality):
    import copy
    speciality_info = copy.deepcopy(speciality)
    speciality_info.pop("id")
    return speciality_info


def move_capital():
    global cities
    msc = cities.pop(cities.index({'name': 'Москва',
                                   'link': 'https://vuzoteka.ru/%D0%B2%D1%83%D0%B7%D1%8B/%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0'}))
    spb = cities.pop(cities.index({'name': 'Санкт-Петербург',
                                   'link': 'https://vuzoteka.ru/%D0%B2%D1%83%D0%B7%D1%8B/%D0%A1%D0%B0%D0%BD%D0%BA%D1%82-%D0%9F%D0%B5%D1%82%D0%B5%D1%80%D0%B1%D1%83%D1%80%D0%B3'}))
    cities.reverse()
    cities.append(spb)
    cities.append(msc)
    cities.reverse()


def remove_zero_price():
    global data
    for city in data.keys():
        if data.get(city):
            average_price = []
            for university in data.get(city).keys():
                specialties = list(data.get(city).get(university).keys())[5:]
                for specialty in specialties:
                    price = data.get(city).get(university).get(specialty).get("price")
                    if price:
                        average_price.append(price)
            if len(average_price):
                average_price = sum(average_price) // len(average_price)
            else:
                average_price = 178070
            for university in data.get(city).keys():
                specialties = list(data.get(city).get(university).keys())[5:]
                for specialty in specialties:
                    price = data.get(city).get(university).get(specialty).get("price")
                    if price == 0:
                        data[city][university][specialty]["price"] = average_price


def check():
    cities = add_cities_info(get_cities())
    for city in cities[42:43]:
        print("\n" + city.get("name") + "\n" + "=" * 30)
        universities = add_city_universities_info(get_city_universities(city), city)
        for university in universities:
            add_university_specialities_info(get_university_specialities(university), university, city)
    remove_zero_price()
    for city in data.keys():
        if data.get(city):
            pprint.pprint(data.get(city))


def main():
    global cities
    cities = add_cities_info(get_cities())
    for city in cities:
        universities = add_city_universities_info(get_city_universities(city), city)
        for university in universities:
            add_university_specialities_info(
                get_university_specialities(university), university, city)
    remove_zero_price()
    save_info()


if __name__ == '__main__':
    check()
else:
    if "list.json" not in os.listdir("config"):
        print("Start parsing")
        main()
        print("Finish parsing")
    else:
        cities = get_cities()
    move_capital()
