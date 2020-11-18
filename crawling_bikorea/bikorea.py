import requests
from bs4 import BeautifulSoup as bs
import json
import numpy as np
from utils import temp_dump, start_from_dump, stop
import os


main_page = 'http://www.bikorea.net/news/articleList.html?page={}&total=27604&sc_section_code=&sc_sub_section_code=&sc_serial_code=&sc_area=&sc_level=&sc_article_type=&sc_view_level=&sc_sdate=&sc_edate=&sc_serial_number=&sc_word=&sc_word2=&sc_andor=&sc_order_by=I&view_type=sm'
html = requests.get(main_page.format(1))
soup = bs(html.content, 'html.parser')
url_head = 'http://www.bikorea.net/news/'
corp = soup.head.title.text


def parse_title(_title):
    return _title.text


def parse_day(_day):
    return _day.text


def parse_url(_url):
    url = str(_url).split('\"')[1]
    url = url_head + url
    return url


def parse_thumb(_thumb):
    try:
        thumb = _thumb.previous_sibling.previous_sibling.select('img')
    except AttributeError:
        return None
    thumb = str(thumb)
    thumb = thumb.split('\"')[1].strip('./')
    thumb = url_head+thumb
    return thumb


def parse_cat(_cat):
    return _cat.previous_sibling.previous_sibling.text


def parse_time(url):
    time = requests.get(url)
    time_soup = bs(time.content, 'html.parser')
    try:
        time = time_soup.select('.View_Time')[0].text
    except IndexError:
        print("mem")
        return None
    time = str(time)
    time = time.split('\xa0')[-1]
    return time


def bikorea(page_num, update, whole_data=None):
    page = main_page.format(page_num)

    html = requests.get(page)
    soup = bs(html.content, 'html.parser')
    
    corp = soup.head.title.text
    thumbs = soup.select('.ArtList_Title')
    cats = soup.select('.ArtList_Title a')
    titles = soup.select('.ArtList_Title a')
    days = soup.select('.FontEng')
    urls = soup.select('.ArtList_Title a')

    one_page = []
    
    for _title, _day, _url, _thumb, _cat in zip(titles, days, urls, thumbs, cats):

        thumb = parse_thumb(_thumb)
        title = parse_title(_title)
        day = parse_day(_day)
        url = parse_url(_url)
        cat = parse_cat(_cat)
        time = parse_time(url)
        
        obj = {'corp': corp,
               'thumb': thumb,
               'time': time,
               'title': title,
               'day': day,
               'url': url,
               'category': cat}

        if update and stop(obj, whole_data):
            last_page = True
            return one_page, last_page

        print(corp, ': ', title)
        one_page.append(obj)
    last_page = True if not one_page else False

    return one_page, last_page 


def bikorea_crwaler(file_path):
    
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
        one_page, last_page = bikorea(page_num, update=update, whole_data=data)
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



