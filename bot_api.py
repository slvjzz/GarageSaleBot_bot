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


def get_lot_buy(id):
    lot = requests.get(BASE_URL+f'/lots/{id}/buy')
    return lot.json()


def get_lot_photos(id):
    photos = requests.get(BASE_URL+f'/lots/{id}/photos')
    return photos.json()


def get_lots_by_category(id):
    lots = requests.get(BASE_URL+f'/categories/{id}')
    return lots.json()
