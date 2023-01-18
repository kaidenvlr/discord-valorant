import requests


class Player:
    def __init__(self, nickname: str, tagline: str):
        self.nickname = nickname
        self.tagline = tagline

    def elo(self):
        res = requests.get(
            f'https://api.henrikdev.xyz/valorant/v1/mmr/eu/{self.nickname}/{self.tagline}')
        response = res.json()
        if response['status'] == 200:
            player = response['data']
            current_rank = player['currenttierpatched']
            img_url = player['images']['small']
            current_elo = str(player['ranking_in_tier']) + \
                          ' / 100' if player['currenttier'] < 24 else 'MMR: ' + \
                                                                      str(player['ranking_in_tier'])
            print(img_url)

            return {
                'status': 'ok',
                'nickname': self.nickname,
                'tagline': self.tagline,
                'img_url': img_url,
                'rank': current_rank,
                'elo': current_elo
            }
        else:
            return {
                'status': 'error'
            }

    def stats(self):
        player_elo = self.elo()

        res = requests.get(
            f'https://api.henrikdev.xyz/valorant/v3/matches/eu/{self.nickname}/{self.tagline}?filter=competitive')
        response = res.json()
        adr = []
        kd = []
        acs = []

        if response['status'] == 200 and player_elo['status'] == 'ok':
            matches = response['data']
            for match in matches:
                qty_rounds = match['metadata']['rounds_played']

                players_in_match = match['players']['all_players']
                for player in players_in_match:
                    if player['name'] == self.nickname and player['tag'] == self.tagline:
                        acs.append(int(player['stats']['score'] / qty_rounds))
                        kd.append(
                            float("%.2f" % (player['stats']['kills'] / player['stats']['deaths'])))
                        adr.append(int(player['damage_made'] / qty_rounds))

            return {
                'status': 'ok',
                'nickname': self.nickname,
                'tagline': self.tagline,
                'rank': player_elo['rank'],
                'elo': player_elo['elo'],
                'img_url': player_elo['img_url'],
                'acs': int(sum(acs) / len(acs)),
                'adr': int(sum(adr) / len(adr)),
                'kd': float("%.2f" % (sum(kd) / len(kd)))
            }
        else:
            return {
                'status': 'error'
            }
