import requests
#TEST
BASE_URL = 'http://127.0.0.1:5000/bot'


def get_home():
    home = requests.get(BASE_URL+'/lots')
    return home.json()
