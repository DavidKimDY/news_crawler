from bs4 import BeautifulSoup as bs
import numpy as np
import requests
import re
import os
import json
from crawling_mobiinside.obj import obj, page_key, headers
from utils import stop, temp_dump, start_from_dump

BASE_PAGE = 'https://www.mobiinside.co.kr/wp-admin/admin-ajax.php?td_theme_name=Newspaper&v=9.7.4'
CORP = '모바일 인사이드'


def parse_cat(_cat):
    cat = _cat.attrs['href']
    cat = re.sub('.*category|/|\\\\', '', cat)
    return cat


def parse_thumb(_thumb):
    thumb = _thumb.attrs['style']
    thumb = re.sub('.*\(|\)', '', thumb)
    thumb = thumb.replace('\\', '')
    return thumb


def parse_url(_url):
    url = _url.next.attrs['href']
    url = url.replace('\\', '')
    return url


def parse_title(_title):
    title = _title.attrs['title']
    return title


def parse_day_time(_datetime):
    datetime = _datetime.attrs['datetime']
    day = datetime.split('T')[0]
    time = datetime.split('T')[1][:5]
    return day, time


def crawler(page_num, whole_data=None):
    obj[page_key] = page_num
    my_obj = obj
    page = requests.post(BASE_PAGE, data=my_obj, headers=headers)
    page = page.text.encode('utf8')
    page = page.decode('unicode_escape')

    soup = bs(page, 'html.parser')

    urls = soup.find_all('h3', {'class': 'entry-title'})
    titles = soup.find_all('a', {'class': 'td-image-wrap'})
    datetimes = soup.find_all('time', {'class': 'entry-date'})
    thumbs = soup.find_all('span', {'class': 'entry-thumb'})
    cats = soup.find_all('a', {'class': 'td-post-category'})

    one_page = []

    for _title, _url, _thumb, _cat, _datetime in zip(titles, urls, thumbs, cats, datetimes):

        thumb = parse_thumb(_thumb)
        title = parse_title(_title)
        url = parse_url(_url)
        cat = parse_cat(_cat)
        day, time = parse_day_time(_datetime)

        obj_ = {
            'corp': CORP,
            'thumb': thumb,
            'title': title,
            'day': day,
            'time': time,
            'url': url,
            'category': cat}

        if stop(obj, whole_data):
            last_page = True
            return one_page, last_page

        print(CORP, ': ', title)
        one_page.append(obj_)
    last_page = True if not one_page else False

    return one_page, last_page


def mobileinside_crawler(file_path):
    pages = np.array([])
    page_num = 1
    last_page = False

    file_name = '{}.json'.format(CORP)
    file = os.path.join(file_path, file_name)

    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        update = True

    except FileNotFoundError:
        data = None
        update = False
        dump, page_num = start_from_dump(CORP)

        if dump:
            pages = np.append(dump, pages)

    while not last_page:
        one_page, last_page = crawler(page_num, whole_data=data)
        if one_page:
            pages = np.append(pages, one_page)
            page_num += 1
            temp_dump(pages, page_num, CORP, update)
    if data:
        pages = np.append(pages, data)

    pages = pages.tolist()
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(pages, f, indent='\t', ensure_ascii=False)
    print(CORP, ' Done')
