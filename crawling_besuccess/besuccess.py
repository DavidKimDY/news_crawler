import json
from bs4 import BeautifulSoup as bs
import requests
import re
import string
import numpy as np
import os
from utils import get_soup, start_from_dump, temp_dump, stop

BASE_PAGE = 'https://besuccess.com/page/{}/'
HEAD_PAGE = 'https://besuccess.com'
CORP = 'besuccess'


def parse_url(_url):
    return HEAD_PAGE+_url.attrs['href']


def parse_title(_title):
    return _title.text


def parse_thumb(_thumb):
    thumb = _thumb.attrs['style']
    thumb = re.sub('.*\(', '', thumb)
    thumb = thumb.strip(')')
    return thumb


def parse_cat(_cat):
    cats = _cat.find_all('div')
    cats = [cat.text for cat in cats]
    return cats


def parse_day(_day):
    day = _day.text
    day = day.strip(string.whitespace)
    day = re.sub('[^0-9 ]*','',day)
    day = day.replace(' ', '-')
    return day


def crawler(page_num, update, whole_data=None):
    page = BASE_PAGE.format(page_num)

    html = requests.get(page)
    soup = bs(html.content, 'html.parser')
    
    titles = soup.find_all('a', {'id':'title'})
    urls = soup.find_all('a', {'id':'title'})
    thumbs = soup.find_all('div', {'id':'image'})
    cats = soup.find_all('div', {'id':'tag_container'})
    days = soup.find_all('div', {'id':'writer'})

    one_page = []
    
    for _title, _day, _url, _thumb, _cat in zip(titles, days, urls, thumbs, cats):

        thumb = parse_thumb(_thumb)
        title = parse_title(_title)
        day = parse_day(_day)
        url = parse_url(_url)
        cat = parse_cat(_cat)
        
        obj = {'corp': CORP,
               'thumb': thumb,
               'title': title,
               'day': day,
               'url': url,
               'category': cat}

        if update and stop(obj, whole_data):
            last_page = True
            return one_page, last_page

        print(CORP, ': ', title)
        one_page.append(obj)
    last_page = True if not one_page else False

    return one_page, last_page


def besuccess_crawler(file_path):
    
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
        one_page, last_page = crawler(page_num, update=update, whole_data=data)
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
