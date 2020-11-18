import requests
from bs4 import BeautifulSoup as bs
import json
import numpy as np
import os
from utils import start_from_dump, temp_dump, stop

main_page = 'https://it.donga.com/news/?page={}'
url_head = 'https://it.donga.com'
page = main_page.format(400)
html = requests.get(page)
soup = bs(html.content, 'html.parser')
corp = soup.head.title.text


def parse_title(_title):
    title = str(_title.text)
    title = title.split('\n')[1].strip()
    return title


def parse_thumb(_thumb):
    thumb = str(_thumb)
    thumb = thumb.split('\"')[5]
    thumb = url_head+thumb
    return thumb


def parse_day(_day):
    return _day.text


def parse_url(_url):
    url = _url.attrs['href']
    url = url_head + url
    return url


def crawler(page_num, whole_data=None):
    page = main_page.format(page_num)

    html = requests.get(page)
    soup = bs(html.content, 'html.parser')
    
    corp = soup.head.title.text
    titles = soup.select('.mt-0')
    thumbs = soup.select('.media img')
    days = soup.find_all('time')
    urls = soup.find_all('a', class_='media')

    one_page = []
    
    for _title, _day, _url, _thumb in zip(titles, days, urls, thumbs):

        thumb = parse_thumb(_thumb)
        title = parse_title(_title)
        day = parse_day(_day)
        url = parse_url(_url)
        
        obj = {'corp': corp,
               'thumb': thumb,
               'title': title,
               'day': day,
               'url': url}

        if stop(obj, whole_data):
            last_page = True
            return one_page, last_page

        print(corp, ': ', title)
        
        one_page.append(obj)
    last_page = True if not one_page else False

    return one_page, last_page


def itdonga_crawler(file_path):
    
    pages = np.array([])
    page_num = 1
    last_page = False

    file_name = '{}.json'.format(corp)
    file = os.path.join(file_path, file_name)

    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        update = True

    except FileNotFoundError:
        data = None
        update = False
        dump, page_num = start_from_dump(corp)
        
        if dump:
            pages = np.append(dump, pages)

    while not last_page:
        one_page, last_page = crawler(page_num, whole_data=data)
        if one_page:
            pages = np.append(pages, one_page)
            page_num += 1
            temp_dump(pages, page_num, corp, update)
    if data:
        pages = np.append(pages, data)
        
    pages = pages.tolist()
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(pages, f, indent='\t', ensure_ascii=False)
    print(corp, ' Done')

