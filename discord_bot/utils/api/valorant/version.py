import json

import requests


def get_version():
    version_data = requests.get("https://valorant-api.com/v1/version")
    version_data_json = json.loads(version_data.text)['data']
    final = f"{version_data_json['branch']}-shipping-{version_data_json['buildVersion']}-{version_data_json['version'][-6:]}"
    return final
