import os

from crawling_hellodd.hellodd import hellodd_crawler
from crawling_irobotnews.irobotnews import irobotnews_crawler
from crawling_bikorea.bikorea import bikorea_crwaler
from crawling_itdonga.itdonga import itdonga_crawler
from crawling_venturesquare.venturesquare import venturesquare_crawler
from crawling_itchosun.IT_Chosun import itchosun_crawler
from crawling_klnews.klnews import klnews_crawler
from crawling_ainews.AI_News import ainews_crawler
from crawling_clo.clomag import clomag_crawler
from crawling_bizwatch.bizwatch import bizwatch_crawler
from crawling_vrn.vrn import vrn_crawler
from crawling_platum.platum import platum_crawler
from crawling_besuccess.besuccess import besuccess_crawler
from crawling_sciencetimes.sciencetimes import sciencetimes_crawler
from crawling_mobiinside.mobiinside import mobileinside_crawler
from crawling_itnews.itnews import itnews_crawler


print('...')

base_path = '/Users/daeyeop/Work/News data/'
file_path = os.path.join(base_path, 'DB file')
temp_file_path = os.path.join(base_path, 'temp file')
url_file_path_itnews = os.path.join(base_path, 'itnews url/url_database.json')

clomag_crawler(integrated_file_path=file_path, individual_file_path=temp_file_path)
ainews_crawler(integrated_file_path=file_path, individual_file_path=temp_file_path)
platum_crawler(integrated_file_path=file_path, individual_file_path=temp_file_path)

venturesquare_crawler(file_path)
besuccess_crawler(file_path)
bikorea_crwaler(file_path)
bizwatch_crawler(file_path)
irobotnews_crawler(file_path)
hellodd_crawler(file_path)
itdonga_crawler(file_path)
klnews_crawler(file_path)
mobileinside_crawler(file_path)
vrn_crawler(file_path)
sciencetimes_crawler(file_path)
itchosun_crawler(file_path)
itnews_crawler(file_path, url_file_path_itnews)

