import requests
from bs4 import BeautifulSoup as bs
import json
import numpy as np
import os
from utils import start_from_dump,temp_dump, stop

page = 'http://www.aitimes.kr/news/articleList.html?sc_section_code=S1N2&view_type=sm'
main_page = 'http://www.aitimes.kr/news/articleList.html?page={0}&total=971&sc_section_code=S1N{1}&sc_sub_section_code=&sc_serial_code=&sc_area=&sc_level=&sc_article_type=&sc_view_level=&sc_sdate=&sc_edate=&sc_serial_number=&sc_word=&sc_word2=&sc_andor=&sc_order_by=E&view_type=sm'
categories = {'AI Tech': 2, 'Focus': 3, 'AI Industry': 4, 'Today': 5, 'Opinion': 6}
url_head = 'http://www.aitimes.kr'
corp = '인공지능신문'


def parse_title(_title):
    return _title.text


def parse_url(_url):
    url = _url.attrs['href']
    url = url_head + url
    return url


def parse_thumb(_thumb):
    thumb = _thumb.attrs['src'].strip('.')
    thumb = url_head + '/news' + thumb
    return thumb


def parse_cat(_cat):
    cat = _cat.contents
    cat = cat[0].split()[0]
    return cat


def parse_day(_date):
    date = _date.contents
    date = date[1].split()[1]
    return date


def parse_time(_time):
    time = _time.contents
    time = time[1].split()[2]
    return time


def crawler(page_num, category_num, category_name, update, last_url, whole_data=None):

    page = main_page.format(page_num, category_num)

    html = requests.get(page)
    soup = bs(html.content, 'html.parser')
    
    titles = soup.select('.list-block strong')
    urls = soup.select('.list-block .list-image a')
    thumbs = soup.select('.list-block .list-image img')
    cats = soup.select('.list-block .list-dated')
    days = soup.select('.list-block .list-dated')
    times = soup.select('.list-block .list-dated')

    one_page = []
    
    for _title, _day, _url, _thumb, _cat, _time in zip(titles, days, urls, thumbs, cats, times):

        thumb = parse_thumb(_thumb)
        title = parse_title(_title)
        day = parse_day(_day)
        url = parse_url(_url)
        cat = parse_cat(_cat)
        time = parse_time(_time)
        
        obj = {'corp': corp,
               'thumb': thumb,
               'time': time,
               'title': title,
               'day': day,
               'url': url,
               'category': [category_name, cat],
               'cat1': category_name,
               'cat2': cat}
        
        if update and url == last_url:
                last_page = True
                return one_page, last_page

        one_page.append(obj)
        print(corp, ': ', title)

    last_page = True if not one_page else False
    return one_page, last_page


def ainews_crawler(individual_file_path, integrated_file_path):
    
    for category_name, category_num in categories.items():
        
        pages = np.array([])
        page_num = 1
        last_page = False
        individual_file_name = '{0}_{1}'.format(corp, category_name)
        individual_file = os.path.join(individual_file_path, '{}.json'.format(individual_file_name))

        try:
            with open(individual_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                last_url = data[0]['url']
            update = True

        except FileNotFoundError:
            data = None
            update = False
            last_url = None
            dump, page_num = start_from_dump(individual_file_name)

            if dump:
                pages = np.append(dump, pages)

        while not last_page:
            one_page, last_page = crawler(page_num, category_num, category_name, update, last_url, whole_data=data)
            if one_page:
                pages = np.append(pages, one_page)
                page_num += 1
                temp_dump(pages, page_num, individual_file_name, update)
        if data:
            pages = np.append(pages, data)

        pages = pages.tolist()
        with open(individual_file, 'w', encoding='utf-8') as f:
            json.dump(pages, f, indent='\t', ensure_ascii=False)
    integrate_files(individual_file_path, integrated_file_path)


def integrate_files(individual_file_path, integrated_file_path):

    integrated_file = []
    integrated_file_name = '{}.json'.format(corp)
    integrated_file_path = os.path.join(integrated_file_path, integrated_file_name)

    for category_name, category_num in categories.items():
        individual_file_name = '{0}_{1}.json'.format(corp, category_name)
        individual_file = os.path.join(individual_file_path, individual_file_name)
        try:
            with open(individual_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print('No {}'.format(individual_file))
            raise Exception("Check the path of individual files")
        integrated_file = np.append(integrated_file, data)

    integrated_file = integrated_file.tolist()

    with open(integrated_file_path, 'w', encoding='utf-8') as f:
        json.dump(integrated_file, f, indent='\t', ensure_ascii=False)
    print(corp, ' Done')





