import datetime
import app.sub_group_list as sub_group_list

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from app import parser
from app.city_finder import find_city, find_city_list
from app.processor import processor
from app.data_processor import update_data
from app.book_maker import make_book
from random import choice
from datetime import datetime

available_decision_answer = ("да", "нет")
available_subjects = ("математика (базовая)", "математика (профиль)", "физика", "химия", "история", "обществознание",
                      "информатика и икт", "биология", "география", "литература", "иностранный язык")
sphere_list = ("техника", "точные науки", "гуманитарные науки", "медицина", "искусство", "образование",
               "социальная сфера", "естественные науки", "радиотехника", "it", "аграрная сфера")
decision_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
decision_keyboard.add(*available_decision_answer)
remove_keyboard = types.ReplyKeyboardRemove()
user_properties = {}

technical_supporters_list = ["@white_tears_of_autumn", "@romankutimskiy", "@Artyomeister"]


class TestQuestions(StatesGroup):
    sphere_decision = State()
    sphere_choice = State()
    finding_sphere = State()
    sphere_answer_handler = State()

    subject_question = State()
    subject_decision = State()
    subject_choice = State()
    finding_subject = State()
    point_input = State()

    city_decision = State()
    barrack_decision = State()
    geolocation_input = State()
    city_input = State()
    radius_input = State()
    city_number_choice = State()

    budget_place_decision = State()
    balance_input = State()

    magistracy_decision = State()
    magistracy_place_decision = State()

    reputation_decision = State()
    result = State()


class SpecialtyButton:
    def __init__(self, info: dict, key, city, university: str):
        self.info = info
        self.key = key
        self.city = gct(city.lower())
        self.university = gct(university.lower())
        self.button = types.InlineKeyboardButton(text=self.key,
                                                 callback_data=self.city + "_" + self.university + "_" + self.key)

    async def print_specialty_info(self, message: types.Message):
        message_res = ""
        message_res += self.info.get("name") + "\n"
        budget_place = self.info.get("budget_place")
        contractual_place = self.info.get("contractual_place")
        message_res += "<u>Места</u>: Б%s Д%s" % (budget_place, contractual_place) + "\n"
        budget_points = self.info.get("budget_points")
        contractual_points = self.info.get("contractual_points")
        message_res += "<u>Баллы</u>: Б%s Д%s" % (budget_points, contractual_points) + "\n"
        price = self.info.get("price")
        if price != 0:
            message_res += "<u>Цена</u>: %s руб./год" % (price) + "\n"
        ege_subjects = self.info.get("ege_subjects")
        ege_sub_mes = ""
        for sub in ege_subjects:
            if type(sub) == list:
                for i in sub[:-1]:
                    ege_sub_mes += i + " или "
                ege_sub_mes += sub[-1] + ", "
            else:
                ege_sub_mes += sub + ", "
        ege_sub_mes = ege_sub_mes[:-2]
        message_res += "<u>Предметы ЕГЭ</u>: " + ege_sub_mes
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        button = types.InlineKeyboardButton(text="========Свернуть========", callback_data="collapse_the_list")
        keyboard.add(button)
        await message.answer(message_res, parse_mode=types.ParseMode.HTML, reply_markup=keyboard)


class UniversityButton:
    def __init__(self, key, city: str):
        self.university = key
        self.key = gct(key.lower())
        self.city = gct(city.lower())
        self.specialties = []
        self.button = types.InlineKeyboardButton(text=key, callback_data=self.city + "_" + self.key + "_")

    def add_specialty(self, specialty: SpecialtyButton):
        self.specialties.append(specialty)

    async def print_specialty_list(self, message: types.Message):
        keyboard = types.InlineKeyboardMarkup()
        buttons = []
        for specialty in self.specialties:
            buttons.append(specialty.button)
        keyboard.add(*buttons)
        button = types.InlineKeyboardButton(text="========Назад========", callback_data=self.city + "_")
        keyboard.add(button)
        await message.answer("Специальности университета " + self.university, reply_markup=keyboard)


class CityButton:
    def __init__(self, key: str):
        self.city = key
        self.key = gct(key.lower())
        self.universities = []
        self.button = types.InlineKeyboardButton(text=key, callback_data=self.key + "_" + "_")

    def add_unversity(self, university: UniversityButton):
        self.universities.append(university)

    async def print_university_list(self, message: types.Message):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        buttons = []
        for university in self.universities:
            buttons.append(university.button)
        keyboard.add(*buttons)
        button = types.InlineKeyboardButton(text="========Назад========", callback_data="print_result_city_list")
        keyboard.add(button)
        await message.answer("Университеты города " + self.city, reply_markup=keyboard)


def gct(data):  # get_callback_text
    if len(data) > 10:
        return data[:5] + data[-5:]
    return data


