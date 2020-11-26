import os
import json
from crawling_itnews.url_crawler import post_soup, url_crawler

ID_PARAMS = {'log': 'coredottoday',
             'pwd': 'core.today',
             'redirect_to': '',
             'a': 'login',
             'rememberme': 'forever',
             'Submit': '로그인'}

CORP = 'IT NEWS'


def get_data(page, soup):

    corp = CORP
    url = page
    title = soup.title.text
    try:
        thumb = soup.find('img', {'class': 'aligncenter'}).attrs['src']
    except:
        thumb = ''
    datetime = soup.find('time', {'class': 'entry-date'}).attrs['datetime'].split('T')
    day = datetime[0]
    time = datetime[1][:5]
    try:
        cat = soup.find('li', {'class': 'entry-category'}).text
    except:
        cat = ''

    return [corp, url, title, thumb, day, time, cat]


def scraping(urls: list, ID_PARAMS: dict):

    '''
    :param urls: list
    to scrape
    :param ID_PARAMS: dict
    dict. id and pw in order to log in
    :param initial: bool
    True: assumes there is no data. So need to save data into DB file
    False : assumes there is data. So scrapes new urls only and returns data from new urls

    :return:
    list composed dict data about articles.
    '''

    newsdata = []
    for page in urls:
        bin = {}
        soup = post_soup(page, ID_PARAMS)
        data = get_data(page, soup)
        bin['corp'], bin['url'], bin['title'], bin['thumb'], bin['day'], bin['time'], bin['cat'] = data
        newsdata.append(bin)

        with open('/Users/daeyeop/Work/News Crawler/DB file/{}.json'.format(CORP), 'w', encoding='utf-8') as f:
            json.dump(newsdata, f, indent='\t', ensure_ascii=False)

    return newsdata


def itnews_crawler(file_path, url_path, initial=False):
    '''
    :param file_path: str
    to DB file about article
    :param url_path: str
    to crawling_itnews
    :param initial: bool
    when first crawling
    '''

    file_name = '{}.json'.format(CORP)
    file = os.path.join(file_path, file_name)
    if initial:
        existed_url = []
    else:
        with open(url_path, 'r', encoding='utf-8') as f:
            existed_url = json.load(f)

    new_url = url_crawler(existed_url)
    result = scraping(new_url, ID_PARAMS)

    if result:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data.extend(result)
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(data, f,  ensure_ascii=False, indent='\t')

    print(CORP, ' Done')
