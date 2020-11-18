import requests
import json
import os
from bs4 import BeautifulSoup as bs
import numpy as np
from utils import start_from_dump, temp_dump, stop

main_page = 'http://www.klnews.co.kr/news/articleList.html?page={}&total=57525&sc_section_code=&sc_sub_section_code=&sc_serial_code=&sc_area=&sc_level=&sc_article_type=&sc_view_level=&sc_sdate=&sc_edate=&sc_serial_number=&sc_word=&sc_word2=&sc_andor=&sc_order_by=E&view_type=sm'
url_head = 'http://www.klnews.co.kr/news/'
corp = '물류신문'


def parse_title(_title):
    return _title.a.text


def parse_cat(_cat):
    cat = _cat.select('.FontKor')[0].text
    return cat


def parse_day(_day):
    day = _day.select('.View_SmFont')[-1].text
    return day


def parse_thumb(_thumb):
    try:
        thumb = _thumb.previous.previous.attrs['src'].strip('./')
        thumb = url_head + thumb
        return thumb
    except:
        return None


def parse_url(_url):
    url = _url.attrs['href']
    url = url_head + url
    return url


def parse_time(url):
    html = requests.get(url)
    soup = bs(html.content, 'html.parser')
    try:
        parsing = soup.select('.WrtTip .SmN')[0].text
    except IndexError:
        return None
    splited = str(parsing).split('\t')
    day_time = [day_time for day_time in splited if ':' in day_time][0]
    time = day_time.split()[-1]
    return time


def crawler(page_num, whole_data=None):
    page = main_page.format(page_num)

    html = requests.get(page)
    soup = bs(html.content, 'html.parser')
    
    titles = soup.select('.ArtList_Title')
    cats = soup.select('.ArtList_Title')
    days = soup.select('.ArtList_Title')
    thumbs = soup.select('.ArtList_Title')
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

        if stop(obj, whole_data):
            last_page = True
            return one_page, last_page

        print(corp, ': ', title)
        one_page.append(obj)
    last_page = True if not one_page else False

    return one_page, last_page


def klnews_crawler(file_path):
    
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
