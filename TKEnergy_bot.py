import requests
from config import tk_bot_key, tk_energy_key
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo
import markups as nav
import logging
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import json
from db import Database
import functions as fc


bot = Bot(token=tk_bot_key, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )

from states.allstates import Search_city, Limits, PricesCity, Extraservices, Triplist, Login, Logout
db = Database('database.db')



@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await bot.send_message(message.from_user.id, "Здравствуйте {0.first_name}!".format(message.from_user))
    await message.answer("Пожалуйста зарегистрируйтесь на нашем сайте и введите команду /login",
reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="Регистрация",
web_app=WebAppInfo(url="https://clients.nrg-tk.ru/user/register", callback_data="calculate"))))


@dp.message_handler(commands="calculate")
async def cmd_calculate(message: types.Message):
    await message.answer("Перейдите в наш калькулятор",
reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="Калькулятор",
web_app=WebAppInfo(url="https://nrg-tk.ru/client/calculator/", callback_data="calculate"))))


@dp.message_handler(commands="tracking")
async def cmd_tracking(message: types.Message):
    await message.answer("Перейдите на наш сайт",
reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="Отслеживание груза",
web_app=WebAppInfo(url="https://nrg-tk.ru/client/tracking/", callback_data="tracking"))))
    

@dp.message_handler(commands="application")
async def cmd_application(message: types.Message):
    await message.answer("Перейдите для оформления заявки",
reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="Заполнение онлайн формы",
web_app=WebAppInfo(url="https://nrg-tk.ru/client/online-application-form/", callback_data="application"))))


# -------- Команда Help -------------

@dp.message_handler(commands="help")
async def cmd_help(message: types.Message):
    await message.answer("Список всех доступных команд:\n"
                         "/search - Узнать id города с помощью почтового индекса \n"
                         "/limits - Метод возвращает информацию о предельных значениях перевозимого груза по местам, весу, объему, длине стороны. \n"
                         "/pricesCity - Возвращает список цен для города откуда и типа рейса. \n"
                         "/extraservices - Возвращает список цен для города откуда и типа рейса. \n"
                         "/cities - Возвращает список городов \n"
                         "/triplist - Получить список типов доступных перевозок \n"
                         "/currency - Список доступных валют к оплате \n"
                         "/logout - Выйти из системы")
    

# -------- Команда login -------------
@dp.message_handler(Command("login"), state=None)
async def enter_login(message: types.Message):
    await message.answer("Пожалуйста введите ваш логин:")
    await Login.Q1.set()

