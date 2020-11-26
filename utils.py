import json
import requests
from bs4 import BeautifulSoup as bs
import numpy as np
import os
import re


def temp_dump(pages, page_num, file_name, update):

    if update:
        return None
    if page_num % 10 == 0:
        print('Dump util ', page_num)
        pages = pages.tolist()
        with open('temp_{}.json'.format(file_name), 'w', encoding='utf-8') as f:
            json.dump(pages, f, indent='\t', ensure_ascii=False)
        with open('page_num_{}.json'.format(file_name), 'w') as f:
            json.dump(page_num, f)


def start_from_dump(dump_file_name):
    try:
        with open('temp_{}.json'.format(dump_file_name), 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        return None, 1
    with open('page_num_{}.json'.format(dump_file_name), 'r') as f:
        page_num = json.load(f)
    return data, page_num


def get_soup(page):
    html = requests.get(page)
    try:
        soup = bs(html.content, 'html.parser')
    except Exception as e:
        print(e)
        raise
    return soup


def first_or_continuous(file_name, individual_file_name):

    pages = np.array([])

    try:  # continue
        with open(file_name, 'r', encoding='utf-8') as f:
            data = json.load(f)

        last_url = data[0]['url']
        update = True
        page_num = 1

    except FileNotFoundError:  # first
        last_url = None
        data = None
        update = False
        dump, page_num = start_from_dump(individual_file_name)

        if dump:
            pages = np.append(dump, pages)

    return page_num, update, data, pages, last_url


def integrate_files(individual_file_path, integrate_file_path, cate_list, corp):

    integrated_file = []
    integrated_file_name = '{}.json'.format(corp)
    integrated_file_path = os.path.join(integrate_file_path, integrated_file_name)

    for category in cate_list:
        individual_file_name = '{0}_{1}.json'.format(corp, category)
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


def stop(obj, whole_data):

    if whole_data is None:
        return False

    latest_urls = [obj['url'] for obj in whole_data[:100]]
    last_day = whole_data[0]['day']
    last_day = int(re.sub('\.|-', '', last_day))
    day = int(re.sub('\.|-', '', obj['day']))

    if obj['url'] in latest_urls:
        return True
    elif last_day > day:
        # need to log
        return True