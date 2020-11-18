import requests
import json
import os
import numpy as np
from utils import start_from_dump, temp_dump, get_soup, stop

main_page = 'http://it.chosun.com/svc/list_in/list.html?pn={}'
url_head = 'http://it.chosun.com'
corp = 'IT CHOSUN'


def parse_title(_title):
    title = str(_title)
    title = title.split('\">')[-1].split('<')[0]
    return title


def parse_thumb(_thumb):
    thumb = _thumb.previous.previous.attrs
    try:
        thumb = thumb['src']
        return thumb
    except Exception:
        return None


def parse_url(_url):
    url = _url.find('a').attrs['href']
    return url


def new_date(url_soup):
    datetime = url_soup.select('.news_date')[0].text
    day = datetime.split()[1].replace('.', '-')
    time = datetime.split()[2].strip('\r\n')
    return day, time


def parse_day_time(soup):

    if not soup.title:
        return None, None
    published_time = soup.find('meta', property='dd:published_time')
    if not published_time:
        published_time = soup.find('meta', property='article:published_time')
        if not published_time:
            day, time = new_date(soup)
            return day, time
    
    time = str(published_time.attrs['content'])
    time = time.split('T')[1].split('+')[0]
        
    day = str(published_time.attrs['content'])
    day = day.split('T')[0].split('+')[0].split('+')[0]
    
    return day, time


def parse_tag(_tag):
    tag = _tag.find('div', class_='right')
    if tag:
        tag = str(tag.text)
        tag = tag.strip().replace('#', '').split('\n')
        return tag
    else:
        return None


def parse_cat(soup):

    if not soup.head:
        return ['', '']

    categories = soup.head.title.text.split(' > ')
    cat1 = categories[-2]
    cat2 = categories[-1]

    if cat2 == '인사·부음':
        return None

    if cat2 in ['동영상', '전체 기사', '기업', '자동차', '기술', '게임·라이프', '사람', '칼럼·해설', '뉴스']:
        cat1 = cat2
        cat2 = ''
    category = [cat1, cat2]

    return category


def crawler(page_num, whole_data=None):
    page = main_page.format(page_num)
    soup = get_soup(page)

    titles = soup.select('.tt')
    thumbs = soup.find_all('div', class_='txt_wrap')
    urls = soup.find_all('div', class_='txt_wrap')
    tags = soup.find_all('div', class_='info')

    one_page = []
    
    for _title, _tag, _url, _thumb in zip(titles, tags, urls, thumbs):

        thumb = parse_thumb(_thumb)
        title = parse_title(_title)
        tag = parse_tag(_tag)
        url = parse_url(_url)

        soup = get_soup(url)
        cat = parse_cat(soup)
        day, time = parse_day_time(soup)

        if not cat:
            continue

        obj = {'corp': corp,
               'thumb': thumb,
               'time': time,
               'title': title,
               'day': day,
               'url': url,
               'tags': tag,
               'category': cat,
               'cat1': cat[0],
               'cat2': cat[1]}

        if stop(obj, whole_data):
            last_page = True
            return one_page, last_page

        print(corp, ': ', title)
        one_page.append(obj)
    last_page = False if one_page else True

    return one_page, last_page


def itchosun_crawler(file_path):
    
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
