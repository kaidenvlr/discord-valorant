import json

import requests


def hug_gif():
    response = requests.get('https://some-random-api.ml/animu/hug')
    json_data = json.loads(response.text)
    return json_data['link']


def pat_gif():
    response = requests.get('https://some-random-api.ml/animu/pat')
    json_data = json.loads(response.text)
    return json_data['link']
