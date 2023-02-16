from pathlib import Path
import os

import discord
import requests
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from bs4 import BeautifulSoup

AVATAR_DIR = os.path.join(Path(__file__).resolve().parent.parent.parent, 'media/avatars/')
FONT_DIR = os.path.join(Path(__file__).resolve().parent.parent.parent, 'media/fonts/')
PROFILE_DIR = os.path.join(Path(__file__).resolve().parent.parent.parent, 'media/profiles/')
RANK_DIR = os.path.join(Path(__file__).resolve().parent.parent.parent, 'media/ranks/')
TEMPLATE_DIR = os.path.join(Path(__file__).resolve().parent.parent.parent, 'media/templates/')


def crop_center(pil_img, crop_width, crop_height):
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


def crop_max_square(pil_img):
    return crop_center(pil_img, min(pil_img.size), min(pil_img.size))


def mask_circle_transparent(pil_img, blur_radius, offset=0):
    offset = blur_radius * 2 + offset
    mask = Image.new("L", pil_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

    result = pil_img.copy()
    result.putalpha(mask)

    return result


def tracker_current_season(name: str, tag: str):
    url = f"https://tracker.gg/valorant/profile/riot/{name}%23{tag}/overview"
    site = requests.get(url)
    print("curr_season", site.status_code)

    if site.status_code == 200:
        soup = BeautifulSoup(site.text, "html.parser")

        result = {"status_code": "ok"}
        labels = ['current_rank', 'max_rank', 'adr', 'kd', 'hs', 'winrate']
        i = 0
        containers = soup.findAll('div', class_="rating-content")
        if containers == []:
            result['status_code'] = 410
        else:
            for rank in containers:
                result[labels[i]] = {
                    'img': rank.find('img')['src'],
                    'value': rank.find('div', class_='value').text.strip()
                }
                i += 1

            for stat in soup.findAll('div', class_="stat align-left giant expandable"):
                result[labels[i]] = stat.find('span', class_="value").text
                i += 1
        return result

    elif site.status_code == 403:
        return {"status_code": 403}

    elif site.status_code == 451:
        return {"status_code": 404}

    else:
        return {"status_code": 1000}


def tracker_all_seasons(name: str, tag: str):
    url = f"https://tracker.gg/valorant/profile/riot/{name}%23{tag}/overview?season=all"
    site = requests.get(url)

    if site.status_code == 200:
        soup = BeautifulSoup(site.text, "html.parser")

        result = {"status_code": "ok"}
        labels = ['current_rank', 'max_rank', 'adr', 'kd', 'hs', 'winrate']
        i = 0
        containers = soup.findAll('div', class_="rating-content")
        print(containers)
        if containers == []:
            result['status_code'] = 410
        else:
            for rank in containers:
                result[labels[i]] = {
                    'img': rank.find('img')['src'],
                    'value': rank.find('div', class_='value').text.strip()
                }
                i += 1

            for stat in soup.findAll('div', class_="stat align-left giant expandable"):
                result[labels[i]] = stat.find('span', class_="value").text
                i += 1

        return result

    elif site.status_code == 403:
        return {"status_code": 403}

    elif site.status_code == 451:
        return {"status_code": 404}

    else:
        return {"status_code": 1000}


def tracker_profile(nickname: str, tag: str, user: discord.User):
    response_current_season = tracker_current_season(nickname, tag)
    response_all_seasons = tracker_all_seasons(nickname, tag)
    result = {}
    print("all_season", response_all_seasons['status_code'])

    if response_current_season['status_code'] == 'ok' and response_all_seasons['status_code'] == 'ok':
        result['status'] = 'ok'

        image = str(user.display_avatar)
        response = requests.get(image)
        if response.status_code:
            fp = open(f'{AVATAR_DIR}/{user.id}.png', 'wb')
            fp.write(response.content)
            fp.close()

        avatar = Image.open(f'{AVATAR_DIR}/{user.id}.png')

        im_square = crop_max_square(avatar).resize((400, 400), Image.LANCZOS)
        im_thumb = mask_circle_transparent(im_square, 4)

        if user.id == 590235051413864489:
            template = Image.open(f'{TEMPLATE_DIR}/kaiden.png')
            stroke_color = (119, 248, 226)
        elif user.id == 774310787404660786 or user.id == 1074370459761651732:
            template = Image.open(f'{TEMPLATE_DIR}/alisha.png')
            stroke_color = (255, 151, 220)
        elif user.id == 594909272358256640:
            template = Image.open(f'{TEMPLATE_DIR}/fairsoul.png')
            stroke_color = (186, 106, 235)
        else:
            template = Image.open(f'{TEMPLATE_DIR}/image.png')
            stroke_color = (254, 71, 99)
        curr_rank = RANK_DIR + response_current_season['current_rank']['img'].split('/')[-1]
        max_rank = RANK_DIR + response_current_season['max_rank']['img'].split('/')[-1]

        rank1 = Image.open(curr_rank).resize((120, 120), Image.LANCZOS)
        rank2 = Image.open(max_rank).resize((120, 120), Image.LANCZOS)
        template.paste(im_thumb, (448, 329), im_thumb)
        template.paste(rank1, (92, 90), rank1)
        template.paste(rank2, (1090, 90), rank2)

        template_editable = ImageDraw.Draw(template)

        font_stats = ImageFont.truetype(f'{FONT_DIR}/Inter/static/Inter-Bold.ttf', 28)

        template_editable.text((339, 363), response_current_season['kd'], (255, 255, 255), font=font_stats, anchor='ra')
        template_editable.text((339, 463), response_current_season['winrate'], (255, 255, 255), font=font_stats,
                               anchor='ra')
        template_editable.text((339, 563), response_current_season['hs'], (255, 255, 255), font=font_stats, anchor='ra')
        template_editable.text((339, 663), response_current_season['adr'], (255, 255, 255), font=font_stats,
                               anchor='ra')

        template_editable.text((1218, 363), response_all_seasons['kd'], (255, 255, 255), font=font_stats, anchor='ra')
        template_editable.text((1218, 463), response_all_seasons['winrate'], (255, 255, 255), font=font_stats,
                               anchor='ra')
        template_editable.text((1218, 563), response_all_seasons['hs'], (255, 255, 255), font=font_stats, anchor='ra')
        template_editable.text((1218, 663), response_all_seasons['adr'], (255, 255, 255), font=font_stats, anchor='ra')

        font_nickname = ImageFont.truetype(f'{FONT_DIR}/Inter/static/Inter-Black.ttf', 50)

        template_editable.text((651, 150), f"{user.name.upper()}#{user.discriminator}", font=font_nickname,
                               anchor='mm', stroke_width=1, stroke_fill=stroke_color)

        template.save(f'{PROFILE_DIR}/profile-{user.id}.png')
        result['img'] = f'{PROFILE_DIR}/profile-{user.id}.png'

    elif response_current_season['status_code'] == 404 or response_all_seasons['status_code'] == 404:
        result['status'] = 'error'
        result['embed'] = discord.Embed(title="", description="вы не зарегистрированы в tracker.gg")
    elif response_current_season['status_code'] == 403 or response_all_seasons['status_code'] == 403:
        result['status'] = 'error'
        result['embed'] = discord.Embed(title="", description="ошибка парсинга данных")
    elif response_current_season['status_code'] == 410 or response_all_seasons['status_code'] == 410:
        result['status'] = 'error'
        result['embed'] = discord.Embed(title="",
                                        description="вы еще не играли рейтинговые игры, потому статистика недоступна")
    else:
        result['status'] = 'error'
        result['embed'] = discord.Embed(title="", description="возникла неизвестная ошибка, попробуйте позднее")

    return result
