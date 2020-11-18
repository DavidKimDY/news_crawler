import json
from bs4 import BeautifulSoup as bs
import requests
import re
import numpy as np
import os
from utils import get_soup, start_from_dump, temp_dump, stop


BASE_PAGE = 'https://www.sciencetimes.co.kr/category/sci-tech/page/{}/'
CORP = 'sciencetimes'
no_cat = []


def parse_thumb(_thumb):
    thumb = _thumb.previous.previous
    thumb = thumb.previous.previous
    try:
        thumb = thumb.attrs['style']
        thumb = re.sub('.*\(\'', '', thumb)
        thumb = thumb.strip('\');')
    except Exception as e:
        thumb = ''
    return thumb


def parse_cat(_cat):
    cat_list = {'133':'자연,환경,에너지', '128':'기초,응용과학',
                '16933':'ICT,로봇','130':'보건,의학',
                '132':'항공,우주','134':'신소재,신기술'}
    cat = _cat.previous.previous
    cat = cat.find('a')
    cat = cat.attrs['href']
    cat = cat.split('cat=')[-1]
    try:
        cat = cat_list[cat]
    except Exception as e:
        title = parse_title(_cat)
        obj = {'title': title, 'cat': cat}
        no_cat.append(obj)
        print(obj)
    return cat


def parse_url(_url):
    url = _url.previous.previous
    url = url.find('a')
    url = url.attrs['href']
    return url


def parse_title(_title):
    title = _title.previous.previous
    title = title.find('strong').text
    return title


def parse_day_time(url):
    soup = get_soup(url)
    day_time = soup.find('em', {'class': 'date'}).text
    day = day_time.split()[0].replace('.', '-')
    time = day_time.split()[1]
    return day,time


def crawler(page_num, whole_data=None):
    page = BASE_PAGE.format(page_num)

    html = requests.get(page)
    soup = bs(html.content, 'html.parser')
    
    titles = soup.find_all('span', {'class': 'cate'})
    urls = soup.find_all('span', {'class': 'cate'})
    cats = soup.find_all('span', {'class': 'cate'})
    thumbs = soup.find_all('span', {'class': 'cate'})

    one_page = []
    
    for _title, _url, _thumb, _cat in zip(titles, urls, thumbs, cats):

        thumb = parse_thumb(_thumb)
        title = parse_title(_title)
        url = parse_url(_url)
        cat = parse_cat(_cat)
        day, time = parse_day_time(url)
        
        obj = {'corp': CORP,
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

        one_page.append(obj)
    last_page = True if not one_page else False

    return one_page, last_page


def sciencetimes_crawler(file_path):
    
    pages = np.array([])
    page_num = 1
    last_page = False

    file_name = '{}.json'.format(CORP)
    file = os.path.join(file_path, file_name)

    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        last_url = data[0]['url']
        update = True

    except FileNotFoundError:
        last_url = None
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

