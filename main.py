import requests
from pprint import pprint
from config import tk_energy_key

def search_city(idCityFrom, type):
    try:
        r = requests.get(
            f"https://api2.nrg-tk.ru/v2/pricesCity?idCityFrom={idCityFrom}&idTripType={type}"
        )
        data = r.json()
        pprint(data)

        
    except Exception as ex:
        print(ex)
        print("Проверьте почтовый индекс")


def login(user, password):
    try:
        r = requests.get(
            f"https://mainapi.nrg-tk.ru/v3/login?user={user}&password={password}", headers={'NrgApi-DevToken': tk_energy_key}
        )
        data = r.json()
        pprint(data)

        
    except Exception as ex:
        print(ex)
        print("Проверьте данные")


def sss():
    try:
        r = requests.get(
            f"https://mainapi.nrg-tk.ru/v3/currency", headers={'NrgApi-DevToken': tk_energy_key}
        )
        data = r.json()
        n = 15
        for c in n:
            pprint(data[0]['title'])


        
    except Exception as ex:
        print(ex)
        print("Проверьте данные")


def main():
    #user = input("Введите логин: ")
    #password = input("Введите пароль: ")
    #login(user, password)
    sss()


if __name__ == '__main__':
    main()
