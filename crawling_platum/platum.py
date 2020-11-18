import json
import os
import numpy as np
from utils import start_from_dump, temp_dump, get_soup, stop, integrate_files

BASE_PAGE='https://platum.kr/{0}/page/{1}'
CORP = 'platum'
CATEGORIES = ['entrepreneur', 'startup', 'china', 'trends', 'workinsight', 'marketing', 'business',
              'event', 'all-tech-korea', 'report', 'blockchain', 'startup-3']
ended_category = []


def parse_title(_title):
    return _title.text


def parse_url(_url):
    return _url.attrs['href']


def parse_day(_day):
    day = _day.text.split()
    day = day[-1]
    day = day.replace('/', '-')
    return day


def parse_thumb(_thumb):
    
    try:
        thumb = _thumb.find('div', class_='post_img').img.attrs['src']
    except AttributeError:
        thumb = None    
    
    return thumb


def parse_cat(_cat):
    return [cat.text for cat in _cat.find_all('a')]


def duplication(parsed_categories, ended_categories):
    for parsed in parsed_categories:
        if parsed.lower() in ended_categories:
            return True
    return False


def crawler(page_num, category, ended_categories, whole_data=None):

    page = BASE_PAGE.format(category, page_num)
    soup = get_soup(page)

    titles = soup.select('.post_header_title h5 a')
    days = soup.select('.post_info_date')
    thumbs = soup.find_all(class_='post_header')
    urls = soup.select('.post_header_title h5 a') 
    cats = soup.select('.post_info_cat')[1:]
    
    one_page = []
    title_list = []

    for _title, _url, _thumb, _day, _cat in zip(titles, urls, thumbs, days, cats):

        thumb = parse_thumb(_thumb)
        title = parse_title(_title)
        url = parse_url(_url)
        day = parse_day(_day)
        cat = parse_cat(_cat)

        title_list.append(title)
        if duplication(cat, ended_categories):
            continue

        obj = {'corp': CORP,
               'thumb': thumb,
               'title': title,
               'day': day,
               'url': url,
               'category': cat}

        if stop(obj, whole_data):
            last_page = True
            return one_page, last_page

        print(CORP, ': ', title)
        
        if obj:
            one_page.append(obj)
    last_page = False if title_list else True
        
    return one_page, last_page


def platum_crawler(integrated_file_path, individual_file_path):
    
    ended_categories = []
    
    for category in CATEGORIES:  
        
        pages = np.array([])
        page_num = 1
        last_page = False

        category_file_name = '{0}_{1}'.format(CORP, category)
        category_file_name_ = '{0}_{1}.json'.format(CORP, category)
        category_file_path = os.path.join(individual_file_path, category_file_name_)

        try:
            with open(category_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            update = True

        except FileNotFoundError:
            data = None
            update = False
            dump, page_num = start_from_dump(category_file_name)

            if dump:
                pages = np.append(dump, pages)

        while not last_page:
            one_page, last_page = crawler(page_num, category, ended_categories, whole_data=data)
            if one_page:
                pages = np.append(pages, one_page)
                temp_dump(pages, page_num, category_file_name, update)
            page_num += 1
            
        if data:
            pages = np.append(pages, data)
        
        if category == 'startup-3':
            category = 'main'
        
        ended_categories.append(category)

        pages = pages.tolist()
        with open(category_file_path, 'w', encoding='utf-8') as f:
            json.dump(pages, f, indent='\t', ensure_ascii=False)

    integrate_files(individual_file_path, integrated_file_path, CATEGORIES, CORP)
