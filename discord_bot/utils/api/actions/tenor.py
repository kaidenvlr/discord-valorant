import json
import random

import requests

from discord_bot.config import load_config


class Tenor:
    def __init__(self, action):
        self.token = load_config(".env").bot.tenor
        self.action = action

    def find(self):
        random_int = random.randint(0, 50)
        response = requests.get(
            'https://g.tenor.com/v1/search?q=%s&key=%s&limit=%s' % (self.action, self.token, 50))
        return json.loads(response.content)['results'][random_int]['media'][0]['gif']['url']
