import json

import psycopg2


def fetch_user():
    with psycopg2.connect(
            "dbname=zhanik user=zhanik password=Executie654# host=94.247.135.210 port=5432"
    ) as conn:
        with conn.cursor() as cur:
            cur.execute('select * from "user"')
            data = cur.fetchall()
            result = {}
            for obj in data:
                cur.execute(f"""select * from "cookie" where id = '{obj[0]}'""")
                cookie = cur.fetchone()
                if cookie:
                    print(cookie)
                    result[obj[0]] = {
                        "cookie": {
                            "tdid": cookie[1],
                            "asid": cookie[2],
                            "clid": cookie[3],
                            "__cf_dm": cookie[4],
                            "ssid": cookie[5],
                            'sub': cookie[6],
                            'csid': cookie[7]
                        },
                        "access_token": obj[1],
                        "token_id": obj[2],
                        "emt": obj[3],
                        "puuid": obj[4],
                        "username": obj[5],
                        "region": obj[6],
                        "expiry_token": obj[7],
                        "notify_mode": obj[8],
                        "DM_Message": obj[9],
                    }

                with open("data/users.json", "w", encoding="utf-8") as json_file:
                    json.dump(result, json_file, indent=2, ensure_ascii=False)


def fetch_notify():
    with psycopg2.connect(
            "dbname=zhanik user=zhanik password=Executie654# host=94.247.135.210 port=5432"
    ) as conn:
        with conn.cursor() as cur:
            cur.execute('select * from "notify"')
            data = cur.fetchall()
            result = []
            for obj in data:
                result.append({
                    "id": obj[0],
                    'uuid': obj[1]
                })

            with open("data/notifys.json", "w", encoding="utf-8") as json_file:
                json.dump(result, json_file, indent=2, ensure_ascii=False)
