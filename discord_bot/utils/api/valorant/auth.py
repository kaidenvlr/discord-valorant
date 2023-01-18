import re

import cloudscraper
import json


class Auth:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def get_data(self):
        session = cloudscraper.create_scraper(disableCloudflareV1=True)
        data = {
            'client_id': 'play-valorant-web-prod',
            'nonce': '1',
            'redirect_uri': 'https://playvalorant.com/opt_in',
            'response_type': 'token id_token',
        }
        session.post('https://auth.riotgames.com/api/v1/authorization', json=data)

        data = {
            'type': 'auth',
            'username': self.username,
            'password': self.password,
        }
        r = session.put('https://auth.riotgames.com/api/v1/authorization', json=data)

        try:
            response = json.loads(r.text)
        except Exception as e:
            return {'error': e, 'message': 'Ошибка при подключении к вашей учетной записи'}
        pattern = re.compile(
            'access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)'
        )

        try:
            data = pattern.findall(response['response']['parameters']['uri'])[0]
        except Exception as e:
            return {'error': e, 'message': 'Неверные данные для входа'}
        access_token = data[0]

        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        r = session.post(
            'https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={})
        entitlements_token = json.loads(r.text)['entitlements_token']

        r = session.post('https://auth.riotgames.com/userinfo',
                         headers=headers, json={})
        user_id = json.loads(r.text)['sub']

        headers['X-Riot-Entitlements-JWT'] = entitlements_token
        session.close()
        return [access_token, entitlements_token, user_id]
