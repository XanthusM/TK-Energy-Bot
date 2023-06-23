from aiogram.dispatcher.filters.state import StatesGroup, State


class Login(StatesGroup):
    Q1 = State()
    Q2 = State()

class Logout(StatesGroup):
    Q1 = State()
    Q2 = State()
    Q3 = State()

class Search_city(StatesGroup):
    Q1 = State()

class Limits(StatesGroup):
    Q1 = State()
    Q2 = State()

class PricesCity(StatesGroup):
    Q1 = State()
    Q2 = State()

class Extraservices(StatesGroup):
    Q1 = State()

class Triplist(StatesGroup):
    Q1 = State()
    Q2 = State()
