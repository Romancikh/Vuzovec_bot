import json

agricultural = ["35", "20", "21", "05", "19", "14"]
technic = ["23", "15", "24", "26", "29", "25", "17", "08"]
exact = ["38", "01", "03", "13", "22", "07", "16"]
humanities = ["45", "51", "46", "47", "58", "48"]
medicine = ["34", "32", "30", "36", "31", "33"]
art = ["53", "54", "55", "50", "52"]
education = ["44", "49"]
it = ["09", "02", "10"]
social = ["40", "43", "42", "37", "39", "41", "56"]
natural = ["04", "06", "18"]
radiotechnics = ["11", "12", "28", "27"]


def check_ege(specialty, data):
    ege = data.get("ege")
    spec_ege = specialty.get("ege_subjects")
    for i in range(len(spec_ege)):
        if type(spec_ege[i]) == list:
            for j in range(len(spec_ege[i])):
                spec_ege[i][j] = spec_ege[i][j].lower()
        else:
            spec_ege[i] = spec_ege[i].lower()
    point_sub = []
    flag = True
    for i in range(len(spec_ege)):
        if type(spec_ege[i]) == list:
            small_flag = False
            small_point_sub = []
            for sub in spec_ege[i]:
                if sub in ege:
                    small_flag = True
                    small_point_sub.append(sub)
            if small_flag:
                if len(small_point_sub) > 1:
                    point_sub.append(small_point_sub)
                else:
                    point_sub.append(*small_point_sub)
            else:
                flag = False
        else:
            if spec_ege[i] in ege:
                point_sub.append(spec_ege[i])
            else:
                flag = False
    if flag:
        return flag, point_sub
    else:
        return flag, None


def check_point(specialty, data):
    flag, point_sub = check_ege(specialty, data)
    if flag:
        point_sum = 0
        ege = data.get("ege")
        points = data.get("ege_points")
        for i in range(len(point_sub)):
            if type(point_sub[i]) == list:
                max_point = 0
                for sub in point_sub[i]:
                    if points[ege.index(sub)] > max_point:
                        max_point = points[ege.index(sub)]
                point_sum += max_point
            else:
                point_sum += points[ege.index(point_sub[i])]
        if data.get("budget_place"):
            if point_sum >= specialty.get("budget_points"):
                return True
        else:
            if point_sum >= specialty.get("contractual_points"):
                return True
    return False


def check_budget(specialty, data):
    budget = data.get("budget_place")
    if budget:
        if specialty.get("budget_place") > 0:
            return True
        else:
            return False
    else:
        balance = data.get("balance")
        if specialty.get("price") <= balance and specialty.get("contractual_place") > 0:
            return True
        else:
            return False


def check_magistracy(specialty, data, un_mag):
    magistracy = data.get("magistracy")
    if magistracy:
        if un_mag:
            return True
        else:
            return False
    else:
        return True


def check_reputation(specialty, data, un_rep):
    reputation = data.get("reputation")
    if reputation:
        if un_rep > 325:
            return True
        else:
            return False
    else:
        return True


def check_spec(specialty, data, un_rep, un_mag):
    args = [specialty, data]
    result = check_point(*args) and check_budget(*args) and check_magistracy(*args, un_mag) and check_reputation(*args,
                                                                                                                 un_rep)
    return result


def init_university(available_specialties, city, university):
    if available_specialties.get(city):
        if available_specialties[city].get(university):
            pass
        else:
            available_specialties[city][university] = {}
    else:
        available_specialties[city] = {}
        available_specialties[city][university] = {}
    return available_specialties


def processor(data: dict):
    specialty_list = {}
    with open("config/list.json", "r") as read_file:
        specialty_list = json.load(read_file)
    available_specialties = {}
    for city in data.get("city_list"):
        city_specialty_list = specialty_list.get(city)
        universities = city_specialty_list.keys()
        for university in universities:
            un_rep = city_specialty_list.get(university).get("rating")
            un_mag = city_specialty_list.get(university).get("magistracy")
            specialties = city_specialty_list.get(university).keys()
            for specialty in specialties:
                specialty_data = city_specialty_list.get(university).get(specialty)
                sphere = data.get("sphere")
                if sphere == "техника":
                    if specialty[:2] in technic:
                        if check_spec(specialty_data, data, un_rep, un_mag):
                            available_specialties = init_university(available_specialties, city, university)
                            available_specialties[city][university][specialty] = specialty_data
                elif sphere == "точные науки":
                    if specialty[:2] in exact:
                        if check_spec(specialty_data, data, un_rep, un_mag):
                            available_specialties = init_university(available_specialties, city, university)
                            available_specialties[city][university][specialty] = specialty_data
                elif sphere == "гуманитарные науки":
                    if specialty[:2] in humanities:
                        if check_spec(specialty_data, data, un_rep, un_mag):
                            available_specialties = init_university(available_specialties, city, university)
                            available_specialties[city][university][specialty] = specialty_data
                elif sphere == "медицина":
                    if specialty[:2] in medicine:
                        if check_spec(specialty_data, data, un_rep, un_mag):
                            available_specialties = init_university(available_specialties, city, university)
                            available_specialties[city][university][specialty] = specialty_data
                elif sphere == "искусство":
                    if specialty[:2] in art:
                        if check_spec(specialty_data, data, un_rep, un_mag):
                            available_specialties = init_university(available_specialties, city, university)
                            available_specialties[city][university][specialty] = specialty_data
                elif sphere == "образование":
                    if specialty[:2] in education:
                        if check_spec(specialty_data, data, un_rep, un_mag):
                            available_specialties = init_university(available_specialties, city, university)
                            available_specialties[city][university][specialty] = specialty_data
                elif sphere == "социальная сфера":
                    if specialty[:2] in social:
                        if check_spec(specialty_data, data, un_rep, un_mag):
                            available_specialties = init_university(available_specialties, city, university)
                            available_specialties[city][university][specialty] = specialty_data
                elif sphere == "естественные науки":
                    if specialty[:2] in natural:
                        if check_spec(specialty_data, data, un_rep, un_mag):
                            available_specialties = init_university(available_specialties, city, university)
                            available_specialties[city][university][specialty] = specialty_data
                elif sphere == "радиотехника":
                    if specialty[:2] in radiotechnics:
                        if check_spec(specialty_data, data, un_rep, un_mag):
                            available_specialties = init_university(available_specialties, city, university)
                            available_specialties[city][university][specialty] = specialty_data
                elif sphere == "it":
                    if specialty[:2] in it:
                        if check_spec(specialty_data, data, un_rep, un_mag):
                            available_specialties = init_university(available_specialties, city, university)
                            available_specialties[city][university][specialty] = specialty_data
                elif sphere == "аграрная сфера":
                    if specialty[:2] in agricultural:
                        if check_spec(specialty_data, data, un_rep, un_mag):
                            available_specialties = init_university(available_specialties, city, university)
                            available_specialties[city][university][specialty] = specialty_data
    return available_specialties
