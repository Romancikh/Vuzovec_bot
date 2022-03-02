from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from app.data_processor import *
from aiogram.dispatcher.filters.state import State, StatesGroup


class ControlThings(StatesGroup):
    control_state = State()
    date_catch_state = State()


buttons = [
    types.InlineKeyboardButton(text="Статистика", callback_data="statistic"),
    types.InlineKeyboardButton(text="Вывести", callback_data="print_stat"),
    types.InlineKeyboardButton(text="Скачать", callback_data="download_stat"),
    types.InlineKeyboardButton(text="За сегодня", callback_data="today"),
    types.InlineKeyboardButton(text="За месяц", callback_data="month"),
    types.InlineKeyboardButton(text="За всё время", callback_data="all"),
    types.InlineKeyboardButton(text="За дату", callback_data="date"),
    types.InlineKeyboardButton(text="Свернуть", callback_data="collapse"),
    types.InlineKeyboardButton(text="Очистить", callback_data="clear_stat"),
    types.InlineKeyboardButton(text="Пользователи", callback_data="user_list")
]


def get_keyboard(button_ids):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    local_buttons = []
    for id in button_ids:
        local_buttons.append(buttons[id])
    keyboard.add(*local_buttons)
    return keyboard


async def control(callback_query: types.CallbackQuery, state: FSMContext):
    data = callback_query.data
    msg = callback_query.message
    if data == "statistic":
        await msg.edit_text("Статистика", reply_markup=get_keyboard([1, 2, 9, 7]))

    if data == "download_stat":
        file = get_data_json()
        await msg.answer_document(file, reply_markup=get_keyboard([7]))
        file.close()

    if data == "print_stat":
        await msg.edit_text("Вывести", reply_markup=get_keyboard([3, 4, 5, 6, 7]))

    if data == "today":
        await msg.answer(get_stat("today"), reply_markup=get_keyboard([7]))

    if data == "month":
        await msg.answer(get_stat("month"), reply_markup=get_keyboard([7]))

    if data == "all":
        await msg.answer(get_stat("all"), reply_markup=get_keyboard([7]))

    if data == "date":
        await msg.answer("Введите дату в формате 01.01.1971\nВведите промежуток в формате 01.01.1971-01.01.2022")
        await ControlThings.date_catch_state.set()

    if data == "collapse":
        await msg.delete()
        if msg.text == "Статистика":
            await msg.answer("Доступ получен", reply_markup=get_keyboard([0]))
        if msg.text == "Вывести":
            await msg.answer("Статистика", reply_markup=get_keyboard([1, 2, 7, 8]))

    if data == "clear_stat":
        # clear_data()
        pass

    if data == "user_list":
        user_list = get_user_list()
        await msg.answer(user_list, reply_markup=get_keyboard([7]))

def validate(date_text):
    from datetime import datetime
    try:
        datetime.strptime(date_text, '%d.%m.%Y')
        return True
    except ValueError:
        try:
            if "-" in date_text:
                dates = date_text.split("-")
                if len(dates) == 2:
                    datetime.strptime(dates[0], '%d.%m.%Y')
                    datetime.strptime(dates[1], '%d.%m.%Y')
                    return True
        except ValueError:
            return False
    return False


async def date_catch(message: types.Message, state: FSMContext):
    if validate(message.text):
        await message.answer(get_stat(message.text), reply_markup=get_keyboard([7]))
        await message.delete()
        message_id = message.message_id - 1
        chat_id = message.chat.id
        await message.bot.delete_message(chat_id, message_id)
        await ControlThings.control_state.set()
    else:
        await message.answer("Введите дату в формате 01.01.1971\nВведите промежуток в формате 01.01.1971-01.01.2022")
        return


def register_handlers_control(dp: Dispatcher):
    dp.register_callback_query_handler(control, state=ControlThings.control_state)
    dp.register_message_handler(date_catch, state=ControlThings.date_catch_state)
