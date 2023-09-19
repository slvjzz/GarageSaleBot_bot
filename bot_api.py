import requests

BASE_URL = 'http://127.0.0.1:5000/bot'


def get_lots():
    home = requests.get(BASE_URL+'/lots')
    return home.json()


def get_categories():
    print('GET')
    categories = requests.get(BASE_URL+'/categories')
    return categories.json()


def get_lot(id):
    lot = requests.get(BASE_URL+f'/lots/{id}')
    return lot.json()
