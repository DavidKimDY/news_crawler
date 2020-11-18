import json
import os
import numpy as np
from utils import stop, temp_dump, get_soup, first_or_continuous, integrate_files
from time import time

BASE_PAGE = 'http://clomag.co.kr/magazine?category={0}&page={1}'
CATEGORIES = ['CAST', 'INSIGHT']
CORP = 'CLO'
CLO_THUMB = '/assets/article_sample-df281dcfbf04fe603f349f9cca65bea16660bc88ff86e733a4ccc53a9e3faf07.png'


def parse_title(_title):
    title = _title.text
    title = title.replace('\u200b', '')
    return title


def parse_tag(_tag):
    tags = _tag.text
    tags = tags.split('\n')[2::3]
    tag = [tag.strip() for tag in tags]
    return tag


def parse_url(_url):
    url = _url.attrs['href']
    return url


def parse_day(_day):
    day = _day.text
    pieces = day.split()
    y = pieces[0][:4]
    m = pieces[1][:2]
    d = pieces[2][:2]
    return '{0}.{1}.{2}'.format(y, m, d)


def parse_thumb(_thumb):
    thumb = _thumb.attrs['src']
    if thumb == CLO_THUMB:
        return None
    else:
        return 'http:'+thumb


def crawler(page_num, category, whole_data=None):

    t1 = time()
    page = BASE_PAGE.format(category, page_num)
    soup = get_soup(page)
    runtime = time()-t1
    timeout = False

    if runtime > 25:
        one_page = None
        last_page = None
        timeout = True

        return one_page, last_page, timeout

    titles = soup.select('.title')
    tags = soup.select('.tags')
    days = soup.select('.date')
    thumbs = soup.select('.img-responsive')
    urls = soup.select('.cover a')

    one_page = []

    for _title, _tag, _url, _thumb, _day in zip(titles, tags, urls, thumbs, days):

        thumb = parse_thumb(_thumb)
        title = parse_title(_title)
        tag = parse_tag(_tag)
        url = parse_url(_url)
        day = parse_day(_day)
        
        obj = {'corp': CORP,
               'thumb': thumb,
               'title': title,
               'day': day,
               'url': url,
               'category': category,
               'tag': tag}

        if stop(obj, whole_data):
            last_page = True
            return one_page, last_page, timeout
        
        one_page.append(obj)
        
    last_page = False if one_page else True
    print(last_page, ': ', page_num)  # delete

    return one_page, last_page, timeout


def clomag_crawler(individual_file_path, integrated_file_path):
    
    for category in CATEGORIES:
        
        last_page = False
        
        individual_file_name = '{0}_{1}.json'.format(CORP, category)
        file = os.path.join(individual_file_path, individual_file_name)

        page_num, update, data, pages, last_url = first_or_continuous(file, individual_file_name)

        while not last_page:
            one_page, last_page, timeout = crawler(page_num, category, whole_data=data)

            if timeout:
                page_num += 1
                continue

            if one_page:
                pages = np.append(pages, one_page)
                page_num += 1
                temp_dump(pages=pages, page_num=page_num, file_name=individual_file_name, update=update)
        if data:
            pages = np.append(pages, data)

        pages = pages.tolist()

        with open(file, 'w', encoding='utf-8') as f:
            json.dump(pages, f, indent='\t', ensure_ascii=False)
            
    integrate_files(individual_file_path, integrated_file_path, CATEGORIES, CORP)