@dp.message_handler(state=Login.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    answer = message.text

    # Вариант 1 сохранения переменных - записываем через key=var
    await state.update_data(answer1=answer)

    await message.answer("Введите пароль:")

    await Login.next()

@dp.message_handler(state=Login.Q2)
async def answer_q2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    answer1 = data.get("answer1")
    answer2 = message.text

    try:
        r = requests.get(
            f"https://mainapi.nrg-tk.ru/v3/login?user={answer1}&password={answer2}", headers={'NrgApi-DevToken': tk_energy_key}
        )
        
    except:
        await message.reply("Что-то пошло не так")

    data = r.json()
    token = data['token']
    accountId = data['accountId']
    await message.answer(f"Токен вашей сессии: {token}")
    await message.answer(f"Id вашего аккаунта: {accountId}")
    await state.finish()


# -------- Команда logout -------------

@dp.message_handler(Command("logout"), state=None)
async def enter_login(message: types.Message):
    await message.answer("Пожалуйста введите Id аккаунта:")
    await Logout.Q1.set()


@dp.message_handler(state=Logout.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    answer = message.text

    # Вариант 1 сохранения переменных - записываем через key=var
    await state.update_data(answer1=answer)

    await message.answer("Введите Токен:")

    await Logout.next()


@dp.message_handler(state=Logout.Q2)
async def answer_q1(message: types.Message, state: FSMContext):
    answer = message.text

    # Вариант 1 сохранения переменных - записываем через key=var
    await state.update_data(answer2=answer)

    await message.answer("Хотите ли вы закончить все сессии? Если да, введите true, если нет, то введите false")

    await Logout.next()


@dp.message_handler(state=Logout.Q3)
async def answer_q2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    answer1 = data.get("answer1")
    answer2 = data.get("answer2")
    answer3 = message.text

    try:
        r = requests.get(
            f"https://mainapi.nrg-tk.ru/v3/{answer1}/logout?token={answer2}%3D&allSessions={answer3}", headers={'NrgApi-DevToken': tk_energy_key}
        )
        
    except:
        await message.reply("Что-то пошло не так")

    await state.finish()
    await message.answer("Вы успешно вышли из системы!")

    
# -------- Команда SEARCH_CITY -------------

@dp.message_handler(Command("search"), state=None)
async def enter_search(message: types.Message):
    await message.answer("Чтобы узнать id и название города, пожалуйста, напишите почтовый индекс")
    await Search_city.Q1.set()


@dp.message_handler(state=Search_city.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    answer1 = message.text

    try:
        r = requests.get(
            f"https://mainapi.nrg-tk.ru/v3/search/city?zipCode={answer1}", headers={'NrgApi-DevToken': tk_energy_key}
        )
        data = r.json()

        idcity = data['id']

        await message.reply(f"Id вашего города: {idcity}")
        
    except:
        await message.reply("Проверьте почтовый индекс")

    await state.finish()


# -------- Команда Currency -------------

@dp.message_handler(commands="currency")
async def enter_currency(message: types.Message):
    try:
        r = requests.get(
            f"https://mainapi.nrg-tk.ru/v3/currency", headers={'NrgApi-DevToken': tk_energy_key}
        )
        data = r.json()
        val1 = data[0]
        name1 = val1['title']
        val2 = data[1]
        name2 = val2['title']
        val3 = data[2]
        name3 = val3['title']
        val4 = data[3]
        name4 = val4['title']
        val5 = data[4]
        name5 = val5['title']
        val6 = data[5]
        name6 = val6['title']

        await message.answer(f"Доступные валюты к оплате: {name1}, {name2}, {name3}, {name4}, {name5}, {name6}")
        
    except:
        await message.reply("Что-то пошло не так")


# -------- Команда price/limits -------------

@dp.message_handler(Command("limits"), state=None)
async def enter_limits(message: types.Message):
    await message.answer("Пожалуйста напишите id города отправления")
    await Limits.Q1.set()


@dp.message_handler(state=Limits.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    answer = message.text

    # Вариант 1 сохранения переменных - записываем через key=var
    await state.update_data(answer1=answer)

    await message.answer("Пожалуйста напишите id города получения")

    await Limits.next()


@dp.message_handler(state=Limits.Q2)
async def answer_q2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    answer1 = data.get("answer1")
    answer2 = message.text

    try:
        r = requests.get(
            f"https://mainapi.nrg-tk.ru/v3/price/limits?idCityFrom={answer1}&idCityTo={answer2}", headers={'NrgApi-DevToken': tk_energy_key}
        )
        data = r.json()
        await message.reply(data)
        
    except:
        await message.reply("Что-то пошло не так")

    await state.finish()


# -------- Команда pricesCity -------------

@dp.message_handler(Command("pricesCity"), state=None)
async def enter_prices(message: types.Message):
    await message.answer("Пожалуйста напишите id города отправления")
    await PricesCity.Q1.set()


@dp.message_handler(state=PricesCity.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    answer = message.text

    # Вариант 1 сохранения переменных - записываем через key=var
    await state.update_data(answer1=answer)

    await message.answer("Пожалуйста напишите id типа рейса")

    await PricesCity.next()


@dp.message_handler(state=PricesCity.Q2)
async def answer_q2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    answer1 = data.get("answer1")
    answer2 = message.text

    try:
        r = requests.get(
            f"https://mainapi.nrg-tk.ru/v3/pricesCity?idCityFrom={answer1}&idTripType={answer2}", headers={'NrgApi-DevToken': tk_energy_key}
        )
        data = r.json()
        await message.reply(data)
        
    except:
        await message.reply("Что-то пошло не так")

    await state.finish()


# -------- Команда extraservices -------------

@dp.message_handler(Command("extraservices"), state=None)
async def enter_extraservices(message: types.Message):
    await message.answer("Пожалуйста, напишите id города")
    await Extraservices.Q1.set()


@dp.message_handler(state=Extraservices.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    answer1 = message.text

    try:
        r = requests.get(
            f"https://mainapi.nrg-tk.ru/v3/cities/{answer1}/extraservices", headers={'NrgApi-DevToken': tk_energy_key}
        )
        data = r.json()
        await message.reply(data)
        
    except:
        await message.reply("Неверный id города")

    await state.finish()


# -------- Команда Cities -------------

@dp.message_handler(commands="cities")
async def enter_cities(message: types.Message):
    try:
        r = requests.get(
            f"https://mainapi.nrg-tk.ru/v3/cities?lang=ru", headers={'NrgApi-DevToken': tk_energy_key}
        )
        data = r.json()
        await message.reply(data)
        
    except:
        await message.reply("Что-то пошло не так")


# -------- Команда triplist -------------

@dp.message_handler(Command("triplist"), state=None)
async def enter_triplist(message: types.Message):
    await message.answer("Пожалуйста, напишите id города отправления")
    await Triplist.Q1.set()


@dp.message_handler(state=Triplist.Q1)
async def answer_q1(message: types.Message, state: FSMContext):
    answer = message.text

    # Вариант 1 сохранения переменных - записываем через key=var
    await state.update_data(answer1=answer)

    await message.answer("Пожалуйста напишите id города получения")

    await Triplist.next()


@dp.message_handler(state=Triplist.Q2)
async def answer_q2(message: types.Message, state: FSMContext):
    data = await state.get_data()
    answer1 = data.get("answer1")
    answer2 = message.text

    try:
        r = requests.get(
            f"https://mainapi.nrg-tk.ru/v3/triplist?idCityFrom={answer1}&idCityTo={answer2}", headers={'NrgApi-DevToken': tk_energy_key}
        )
        data = r.json()
        await message.reply(data)
        
    except:
        await message.reply("Что-то пошло не так")

    await state.finish()


@dp.message_handler()
async def message_output(message: types.Message):
    answer_id = fc.recognize_question(message.text, db.get_questions())
    await bot.send_message(message.from_user.id, db.get_answer(answer_id))



if __name__ == '__main__':
    executor.start_polling(dp)