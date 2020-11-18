import json
import os
import numpy as np
from utils import start_from_dump, temp_dump, get_soup, stop

BASE_PAGE = 'http://www.vrn.co.kr/news/articleList.html?page={}&total=3788&sc_section_code=&sc_sub_section_code=&sc_serial_code=&sc_area=&sc_level=&sc_article_type=&sc_view_level=&sc_sdate=&sc_edate=&sc_serial_number=&sc_word=&sc_word2=&sc_andor=&sc_order_by=E&view_type=sm'
PAGE_HEAD = 'http://www.vrn.co.kr'
CORP = 'VRN'


def parse_title(_title):
    return _title.text


def parse_url(_url):
    url = _url.attrs['href']
    url = PAGE_HEAD + url
    return url


def parse_thumb(_thumb):
    thumb = _thumb.attrs['style']
    thumb = thumb.split('./')[-1].strip(')')
    thumb = PAGE_HEAD + '/news/' + thumb
    return thumb


def parse_day(_day):
    day = _day.text.split()
    day = day[-2]
    return day


def parse_cat(_cat):
    cat = _cat.text.split()
    cat = cat[0]
    return cat


def parse_time(_time):
    time = _time.text.split()
    time = time[-1]
    return time


def crawler(page_num, whole_data=None):

    page = BASE_PAGE.format(page_num)
    soup = get_soup(page)

    titles = soup.select('.list-titles')
    days = soup.select('.list-dated')
    times = soup.select('.list-dated')
    thumbs = soup.select('.list-image')
    urls = soup.select('.list-titles a')
    cats = soup.select('.list-dated')
    
    one_page = []

    for _title, _url, _thumb, _day, _time, _cat in zip(titles, urls, thumbs, days, times, cats):

        thumb = parse_thumb(_thumb)
        title = parse_title(_title)
        url = parse_url(_url)
        day = parse_day(_day)
        time = parse_time(_time)
        cat = parse_cat(_cat)

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
        
    last_page = False if one_page else True

    return one_page, last_page


def vrn_crawler(file_path):
    
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

