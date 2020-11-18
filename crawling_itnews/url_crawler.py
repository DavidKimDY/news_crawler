import requests
import json
from bs4 import BeautifulSoup as bs

url = 'http://www.itnews.or.kr/wp-admin/admin-ajax.php?td_theme_name=Newspaper&v=8.0'
params = {
    'MIME Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'action': 'td_ajax_block',
    'td_atts': {"limit": "5", "sort": "", "post_ids": "", "tag_slug": "", "autors_id": "", "installed_post_types": "", "category_id":"1162","category_ids":"","custom_title":"","custom_url":"","show_child_cat":30,"sub_cat_ajax":"","ajax_pagination":"next_prev","header_color":"","header_text_color":"","ajax_pagination_infinite_stop":"","td_column_number":3,"td_ajax_preloading":"","td_ajax_filter_type":"td_category_ids_filter","td_ajax_filter_ids":"","td_filter_default_txt":"All","color_preset":"","border_top":"","class":"td_uid_1_5f6d6002399b8_rand","el_class":"","offset":"","css":"","tdc_css":"","tdc_css_class":"td_uid_1_5f6d6002399b8_rand","live_filter":"","live_filter_cur_post_id":"","live_filter_cur_post_author":"","block_template_id":""},
    'td_block_id': 'td_uid_1_5f6d6002399b8',
    'td_column_number': 3,
    'td_current_page': 2,
    'block_type': 'td_block_mega_menu'
}

page_key = 'td_current_page'


def post_soup(url, params):
    html = requests.post(url, data=params)
    soup = bs(html.content, 'html.parser')
    return soup


def get_url_list(page_num, url, params):
    params[page_key] = page_num
    soup = post_soup(url, params)
    urls = soup.find_all('div', {'class': 'item-details'})
    url_list = [url.a.attrs['href'] for url in urls]
    url_list = [url.replace('\\', '') for url in url_list]
    return url_list


def new_url(url_list, url_database):
    new_url_list = []
    for url in url_list:
        if url not in url_database:
            new_url_list.append(url)
    return new_url_list


def url_crawler(existed_url):
    page_num = 1
    patient = 2
    new_urls = []
    while True:
        url_list = get_url_list(page_num, url, params)
        new_url_list = new_url(url_list, existed_url)
        if len(new_url_list) == 0:
            if patient == 0:
                break
            else:
                patient -= 1
                continue
        new_urls.extend(new_url_list)
        page_num += 1
    if not len(new_urls) == 0:
        update_database(new_urls)

    return new_urls


def update_database(new_urls):
    with open('url_database.json', 'r', encoding='utf-8') as f:
        database = json.load(f)

    database.extend(new_urls)
    with open('url_database.json', 'w', encoding='utf-8') as f:
        json.dump(database, f, indent='\t')