async def callback_query_handler(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    cities_res = user_properties[user_id].get("cities_res")
    data = callback_query.data.split("_")
    for city in cities_res:
        if gct(data[0]) == city.key and not data[1]:
            await city.print_university_list(callback_query.message)
            await callback_query.message.delete()
        if gct(data[1]):
            for university in city.universities:
                if gct(data[1]) == university.key and gct(data[0]) == university.city and not data[2]:
                    await university.print_specialty_list(callback_query.message)
                    await callback_query.message.delete()
                if data[2]:
                    for specialty in university.specialties:
                        if data[2] == specialty.key and gct(data[1]) == specialty.university and gct(
                                data[0]) == specialty.city:
                            await specialty.print_specialty_info(callback_query.message)


async def print_subject_list(callback_query: types.CallbackQuery | types.Message, state: FSMContext):
    user_id = callback_query.from_user.id
    is_passed = user_properties[user_id].get("is_passed")
    result_message = ""
    for i in range(len(available_subjects)):
        result_message += str(i) + ". " + available_subjects[i] + "\n"
    try:
        await callback_query.message.answer(result_message)
    except:
        if is_passed:
            await callback_query.answer(
                "Введите названия предметов, которые Вы сдали на ЕГЭ, или их номер <u>через запятую</u>",
                parse_mode=types.ParseMode.HTML)
        else:
            await callback_query.answer(
                "Введите названия предметов, которые Вы выбрали для сдачи на ЕГЭ, или их номер <u>через запятую</u>",
                parse_mode=types.ParseMode.HTML)
        await callback_query.answer(result_message, reply_markup=remove_keyboard)


async def print_sphere_subject(message: types.Message, state: FSMContext):
    data = await state.get_data()
    sphere = data.get("sphere")
    groups = sub_group_list.spheres.get(sphere)
    await message.answer("Введите номер одной из понравившихся групп", reply_markup=remove_keyboard)
    k = 1
    for i in groups:
        group = sub_group_list.groups[i]
        res_mes = ''
        res_mes += str(k) + '\n'
        for sub in group:
            res_mes += sub + '\n'
        await message.answer(res_mes)
        k += 1
    await TestQuestions.finding_sphere.set()


async def select_all_cities(callback_query: types.CallbackQuery, state: FSMContext):
    city_choice = []
    for i in parser.cities:
        city_choice.append(i.get("name"))
    await state.update_data(city_list=city_choice)
    await callback_query.message.answer("=====================\nВы выбрали все города\n=====================")
    await callback_query.message.answer("Нужно ли Вам общежитие?", reply_markup=decision_keyboard)
    await TestQuestions.barrack_decision.set()


async def print_city_list(callback_query: types.CallbackQuery, state: FSMContext):
    result_message = ""
    for i in range(len(parser.cities)):
        result_message += str(i + 1) + ". " + parser.cities[i].get("name") + "\n"
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="========Свернуть========", callback_data="collapse_the_list")
    keyboard.add(button)
    await callback_query.message.answer(result_message, reply_markup=keyboard)


