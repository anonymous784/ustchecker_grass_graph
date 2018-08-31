import re
from pathlib import Path
from uuid import uuid4
from datetime import datetime, date, timedelta, timezone
import requests
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup
from flask import request, send_file


JST = timezone(timedelta(hours=9))


def hello_world(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/0.12/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    if request.args and 'message' in request.args:
        return request.args.get('message')
    elif request_json and 'message' in request_json:
        return request_json['message']
    else:
        return f'Hello World!'


def _generate_grass_image(id=None, username=None, bc_data=None, dummy=False):
    IMG_SIZE = (580, 140)
    BG_COLOR = (255, 255, 255)

    TEXT_COLOR = (0, 0, 0)

    BOX_OFFSET = (30, 50)  # px
    BOX_DIFF = (10, 10)  # px
    BOX_SIZE = 8  # px
    BOX_COLOR1 = (235, 237, 240)  # 0h /day
    BOX_COLOR2 = (204, 226, 149)  # 0h - 2h /day
    BOX_COLOR3 = (141, 198, 121)  # 2h - 6h /day
    BOX_COLOR4 = (75, 151, 71)  # 6h - 12h /day
    BOX_COLOR5 = (48, 95, 46)  # 12h - 24h /day

    def set_font(size=12):
        font = ImageFont.truetype(
            str(Path(__file__).parent.joinpath('misaki_gothic.ttf').resolve()),
            size=size
        )
        return font

    fn = f'/tmp/{uuid4().hex}.jpg'

    im = Image.new('RGB', IMG_SIZE, color=BG_COLOR)
    draw = ImageDraw.Draw(im)

    if dummy is True:

        x, y = BOX_OFFSET
        draw.text(
            (x, y),
            f"NOT FOUND ID = {id}",
            fill=TEXT_COLOR,
            font=set_font(32)
        )
        im.save(fn)
        return fn

    # draw boxes
    end_date = date.today()
    start_date = date(end_date.year - 1, end_date.month, end_date.day)
    start_date = start_date - timedelta(days=start_date.isoweekday())

    x, y = BOX_OFFSET
    dt = start_date
    while dt <= end_date:
        if dt in bc_data:
            if bc_data[dt] < 60 * 2:
                box_color = BOX_COLOR2
            elif 60 * 2 <= bc_data[dt] < 60 * 6:
                box_color = BOX_COLOR3
            elif 60 * 6 <= bc_data[dt] < 60 * 12:
                box_color = BOX_COLOR4
            else:
                box_color = BOX_COLOR5
        else:
            box_color = BOX_COLOR1
        draw.rectangle(
            (x, y, x + BOX_SIZE, y + BOX_SIZE),
            fill=box_color
        )

        dt += timedelta(days=1)
        if dt.isoweekday() == 7:
            x += BOX_DIFF[0]
            y = BOX_OFFSET[1]
        else:
            y += BOX_DIFF[1]

    # draw text
    # week day
    x, y = BOX_OFFSET
    x -= BOX_DIFF[0] * 2
    y += BOX_DIFF[1]
    _weekday = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat')
    for i in range(1, 7, 2):
        draw.text(
            (x, y),
            _weekday[i],
            fill=TEXT_COLOR,
            font=set_font(12)
        )
        y += BOX_DIFF[1] * 2

    # month
    x, y = BOX_OFFSET
    y -= BOX_DIFF[1] * 1.5
    dt = start_date
    while dt <= end_date:
        if dt.day <= 7:
            draw.text(
                (x, y),
                f"{dt:%b}",
                fill=TEXT_COLOR,
                font=set_font(12)
            )
        dt += timedelta(days=7)
        x += BOX_DIFF[0]

    # username
    x, y = BOX_OFFSET
    y -= BOX_DIFF[1] * 4
    draw.text(
        (x, y),
        f'{username} の過去１年間の配信記録',
        fill=TEXT_COLOR,
        font=set_font(18)
    )

    # legend
    # box
    x, y = BOX_OFFSET
    x += 430
    y -= BOX_DIFF[1] * 3
    for c in (BOX_COLOR1, BOX_COLOR2, BOX_COLOR3, BOX_COLOR4, BOX_COLOR5):
        draw.rectangle(
            (x, y, x + BOX_SIZE, y + BOX_SIZE),
            fill=c
        )
        x += BOX_DIFF[0] * 2

    # text
    x, y = BOX_OFFSET
    x += 430
    y -= BOX_DIFF[1] * 4.3
    for t in ('0h', '~2h', '~6h', '~12h', ' ~24h'):
        draw.text(
            (x, y),
            t,
            fill=TEXT_COLOR,
            font=set_font(12)
        )
        x += BOX_DIFF[0] * 1.5

    x, y = BOX_OFFSET
    x += 400
    y += BOX_DIFF[1] * 7.5
    draw.text(
        (x, y),
        "inspired by github.com",
        fill=TEXT_COLOR,
        font=set_font(12)
    )

    im.save(fn)
    return fn


def _scrape_ustchecker(id=None):
    def parse_to_datetime(dt_text):
        mo = re.search(
            r'(\d{2})/(\d{2})/(\d{2}).*(\d{2}):(\d{2})',
            dt_text
        )
        if mo:
            year = int('20' + mo[1])
            month = int(mo[2])
            day = int(mo[3])
            hour = int(mo[4])
            minute = int(mo[5])
            return datetime(year, month, day, hour, minute)
        else:
            return None

    username = None
    bc_data = {}

    url = f'https://revinx.net/ustream/history/?id={id}'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html5lib')
    try:
        username = re.search(r'(.+)さんの配信履歴 - Ustream Checke', soup.title.text)[1]
        rows = soup.find_all('table', id='log')[1].find_all('tr')
    except Exception as e:
        print(e)
        return username, bc_data

    for row in rows:
        d = row.find_all('td')
        if d:
            begin_dt = parse_to_datetime(d[0].text)
            end_dt = parse_to_datetime(d[1].text)
            if begin_dt is not None and end_dt is None:
                end_dt = datetime.now(JST).replace(tzinfo=None)
            if begin_dt.day != end_dt.day:
                td = (datetime(
                    begin_dt.year, begin_dt.month, begin_dt.day,
                    23, 59, 59
                ) - begin_dt).seconds / 60
                if bc_data.get(begin_dt.date()):
                    bc_data[begin_dt.date()] += td
                else:
                    bc_data[begin_dt.date()] = td

                td = (end_dt - datetime(
                    end_dt.year, end_dt.month, end_dt.day,
                    0, 0, 0
                )).seconds / 60
                if bc_data.get(end_dt.date()):
                    bc_data[end_dt.date()] += td
                else:
                    bc_data[end_dt.date()] = td
                days = end_dt.day - begin_dt.day

                if days > 1:
                    for i in range(1, days):
                        dt = begin_dt.date() + timedelta(days=1)
                        bc_data[dt] = 24 * 60
            else:
                bc_data[begin_dt.date()] = (end_dt - begin_dt).seconds / 60

    return username, bc_data


def grass_image_view(request):
    if request.args and 'id' in request.args:
        id = request.args.get('id')
    else:
        return f"ID IS REQUIRED"
    username, bc_data = _scrape_ustchecker(id=id)
    if bc_data:
        img_fn = _generate_grass_image(id, username, bc_data)
    else:
        img_fn = _generate_grass_image(id, dummy=True)
    return send_file(img_fn, mimetype='image/jpg')
