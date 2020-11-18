import requests
from bs4 import BeautifulSoup as bs
import json
import numpy as np
import os
from utils import stop


api_key = "irobotnews"
url_head = 'http://www.irobotnews.com/news/'
main_page = 'http://www.irobotnews.com/news/articleList.html?page={}&total=16078&sc_section_code=S1N1&sc_sub_section_code=&sc_serial_code=&sc_area=&sc_level=&sc_article_type=&sc_view_level=&sc_sdate=&sc_edate=&sc_serial_number=&sc_word=&sc_word2=&sc_andor=&sc_order_by=I&view_type=sm'
corp = '로봇신문'


def irobotnews(page_number, update=False, whole_data=None):
    page = main_page.format(page_number)
    html = requests.get(page)
    soup = bs(html.content, 'html.parser')

    titles = soup.select('.ArtList_Title a ')
    urls = soup.select('.ArtList_Title a ')
    days = soup.select('.View_SmFont')
    thumbnails = soup.select('.ArtList_Title')
    categories = soup.select('.ArtList_Title .FontKor')
    corp = soup.title.text

    one_page = []
    last_page = False

    for _title, _day, _thumb, _cat, _url in zip(titles, days, thumbnails, categories, urls):

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
            break

        print(corp, ': ', title)
        one_page.append(obj)

    return last_page, one_page


def irobotnews_crawler(file_path):

    file_name = '{}.json'.format(api_key)
    file = os.path.join(file_path, file_name)
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print('FileNotFoundError: expected {} but there is not.'.format(file))
        return


    pages = []
    page_num = 1
    last_page = False
    while not last_page:
        last_page, one_page = irobotnews(page_num, update=True, whole_data=data)
        pages = np.append(pages, one_page)
        page_num += 1

    pages = np.append(pages, data).tolist()
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(pages, f, indent='\t', ensure_ascii=False)
    print(corp, ' Done')


def parse_irobonews():
    last_page = False
    page_num = 1
    pages = []

    while not last_page:
        last_page, one_page = irobotnews(page_num)
        if not last_page:
            pages = np.append(pages, one_page)
            page_num += 1
        else:
            page_num -= 1
            print('Last page is {}'.format(page_num))

    pages = pages.tolist()

    with open('irobotnews.json', 'w', encoding='utf-8') as f:
        json.dump(pages, f, indent='\t', ensure_ascii=False)


def isempty(title):
    if title:
        return False
    else:
        return True


def parse_url(_url):
    return url_head + str(_url).split('>')[0].split('\"')[1]


def parse_thumb(_thumb):
    tags = str(_thumb.previous_sibling.previous_sibling)
    if tags == 'None':
        thumb = ''
    else:
        thumb = url_head + tags.split('\"')[3].strip('./')
    return thumb


def parse_title(_title):
    return _title.text


def parse_day(_day):
    return _day.text


def parse_time(url):
    url_site = requests.get(url)
    time = bs(url_site.content, 'html.parser')
    time = str(time.select('.View_Time')).split()[3].split('<')[0]
    return time


def parse_cat(_cat):
    return _cat.text