async def print_result_city_list(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.message.text != "Итоги теста":
        await callback_query.message.delete()
    if callback_query.message.text == "Итоги теста":
        await callback_query.answer(
            "Мы будем благодарны, если Вы сделаете репост бота для Ваших одноклассников или друзей!",
            show_alert=True)

    user_id = callback_query.from_user.id
    cities_res = user_properties[user_id].get("cities_res")
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = []
    for city in cities_res:
        buttons.append(city.button)
    keyboard.add(*buttons)
    button = types.InlineKeyboardButton(text="========Свернуть========", callback_data="collapse_the_list")
    keyboard.add(button)
    await callback_query.message.answer("Список городов", reply_markup=keyboard)


async def collapse_the_list(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()


async def print_subject_choice(message: types.Message, state: FSMContext):
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(text="Вывести список доступных предметов",
                                        callback_data="print_subject_list")
    keyboard.add(button)
    await message.answer("Введите названия предметов или их номер <u>через запятую</u>", reply_markup=keyboard,
                         parse_mode=types.ParseMode.HTML)


async def print_city_choice(message: types.Message, state: FSMContext):
    await message.answer("Выберите город", reply_markup=remove_keyboard)
    keyboard = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(text="Вывести список доступных городов", callback_data="print_city_list"),
               types.InlineKeyboardButton(text="Выбрать все", callback_data="select_all_cities")]
    another_city = await state.get_data()
    another_city = another_city.get("another_city")
    if another_city:
        keyboard.add(*buttons)
    else:
        keyboard.add(buttons[0])
    await message.answer("Вы можете ввести номер или название города")
    await message.answer("Введите один или несколько городов <u>через запятую</u>", reply_markup=keyboard,
                         parse_mode=types.ParseMode.HTML)


async def print_subjects_to_pass(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    is_passed = user_properties[user_id].get("is_passed")
    await message.answer("Предметы ЕГЭ, которые Вы выбрали: ")
    data = await state.get_data()
    ege = data.get("ege")
    result_message = ""
    for subject in ege:
        if subject == None:
            result_message += 'математика (базовая)'
        else:
            result_message += subject + "\n"
    await message.answer(result_message)
    if is_passed:
        await message.answer(
            "Введите баллы, на которые Вы сдали ЕГЭ по выбранным предметам\nПожалуйста, сделайте это в <u>указанном порядке</u>",
            parse_mode=types.ParseMode.HTML)
        await message.answer("Пример:\n72 91 64 49\nили\n72, 91, 64, 49")
    else:
        await message.answer(
            "Введите баллы, на которые Вы планируете сдать ЕГЭ по выбранным предметам\nПожалуйста, сделайте это в <u>указанном порядке</u>",
            parse_mode=types.ParseMode.HTML)
        await message.answer("Пример:\n72 91 64 49\nили\n72, 91, 64, 49")


async def cmd_back(message: types.Message, state: FSMContext):
    state_id = await state.get_state()
    data = await state.get_data()
    if state_id == TestQuestions.sphere_decision.state:
        await state.finish()
        await test_start(message)
    if state_id == TestQuestions.sphere_choice.state:
        await state.finish()
        await test_start(message)
    if state_id == TestQuestions.finding_sphere.state:
        await state.finish()
        await test_start(message)
    if state_id == TestQuestions.sphere_answer_handler.state:
        message.text = 'нет'
        await sphere_decision(message, state)
    if state_id == TestQuestions.subject_question.state:
        if data.get('sphere_test'):
            if data.get('sphere_test') == "proftest":
                message.text = 'профтест'
                await finding_sphere(message, state)
            if data.get('sphere_test') == "testometrika":
                message.text = 'testometrika'
                await finding_sphere(message, state)
        else:
            message.text = 'да'
            await sphere_decision(message, state)
    if state_id == TestQuestions.subject_choice.state:
        user_id = message.from_user.id
        if user_properties[user_id]["is_passed"]:
            sphere = data.get('sphere')
            message.text = sphere
            await sphere_choice(message, state)
        else:
            message.text = "нет"
            await subject_question(message, state)
    if state_id == TestQuestions.subject_decision.state:
        sphere = data.get('sphere')
        message.text = sphere
        await sphere_choice(message, state)
    if state_id == TestQuestions.finding_subject.state:
        message.text = "нет"
        await subject_question(message, state)
    if state_id == TestQuestions.point_input.state:
        user_id = message.from_user.id
        if user_properties[user_id]["is_passed"]:
            message.text = 'да'
            await subject_decision(message, state)
        else:
            if user_properties[user_id]["is_chosen"]:
                message.text = "да"
                await subject_decision(message, state)
            else:
                message.text = "нет"
                await subject_decision(message, state)
    if state_id == TestQuestions.city_decision.state:
        user_id = message.from_user.id
        if user_properties[user_id]["is_chosen"] or user_properties[user_id]["is_passed"]:
            ege = data.get("ege")
            ege.remove('русский язык')
            try:
                if 'математика' in ege:
                    text = ','.join(ege).replace('математика', "математика (профиль)")
                else:
                    text = ','.join(ege)
            except TypeError:
                text = str(*ege)
            message.text = text
            await subject_choice(message, state)
        else:
            message.text = str(data.get('chosen_group'))
            await finding_subject(message, state)
    if state_id == TestQuestions.geolocation_input.state:
        ege = data.get('ege_points')
        text = ' '.join(list(map(str, ege)))
        message.text = text
        await point_input(message, state)
    if state_id == TestQuestions.city_input.state:
        another_city = data.get('another_city')
        if another_city:
            text = 'да'
        else:
            text = 'нет'
        message.text = text
        await city_question(message, state)
    if state_id == TestQuestions.city_number_choice.state:
        another_city = data.get('another_city')
        if another_city:
            text = 'да'
        else:
            text = 'нет'
        message.text = text
        await city_question(message, state)
    if state_id == TestQuestions.radius_input.state:
        longitude = data.get('longitude')
        latitude = data.get('latitude')
        message.location = types.location.Location
        message.location.longitude = longitude
        message.location.latitude = latitude
        message.text = None
        await geolocation_input(message, state)
    if state_id == TestQuestions.barrack_decision.state:
        what_to_find = data.get('what_to_find')
        if what_to_find == 'radius':
            message.text = 'Искать в радиусе'
            await city_number_choice(message, state)
        elif what_to_find == "Ближайший город":
            longitude = data.get('longitude')
            latitude = data.get('latitude')
            message.location = types.location.Location
            message.location.longitude = longitude
            message.location.latitude = latitude
            message.text = None
            await geolocation_input(message, state)
        elif what_to_find == 'city':
            message.text = "Указать город"
            await geolocation_input(message, state)
    if state_id == TestQuestions.budget_place_decision.state:
        what_to_find = data.get('what_to_find')
        if what_to_find == 'radius':
            message.text = data.get('chosen_radius')
            await radius_input(message, state)
        elif what_to_find == "nearest_city":
            message.text = "Ближайший город"
            await city_number_choice(message, state)
        elif what_to_find == 'city':
            city_list = data.get('city_list')
            try:
                text = ','.join(city_list)
            except TypeError:
                text = str(*city_list)
            message.text = text
            await city_input(message, state)
    if state_id == TestQuestions.magistracy_decision.state:
        if data.get('budget_place'):
            if data.get('barrack'):
                message.text = 'да'
            else:
                message.text = 'нет'
            await barrack_decision(message, state)
        else:
            message.text = 'нет'
            await budget_place_decision(message, state)
    if state_id == TestQuestions.balance_input.state:
        if data.get('barrack'):
            message.text = 'да'
        else:
            message.text = 'нет'
        await barrack_decision(message, state)
    if state_id == TestQuestions.magistracy_place_decision.state:
        if data.get('budget_place'):
            message.text = 'да'
            await budget_place_decision(message, state)
        else:
            message.text = str(data.get('balance'))
            await balance_input(message, state)
    if state_id == TestQuestions.reputation_decision.state:
        if data.get('magistracy'):
            message.text = 'да'
            await magistracy_decision(message, state)
        else:
            if data.get('budget_place'):
                message.text = 'да'
                await budget_place_decision(message, state)
            else:
                message.text = message.text = str(data.get('balance'))
                await balance_input(message, state)
    if state_id == TestQuestions.result.state:
        if data.get('magistracy'):
            message.text = 'да'
        else:
            message.text = 'нет'
        await magistracy_place_decision(message, state)


"""Определение сферы и её сохранение"""


async def test_start(message: types.Message):
    user_id = message.from_user.id
    user_properties[user_id] = {"is_passed": False, "is_chosen": True, "cities_res": []}
    await message.answer("Вы определились со сферой обучения?", reply_markup=decision_keyboard)
    await TestQuestions.sphere_decision.set()


async def sphere_decision(message: types.Message, state: FSMContext):
    decision = message.text.lower()
    if decision not in available_decision_answer:
        await message.answer("Пожалуйста, используйте клавиатуру ниже")
        return
    if decision == "да":
        sphere_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        sphere_keyboard.add(*sphere_list)
        await message.answer("Выберите сферу", reply_markup=sphere_keyboard)
        await TestQuestions.sphere_choice.set()
    elif decision == "нет":
        prof_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        prof_buttons = ["ПрофТест", "testometrika"]
        prof_keyboard.add(*prof_buttons)
        await message.answer("Выберите тест на профориентацию", reply_markup=prof_keyboard)
        await TestQuestions.finding_sphere.set()


async def finding_sphere(message: types.Message, state: FSMContext):
    answer = message.text.lower()
    if answer == "профтест":
        await state.update_data(sphere_test="proftest")
        await message.answer("https://careertest.ru/tests/opredelenie-professionalnyh-sklonnostej/")
        await message.answer("Пройдите тест на предложенном сайте и введите свой результат")
        await message.answer("Введите баллы по порядку")
        message_text = "1. Интеллектуально-исследовательская работа\n"
        message_text += "2. Планово-экономические виды деятельности\n"
        message_text += "3. Практическая деятельность\n"
        message_text += "4. Работа с людьми\n"
        message_text += "5. Экстремальные виды деятельности\n"
        message_text += "6. Эстетические виды деятельности\n"
        message_text += "Пример: 7 5 5 4 2 1"
        await message.answer(message_text, reply_markup=remove_keyboard)
    elif answer == "testometrika":
        await state.update_data(sphere_test="testometrika")
        await message.answer("https://testometrika.com/business/test-to-determine-career/")
        await message.answer("Пройдите тест на предложенном сайте и введите свой результат")
        await message.answer("Введите баллы по порядку")
        message_text = "1. Человек-Художественные образы\n"
        message_text += "2. Человек-Знаковая система\n"
        message_text += "3. Человек-Природа\n"
        message_text += "4. Человек-Техника\n"
        message_text += "5. Человек-Человек\n"
        message_text += "Пример: 10 9 3 11 7"
        await message.answer(message_text, reply_markup=remove_keyboard)
    else:
        await message.answer("Пожалуйста, используйте клавиатуру ниже")
        return
    await TestQuestions.sphere_answer_handler.set()


async def sphere_answer_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    sphere_test = data.get("sphere_test")
    answer = message.text.replace(",", " ")
    answer = answer.split()
    for i in range(len(answer)):
        if answer[i].strip().isnumeric():
            answer[i] = int(answer[i])
        else:
            await message.answer("Следуйте <u>предложенному формату</u> ввода результатов теста",
                                 parse_mode=types.ParseMode.HTML)
            return
    sphere_ans = answer.index(max(answer))
    sphere_id = 0
    if sphere_test == "proftest" and len(answer) == 6:
        if sphere_ans == 0:
            sphere_id = 1
        if sphere_ans == 1:
            sphere_id = 2
        if sphere_ans == 2:
            sphere_id = 0
        if sphere_ans == 3:
            sphere_id = 6
        if sphere_ans == 4:
            sphere_id = 5
        if sphere_ans == 5:
            sphere_id = 4
    elif sphere_test == "testometrika" and len(answer) == 5:
        if sphere_ans == 0:
            sphere_id = 4
        if sphere_ans == 1:
            sphere_id = choice((1, 8, 9))
        if sphere_ans == 2:
            sphere_id = 10
        if sphere_ans == 3:
            sphere_id = 0
        if sphere_ans == 4:
            sphere_id = 6
    else:
        await message.answer("Следуйте <u>предложенному формату</u> ввода результатов теста",
                             parse_mode=types.ParseMode.HTML)
        return
    await state.update_data(sphere=sphere_list[sphere_id])
    await message.answer("Ваша сфера: " + sphere_list[sphere_id])
    if sphere_list[sphere_id] == "искусство":
        await message.answer('Вы выбрали направление "Искусство". Будьте готовы к <u>дополнительному испытанию</u>',
                             parse_mode=types.ParseMode.HTML)
    await message.answer("Вы уже выпустились из школы?", reply_markup=decision_keyboard)
    await TestQuestions.subject_question.set()


async def sphere_choice(message: types.Message, state: FSMContext):
    answer = message.text.lower()
    if answer not in sphere_list:
        await message.answer("Пожалуйста, используйте клавиатуру ниже")
        return
    if answer == "искусство":
        await message.answer('Вы выбрали направление "Искусство". Будьте готовы к <u>дополнительному испытанию</u>',
                             parse_mode=types.ParseMode.HTML)
    await state.update_data(sphere=answer)
    await message.answer("Вы уже выпустились из школы?", reply_markup=decision_keyboard)
    await TestQuestions.subject_question.set()


"""Определение предметов и баллов"""


async def subject_question(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    decision = message.text.lower()
    if decision not in available_decision_answer:
        await message.answer("Пожалуйста, используйте клавиатуру ниже")
        return
    if decision == "да":
        user_properties[user_id]["is_passed"] = True
        await print_subject_list(message, state)
        await TestQuestions.subject_choice.set()
    elif decision == "нет":
        user_properties[user_id]["is_passed"] = False
        await message.answer("Вы уже решили, какие предметы ЕГЭ будете сдавать?", reply_markup=decision_keyboard)
        await TestQuestions.subject_decision.set()


async def subject_decision(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    decision = message.text.lower()
    if decision not in available_decision_answer:
        await message.answer("Пожалуйста, используйте клавиатуру ниже")
        return
    if decision == "да":
        user_properties[user_id]["is_chosen"] = True
        await print_subject_list(message, state)
        await TestQuestions.subject_choice.set()
    elif decision == "нет":
        user_properties[user_id]["is_chosen"] = False
        await message.answer("Комбинации предметов подходящие под вашу сферу")
        await print_sphere_subject(message, state)
        await TestQuestions.finding_subject.set()


async def finding_subject(message: types.Message, state: FSMContext):
    answer = message.text.lower()
    if answer.isnumeric():
        answer = int(answer)
        data = await state.get_data()
        sphere = data.get("sphere")
        groups = sub_group_list.spheres.get(sphere)
        if 0 < answer <= len(groups):
            await state.update_data(chosen_group=answer)
            ege_subjects = set()
            group = sub_group_list.groups[groups[answer - 1]]
            for i in group:
                ege_subjects.add(i)
        else:
            await message.answer("Введите одно число из списка")
            return
    else:
        await message.answer("Введите одно число")
        return
    ege_sub = ["русский язык", "математика (базовая)"]
    ege_sub.extend(list(ege_subjects))
    ege_sub = list(set(ege_sub))
    if "математика (профиль)" in ege_sub:
        ege_sub.remove("математика (базовая)")
        ege_sub.remove("математика (профиль)")
        ege_sub.append("математика")
    await state.update_data(ege=ege_sub)
    await print_subjects_to_pass(message, state)
    await TestQuestions.point_input.set()


async def subject_choice(message: types.Message, state: FSMContext):
    answer = message.text.lower()
    ege_subjects = set()
    for subject in answer.split(","):
        subject = subject.strip()
        if subject.isnumeric():
            subject = int(subject)
            if subject not in range(len(available_subjects)):
                await message.answer("Пожалуйста, введите предметы ЕГЭ из <u>списка</u> доступных",
                                     parse_mode=types.ParseMode.HTML)
                return
            else:
                ege_subjects.add(available_subjects[subject])
        else:
            if subject not in available_subjects:
                await message.answer("Пожалуйста, введите предметы ЕГЭ из <u>списка</u> доступных",
                                     parse_mode=types.ParseMode.HTML)
                return
            else:
                ege_subjects.add(subject)
    ege_sub = ["русский язык", "математика (базовая)"]
    ege_sub.extend(list(ege_subjects))
    ege_sub = list(set(ege_sub))
    if "математика (профиль)" in ege_sub:
        ege_sub.remove("математика (базовая)")
        ege_sub.remove("математика (профиль)")
        ege_sub.append("математика")
    await state.update_data(ege=ege_sub)
    await print_subjects_to_pass(message, state)
    await TestQuestions.point_input.set()


async def point_input(message: types.Message, state: FSMContext):
    points = []
    data = await state.get_data()
    ege = data.get("ege")
    answer = message.text.replace(",", " ")
    answer = list(map(str.strip, answer.split()))
    if len(answer) > len(ege):
        await message.answer("Вы ввели слишком много чисел")
        return
    if len(answer) < len(ege):
        await message.answer("Вы ввели недостаточно чисел")
        return
    for point in answer:
        point = point.strip()
        if point.isnumeric():
            point = int(point)
            if point < 0 or point > 100:
                await message.answer("Есть числа меньше 0 или больше 100")
                return
            points.append(point)
        else:
            await message.answer("Пожалуйста, введите число")
            return
    await state.update_data(ege_points=points)
    await message.answer("Готовы ли Вы учиться в другом городе?", reply_markup=decision_keyboard)
    await TestQuestions.city_decision.set()


"""определение города"""


async def city_question(message: types.Message, state: FSMContext):
    decision = message.text.lower()
    if decision not in available_decision_answer:
        await message.answer("Пожалуйста, используйте клавиатуру ниже")
        return
    if decision == "да":
        await state.update_data(another_city=True)
    else:
        await state.update_data(another_city=False)
    geolocation_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    await message.answer(
        "Если указываете геопозицию, не забудьте включить геолокацию на вашем устройстве и выключить сторонние приложения для сокрытия местоположения")
    buttons = [types.KeyboardButton(text="Указать геолокацию", request_location=True), "Указать город"]
    geolocation_keyboard.add(*buttons)
    await TestQuestions.geolocation_input.set()
    await message.answer("Указать...", reply_markup=geolocation_keyboard)


async def city_input(message: types.Message, state: FSMContext):
    city_choice = message.text.strip()
    city_choice = list(map(str.strip, city_choice.split(",")))
    for i in range(len(city_choice)):
        city_choice[i] = city_choice[i].strip()
        if city_choice[i].isnumeric():
            city_choice[i] = int(city_choice[i]) - 1
            if city_choice[i] in range(len(parser.cities)):
                city_choice[i] = parser.cities[city_choice[i]].get("name")
            else:
                await message.answer("Введите город из <u>списка</u>", parse_mode=types.ParseMode.HTML)
                return
        else:
            is_available = False
            for city in parser.cities:
                if city_choice[i] == city.get("name"):
                    is_available = True
                    break
            if not is_available:
                await message.answer("Введите город из <u>списка</u>", parse_mode=types.ParseMode.HTML)
                return
    await state.update_data(city_list=city_choice)
    await message.answer("Нужно ли Вам общежитие?", reply_markup=decision_keyboard)
    await TestQuestions.barrack_decision.set()


async def geolocation_input(message: types.Message, state: FSMContext):
    if message.text == "Указать город":
        await state.update_data(what_to_find='city')
        await print_city_choice(message, state)
        await TestQuestions.city_input.set()
    elif message.text == None:
        now_longitude = message.location.longitude
        now_latitude = message.location.latitude
        await state.update_data(longitude=now_longitude)
        await state.update_data(latitude=now_latitude)
        city_number_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Искать в радиусе", "Ближайший город"]
        city_number_keyboard.add(*buttons)
        await message.answer("Что искать?", reply_markup=city_number_keyboard)
        await TestQuestions.city_number_choice.set()
    else:
        await message.answer("Используйте клавиатуру ниже")
        return


async def city_number_choice(message: types.Message, state: FSMContext):
    if message.text == "Искать в радиусе":
        await state.update_data(what_to_find='radius')
        await message.answer("Введите радиус в километрах, рекомендуемое значение = 500", reply_markup=remove_keyboard)
        await TestQuestions.radius_input.set()
    elif message.text == "Ближайший город":
        await state.update_data(what_to_find='nearest_city')
        data = await state.get_data()
        city = find_city(data.get("latitude"), data.get("longitude"))
        if city:
            await state.update_data(city_list=city)
            await message.answer("Нужно ли Вам общежитие?", reply_markup=decision_keyboard)
            await TestQuestions.barrack_decision.set()
        else:
            await message.answer("===========================\nФункция временно недоступна")
            await message.answer("   Попробуйте снова позже  \n===========================")
            geolocation_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button = types.KeyboardButton("Указать город")
            geolocation_keyboard.add(button)
            await message.answer("А сейчас...", reply_markup=geolocation_keyboard)
            await TestQuestions.geolocation_input.set()


async def radius_input(message: types.Message, state: FSMContext):
    radius_chioce = message.text.strip()
    await state.update_data(chosen_radius=str(radius_chioce))
    if len(radius_chioce.split(",")) != 1 or len(radius_chioce.split(" ")) != 1:
        await message.answer("Введите одно значение")
    if radius_chioce.isnumeric():
        radius_chioce = int(radius_chioce)
        data = await state.get_data()
        city = find_city_list(data.get("latitude"), data.get("longitude"), radius_chioce)
        if city:
            await state.update_data(city_list=city)
        else:
            await message.answer("===========================\nФункция временно недоступна")
            await message.answer("   Попробуйте снова позже  \n===========================")
            geolocation_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            button = types.KeyboardButton("Указать город")
            geolocation_keyboard.add(button)
            await message.answer("А сейчас...", reply_markup=geolocation_keyboard)
            await TestQuestions.geolocation_input.set()
    else:
        await message.answer("Введите число")
        return
    await message.answer("Нужно ли Вам общежитие?", reply_markup=decision_keyboard)
    await TestQuestions.barrack_decision.set()


"""бюджетные места и общежитие"""


async def barrack_decision(message: types.Message, state: FSMContext):
    decision = message.text.lower()
    if decision not in available_decision_answer:
        await message.answer("Пожалуйста, используйте клавиатуру ниже")
        return
    if decision == "да":
        await state.update_data(barrack=True)
    elif decision == "нет":
        await state.update_data(barrack=False)
    await message.answer("Нужны ли Вам бюджетные места?", reply_markup=decision_keyboard)
    await TestQuestions.budget_place_decision.set()


async def budget_place_decision(message: types.Message, state: FSMContext):
    decision = message.text.lower()
    if decision not in available_decision_answer:
        await message.answer("Пожалуйста, используйте клавиатуру ниже")
        return
    if decision == "да":
        await state.update_data(budget_place=True)
        await message.answer("Планируете ли Вы поступать на магистратуру?", reply_markup=decision_keyboard)
        await TestQuestions.magistracy_decision.set()
    elif decision == "нет":
        await state.update_data(budget_place=False)
        await message.answer("Введите ваш бюджет на обучение в год, руб.", reply_markup=remove_keyboard)
        await TestQuestions.balance_input.set()


async def balance_input(message: types.Message, state: FSMContext):
    bal_input = message.text.strip()
    if not bal_input.isnumeric():
        await message.answer("Введите число")
        return
    await state.update_data(balance=int(bal_input))
    await message.answer("Планируете ли Вы поступать на магистратуру?", reply_markup=decision_keyboard)
    await TestQuestions.magistracy_decision.set()


"""магистратура"""


async def magistracy_decision(message: types.Message, state: FSMContext):
    decision = message.text.lower()
    if decision not in available_decision_answer:
        await message.answer("Пожалуйста, используйте клавиатуру ниже")
        return
    if decision == "да":
        await message.answer("Важно ли для Вас наличие магистратуры на том же месте?", reply_markup=decision_keyboard)
        await TestQuestions.magistracy_place_decision.set()
    elif decision == "нет":
        await state.update_data(magistracy=False)
        await message.answer("Важна ли для Вас репутация вуза?", reply_markup=decision_keyboard)
        await TestQuestions.reputation_decision.set()


async def magistracy_place_decision(message: types.Message, state: FSMContext):
    decision = message.text.lower()
    if decision not in available_decision_answer:
        await message.answer("Пожалуйста, используйте клавиатуру ниже")
        return
    if decision == "да":
        await state.update_data(magistracy=True)
    elif decision == "нет":
        await state.update_data(magistracy=False)
    await message.answer("Важна ли для Вас репутация ВУЗа?", reply_markup=decision_keyboard)
    await TestQuestions.reputation_decision.set()


"""репутация ВУЗов"""


async def reputation_decision(message: types.Message, state: FSMContext):
    decision = message.text.lower()
    if decision not in available_decision_answer:
        await message.answer("Пожалуйста, используйте клавиатуру ниже")
        return
    if decision == "да":
        await state.update_data(reputation=True)
    elif decision == "нет":
        await state.update_data(reputation=False)
    user_id = str(message.from_user.id)
    username = message.from_user.username
    try:
        update_data(username, datetime.timestamp(datetime.now()))
    except TypeError:
        update_data(user_id, datetime.timestamp(datetime.now()))
    await TestQuestions.result.set()
    await result(message, state)


"""результат"""


async def result(message: types.Message, state: FSMContext):
    await message.answer("Опрос завершён", reply_markup=remove_keyboard)
    data = await state.get_data()
    await print_data(message, state, data)
    await print_result(message, state, data)


async def print_data(message: types.Message, state: FSMContext, data: dict):
    result_message = "<u>Сфера</u>: " + data.get("sphere") + "\n"
    result_message += "<u>Сдаваемые предметы</u>: " + "\n"
    ege = data.get("ege")
    points = data.get("ege_points")
    ege_message = ""
    for i in range(len(ege)):
        if ege[i] == None:
            ege_message += "математика (базовая)" + " - " + str(points[i]) + "\n"
        else:
            ege_message += ege[i] + " - " + str(points[i]) + "\n"
    result_message += ege_message
    result_message += "<u>Общий балл</u>: " + str(sum(points)) + "\n"
    city_list = data.get("city_list")
    if len(city_list) <= 3:
        try:
            city_list = ','.join(city_list)
        except TypeError:
            city_list = str(*city_list)
        result_message += "<u>Город</u>: " + str(city_list) + "\n"
    else:
        result_message += "<u>Город</u>: много\n"
    result_message += "<u>Бюджетные места</u>: " + ("Да" if data.get("budget_place") else "Нет") + "\n"
    if not data.get("budget_place"):
        result_message += "<u>Бюджет</u>: " + str(data.get("balance")) + "\n"
    if data.get("magistracy"):
        result_message += "<u>Магистратура</u>: " + "Да" + "\n"
        result_message += "<u>Расположение магистратуры</u>: " + ("Да" if data.get("magistracy") else "Нет") + "\n"
    else:
        result_message += "<u>Магистратура</u>: " + "Нет" + "\n"
    result_message += "<u>Репутация</u>: " + ("Да" if data.get("reputation") else "Нет") + "\n"
    await message.answer(result_message, parse_mode=types.ParseMode.HTML)


async def print_result(message: types.Message, state: FSMContext, data: dict):
    user_id = message.from_user.id
    username = message.from_user.username
    cities_res = user_properties[user_id].get("cities_res")
    specialties = processor(data)
    if len(specialties) == 0:
        await message.answer("Ничего не найдено")
        await message.answer(
            "Попробуйте пройти тест заново или обратитесь в тех. поддержку: %s" % (choice(technical_supporters_list)))
    else:
        import os
        try:
            book_message = str(data.get("sphere")) + str(data.get("ege")) + str(data.get("ege_points")) + "@" + username
        except TypeError:
            book_message = str(data.get("sphere")) + str(data.get("ege")) + str(data.get("ege_points")) + "@" + str(
                user_id)
        book_path = make_book(book_message, specialties)
        book = open(book_path, 'rb')
        await message.answer_document(book)
        book.close()
        if os.path.isfile(book_path):
            os.remove(book_path)
        city_id = 0
        for city in specialties.keys():
            cities_res.append(CityButton(city))
            university_id = 0
            for university in specialties[city].keys():
                cities_res[city_id].add_unversity(UniversityButton(university, city))
                for specialty in specialties[city][university].items():
                    specialty_key = specialty[0]
                    specialty_info = specialty[1]
                    specialty_button = SpecialtyButton(specialty_info, specialty_key, city, university)
                    cities_res[city_id].universities[university_id].add_specialty(specialty_button)
                university_id += 1
            city_id += 1
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        button = types.InlineKeyboardButton(text="Вывести", callback_data="print_result_city_list")
        keyboard.add(button)
        await message.answer("Итоги теста", reply_markup=keyboard)


def register_handlers_question(dp: Dispatcher):
    dp.register_callback_query_handler(print_subject_list, text="print_subject_list", state="*")
    dp.register_callback_query_handler(print_city_list, text="print_city_list", state=TestQuestions.city_input)
    dp.register_callback_query_handler(select_all_cities, text="select_all_cities", state=TestQuestions.city_input)
    dp.register_callback_query_handler(collapse_the_list, text="collapse_the_list", state="*")
    dp.register_callback_query_handler(print_result_city_list, text="print_result_city_list",
                                       state=TestQuestions.result)

    dp.register_callback_query_handler(callback_query_handler, state=TestQuestions.result)
    dp.register_message_handler(cmd_back, commands="back", state="*")

    dp.register_message_handler(test_start, commands="test", state="*")
    dp.register_message_handler(sphere_decision, state=TestQuestions.sphere_decision)
    dp.register_message_handler(sphere_choice, state=TestQuestions.sphere_choice)
    dp.register_message_handler(finding_sphere, state=TestQuestions.finding_sphere)
    dp.register_message_handler(sphere_answer_handler, state=TestQuestions.sphere_answer_handler)

    dp.register_message_handler(subject_question, state=TestQuestions.subject_question)
    dp.register_message_handler(subject_choice, state=TestQuestions.subject_choice)
    dp.register_message_handler(subject_decision, state=TestQuestions.subject_decision)
    dp.register_message_handler(finding_subject, state=TestQuestions.finding_subject)
    dp.register_message_handler(point_input, state=TestQuestions.point_input)

    dp.register_message_handler(city_question, state=TestQuestions.city_decision)
    dp.register_message_handler(geolocation_input, state=TestQuestions.geolocation_input)
    dp.register_message_handler(geolocation_input, content_types=types.ContentType.LOCATION,
                                state=TestQuestions.geolocation_input)
    dp.register_message_handler(city_input, state=TestQuestions.city_input)
    dp.register_message_handler(city_number_choice, state=TestQuestions.city_number_choice)
    dp.register_message_handler(radius_input, state=TestQuestions.radius_input)
    dp.register_message_handler(barrack_decision, state=TestQuestions.barrack_decision)

    dp.register_message_handler(budget_place_decision, state=TestQuestions.budget_place_decision)
    dp.register_message_handler(balance_input, state=TestQuestions.balance_input)

    dp.register_message_handler(magistracy_decision, state=TestQuestions.magistracy_decision)
    dp.register_message_handler(magistracy_place_decision, state=TestQuestions.magistracy_place_decision)

    dp.register_message_handler(reputation_decision, state=TestQuestions.reputation_decision)
