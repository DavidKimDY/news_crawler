import requests
from bs4 import BeautifulSoup as bs
import json
import numpy as np
import os
from utils import stop, start_from_dump, temp_dump

main_page = 'https://www.hellodd.com/news/articleList.html?page={}&view_type=sm'
url_head = 'https://www.hellodd.com'
corp = '헬로디디'


def hellodd(page_num, whole_data=None):
    page = main_page.format(page_num)

    html = requests.get(page)
    soup = bs(html.content, 'html.parser')
    content = soup.find('section', {'id': 'section-list'})

    titles_urls = content.find_all('h4', {'class': 'titles'})
    time_category = content.find_all('span', {'class': 'byline'})
    thumbs = content.find_all('li')

    one_page = []
    
    for _titles_urls, _time_category, _thumb in zip(titles_urls, time_category, thumbs):

        thumb = parse_thumb(_thumb)
        title, url = parse_titles_urls(_titles_urls)
        time, day, cat = parse_time_category(_time_category)

        obj = {'corp': corp,
               'thumb': thumb,
               'title': title,
               'day': day,
               'url': url,
               'category': cat}

        if '[인사]' in title or cat is '인사동정':
            continue

        if stop(obj, whole_data):
            last_page = True
            return one_page, last_page

        print(corp, ': ', title)
        one_page.append(obj)
    last_page = True if not one_page else False
        
    return one_page, last_page  


def hellodd_crawler(file_path):

    pages = np.array([])
    page_num = 1
    last_page = False

    file_name = 'hellodd.json'
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
        one_page, last_page = hellodd(page_num, whole_data=data)
        if one_page:

            pages = np.append(pages, one_page)
            page_num += 1
            temp_dump(pages, page_num, corp, update)

    if data:
        pages = np.append(pages, data)

    pages = pages.tolist()
    with open(file, 'w', encoding='utf-8',) as f:
        json.dump(pages, f, indent='\t', ensure_ascii=False)
    print(corp, ' Done')


def parse_thumb(_thumb):
    img_tag = _thumb.a.img
    if img_tag is None:
        return img_tag
    return img_tag.attrs['src']


def parse_titles_urls(source):
    title = source.text
    url = url_head + source.a.attrs['href']
    return title, url


def parse_time_category(source):
    cat = source.find_all('em')[0].text
    time = source.find_all('em')[-1].text
    date, time = time.split()
    return time, date, cat
