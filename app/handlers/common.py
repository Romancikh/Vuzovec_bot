from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
import app.handlers.control

keyboard_remove = types.ReplyKeyboardRemove()
admins_list = [626805724, 810906912, 1059612952]


async def cmd_start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Здравствуйте!")
    await message.answer("Чтобы приступить к тесту исползуйте команду /test", reply_markup=keyboard_remove)


async def cmd_stop(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Тест принудительно завершён", reply_markup=keyboard_remove)


async def cmd_help(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Тех. поддержка:\n@romankutimskiy\n@white_tears_of_autumn\n@Artyomeister",
                         reply_markup=keyboard_remove)


async def cmd_info(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Этот бот поможет Вам определиться с выбором вуза после небольшого теста.\n"
                         "Бот использует информацию из открытого источника vuzoteka.ru\n"
                         "Оставить отзыв: qiwi.com/n/ROMANCIKH", reply_markup=keyboard_remove)


async def admin_panel(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    if user_id in admins_list:
        await message.answer("Доступ получен", reply_markup=app.handlers.control.get_keyboard([0]))
        await app.handlers.control.ControlThings.control_state.set()
    else:
        await state.finish()
        await message.answer("У вас нет доступа к этому разделу!", reply_markup=keyboard_remove)


def register_handlers_common(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands="start", state="*")
    dp.register_message_handler(cmd_stop, commands="stop", state="*")
    dp.register_message_handler(cmd_help, commands="help", state="*")
    dp.register_message_handler(cmd_info, commands="info", state="*")
    dp.register_message_handler(admin_panel, commands="admin_panel", state="*")
