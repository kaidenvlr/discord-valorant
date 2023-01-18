import requests
import json

from discord_bot.utils.api.valorant import version


def price_convert(skin_uuid, offers_data):
    for row in offers_data["Offers"]:
        if row["OfferID"] == skin_uuid:
            for cost in row["Cost"]:
                return row["Cost"][cost]


class User:
    def __init__(self, entitlements_token, access_token, user_id):
        self.entitlements_token = entitlements_token
        self.access_token = access_token
        self.user_id = user_id

    def skins(self, locale: str):
        headers = {
            'X-Riot-Entitlements-JWT': self.entitlements_token,
            'Authorization': f'Bearer {self.access_token}',
        }

        r = requests.get(
            f'https://pd.eu.a.pvp.net/store/v2/storefront/{self.user_id}', headers=headers)

        skins_data = json.loads(r.text)
        single_skins = skins_data["SkinsPanelLayout"]["SingleItemOffers"]

        weapon_fetch = requests.get(
            f'https://valorant-api.com/v1/weapons/skinlevels')
        weapon_fetch = json.loads(weapon_fetch.text)

        all_weapons = requests.get("https://valorant-api.com/v1/weapons")
        data_weapons = json.loads(all_weapons.text)

        single_skins_tiers_uuids = []

        for skin in single_skins:
            for weapons_list in data_weapons['data']:
                for skin1 in weapons_list['skins']:
                    if skin in str(skin1):
                        single_skins_tiers_uuids.append(skin1['contentTierUuid'])

        locale_fetch = requests.get(
            f"https://api.henrikdev.xyz/valorant/v1/content?locale={locale}")
        locale_fetch = json.loads(locale_fetch.text)['skinLevels']

        localized_names = []

        for skin in single_skins:
            for localized in locale_fetch:
                if skin.upper() in str(localized):
                    localized_names.append(localized['name'])

        headers = {
            'X-Riot-Entitlements-JWT': self.entitlements_token,
            'Authorization': f'Bearer {self.access_token}',
            'X-Riot-ClientVersion': version.get_version(),
            "X-Riot-ClientPlatform": "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9"
                                     "ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2"
                                     "lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkic"
                                     "GxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"
        }

        data = requests.get(
            f"https://pd.eu.a.pvp.net/store/v1/offers/", headers=headers)

        offers_data = json.loads(data.text)

        daily_reset = skins_data["SkinsPanelLayout"]["SingleItemOffersRemainingDurationInSeconds"]

        skin_counter = 0

        result = []
        for skin in single_skins:
            for row in weapon_fetch["data"]:
                if skin == row["uuid"]:
                    result.append({
                        'name': localized_names[skin_counter],
                        'image': row['displayIcon'],
                        'price': price_convert(skin, offers_data),
                        'tier': f"https://media.valorant-api.com/contenttiers/"
                                f"{single_skins_tiers_uuids[skin_counter]}/displayicon.png",
                        'tier_id': single_skins_tiers_uuids[skin_counter]
                    })
                    skin_counter += 1
        skins_list = [result, daily_reset]

        return skins_list
