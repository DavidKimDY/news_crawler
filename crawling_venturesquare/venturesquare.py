import requests
from bs4 import BeautifulSoup as bs
import json
import numpy as np
import os
from utils import start_from_dump, temp_dump, stop

main_page = 'https://www.venturesquare.net/news/page/{}'
corp = '벤처스퀘어'


def parse_title(_title):
    title = _title.attrs['title']
    return title


def parse_thumb(_thumb):
    thumb = _thumb.attrs['src']
    return thumb
    
    
def parse_url(_url):
    url = _url.attrs['href']
    return url


def parse_cat(_cat):
    return _cat.text


def parse_day_time(_datetime):
    datetime = _datetime.attrs['datetime']
    day = datetime.split('T')[0]
    time = datetime.split('T')[1].split('+')[0]
    return day, time


def crawler(page_num, whole_data=None):
    page = main_page.format(page_num)

    html = requests.get(page)
    soup = bs(html.content, 'html.parser')
    
    titles = soup.select('.post-wrap img')
    thumbs = soup.select('.post-wrap img')
    cats = soup.find_all('span', class_="cat-title")
    urls = soup.select('.image-link')
    datetimes = soup.find_all('time')

    one_page = []
    
    for _title, _cat, _url, _thumb, _datetime in zip(titles, cats, urls, thumbs, datetimes):

        thumb = parse_thumb(_thumb)
        title = parse_title(_title)
        cat = parse_cat(_cat)
        url = parse_url(_url)
        day, time = parse_day_time(_datetime)
        
        obj = {'corp': corp,
               'thumb': thumb,
               'time': time,
               'title': title,
               'day': day,
               'url': url,
               'category': cat}

        if stop(obj, whole_data):
            last_page = True
            return one_page, last_page

        print(corp, ': ', title)
        one_page.append(obj)
    last_page = True if not one_page else False

    return one_page, last_page


def venturesquare_crawler(file_path):
    
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

