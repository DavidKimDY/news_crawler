import json
import os
import numpy as np
from utils import start_from_dump, temp_dump, get_soup, stop

BASE_PAGE = 'http://news.bizwatch.co.kr/search/news/{}'
CORP = 'bizwatch'


def parse_title(_title):
    return _title.text


def parse_cat(_cat):
    
    category = {'finance': '경제',
                'market': '증권',
                'mobile': '모바일경제',
                'real_estate': '부동산',
                'industry': '산업',
                'consumer': '생활경제',
                'opinion': '사설',
                'policy': '정책',
                'tax': '세금'}
    
    cat = _cat.attrs['href']
    cat = cat.split('/')[4]
    return category.get(cat, 'No need')


def parse_url(_url):
    url = _url.next
    url = url.attrs['href']
    url = 'http:' + url
    return url


def parse_day(_day):
    day = _day.text
    day = day.split('(')[0]
    return day


def parse_time(_time):
    return _time.text


def parse_thumb(_thumb):
    thumb = _thumb.attrs['src']
    thumb = 'http:' + thumb
    return thumb


def exception(title, cat):
    
    if '부음' in title:
        return True
    elif cat == 'No need':
        return True
    else:
        return False


def crawler(page_num, whole_data=None):

    page = BASE_PAGE.format(page_num)
    soup = get_soup(page)

    titles = soup.select('.all_news .title')
    days = soup.select('.date')
    times = soup.select('.time')
    thumbs = soup.select('.all_news img')
    urls = soup.select('.all_news .title')
    cats = soup.select('.all_news a')
    
    one_page = []

    for _title, _url, _thumb, _day, _time, _cat in zip(titles, urls, thumbs, days, times, cats):

        thumb = parse_thumb(_thumb)
        title = parse_title(_title)
        url = parse_url(_url)
        day = parse_day(_day)
        time = parse_time(_time)
        cat = parse_cat(_cat)
        
        if exception(title, cat):
            continue

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


def bizwatch_crawler(file_path):
    
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
