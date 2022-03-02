import json
from datetime import datetime


def update_data(user_id: str, date: float):
    if user_id == None:
        return TypeError
    with open("config/data.json", "r") as read_file:
        data = read_file.read()
        if data:
            data = json.loads(data)
        else:
            clear_data()
            update_data(user_id, date)
            return
    date = str(date)
    with open("config/data.json", "w") as write_file:
        if user_id in data.keys():
            data[user_id].append(date)
        else:
            data[user_id] = []
            data[user_id].append(date)
        json.dump(data, write_file, indent=4)


def clear_data():
    with open("config/data.json", "w") as file:
        file.write("{}")


def get_data_dict():
    with open("config/data.json", "r") as read_file:
        data = read_file.read()
        if data:
            return json.loads(data)
        else:
            return {}


def get_data_json():
    data = open("config/data.json", 'rb')
    return data


def get_stat(date: str):
    data = get_data_dict()
    if data == {}:
        return "NO DATA"
    for user in data.keys():
        for i in range(len(data.get(user))):
            data[user][i] = datetime.fromtimestamp(float(data[user][i])).date()
    search_date = get_search_date(date, data)
    pass_count = get_pass(search_date, data, date)
    news_count = get_news(search_date, data, date)
    result_message = pass_count + "\n"
    result_message += news_count
    return result_message


def get_pass(search_date: list, data: dict, call_data: str):
    result_message = ""
    if call_data == "today":
        result_message += "Прохождений за сегодня: "
    elif call_data == "month":
        result_message += "Прохождений за месяц: "
    else:
        if len(search_date) == 1:
            date_text = str(search_date[0]).replace("-", ".")
        else:
            date_text = str(search_date[0]).replace("-", ".") + "-" + str(search_date[-1]).replace("-", ".")
        result_message += "Прохождений за " + date_text + ": "
    pass_count = 0
    for user in data.keys():
        for i in data.get(user):
            if i in search_date:
                pass_count += 1
    result_message += str(pass_count)
    return result_message


def get_news(search_date: list, data: dict, call_data: str):
    result_message = ""
    if call_data == "today":
        result_message += "Новых пользователей за сегодня: "
    elif call_data == "month":
        result_message += "Новых пользователей за месяц: "
    else:
        if len(search_date) == 1:
            date_text = str(search_date[0]).replace("-", ".")
        else:
            date_text = str(search_date[0]).replace("-", ".") + "-" + str(search_date[-1]).replace("-", ".")
        result_message += "Новых пользователей за " + date_text + ": "
    news_count = 0
    for user in data.keys():
        if data.get(user)[0] in search_date:
            news_count += 1
    result_message += str(news_count)
    return result_message


def get_search_date(call_data: str, data: dict) -> list:
    from datetime import date
    if call_data == "today":
        search_date = [datetime.today().date()]
    elif call_data == "month":
        month = datetime.today().date().month
        year = datetime.today().date().year
        days = datetime.today().date().day
        search_date = []
        for day in range(days):
            search_date.append(date(year, month, day + 1))
    else:
        if call_data == "all":
            call_data = "01.01.1971-"
            day = az(datetime.today().date().day)
            month = az(datetime.today().date().month)
            year = az(datetime.today().date().year)
            call_data += day + "."
            call_data += month + "."
            call_data += year
        if "-" in call_data:
            dates = call_data.split("-")
            search_date = []
            for i in range(2):
                day = int(dates[i][:2])
                month = int(dates[i][3:5])
                year = int(dates[i][-4:])
                dates[i] = int(datetime.timestamp(datetime(year, month, day + i)))
            for i in range(dates[0], dates[1], 86400):
                search_date.append(date.fromtimestamp(i))
        else:
            day = int(call_data[:2])
            month = int(call_data[3:5])
            year = int(call_data[-4:])
            search_date = [date(year, month, day)]
    return search_date


def az(num: int) -> str:  # add_zero
    num = str(num)
    if len(num) == 1:
        num = "0" + num
    return num

def get_user_list() -> str:
    result_message = ''
    data = get_data_dict()
    if data == {}:
        return "NO DATA"
    for user in data.keys():
        if user.isnumeric():
            result_message += "#" + user + "\n"
        else:
            result_message += "@" + user + "\n"
    return result_message