import json

import psycopg2


def backup_users():
    with psycopg2.connect(
            "dbname=zhanik user=zhanik password=Executie654# host=94.247.135.210 port=5432"
    ) as conn:
        with conn.cursor() as cur:
            cur.execute('delete from "user"')
            with open('data/users.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                for key in data.keys():
                    query = """
                    insert into "user" values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', %f, '%s', '%s')
                    """ % (
                        str(key),
                        data[key]['access_token'],
                        data[key]['token_id'],
                        data[key]['emt'],
                        data[key]['puuid'],
                        data[key]['username'],
                        data[key]['region'],
                        data[key]['expiry_token'],
                        data[key]['notify_mode'],
                        data[key]['DM_Message']
                    )
                    cur.execute(query)
                    conn.commit()


def backup_cookie():
    with psycopg2.connect(
            "dbname=zhanik user=zhanik password=Executie654# host=94.247.135.210 port=5432"
    ) as conn:
        with conn.cursor() as cur:
            cur.execute('delete from "cookie"')
            with open('data/users.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                for key in data.keys():
                    query = """
                                    insert into "cookie" values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')
                                    """ % (
                        str(key),
                        data[key]['cookie']['tdid'],
                        data[key]['cookie']['asid'],
                        data[key]['cookie']['clid'],
                        data[key]['cookie']['__cf_bm'],
                        data[key]['cookie']['ssid'],
                        data[key]['cookie']['sub'],
                        data[key]['cookie']['csid']
                    )
                    cur.execute(query)


def backup_notify():
    with psycopg2.connect(
            "dbname=zhanik user=zhanik password=Executie654# host=94.247.135.210 port=5432"
    ) as conn:
        with conn.cursor() as cur:
            cur.execute('delete from "notify"')
            with open('data/notifys.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                for obj in data:
                    query = """insert into notify values ('%s', '%s')""" % (obj['id'], obj['uuid'])
                    print(query)
                    cur.execute(query)
