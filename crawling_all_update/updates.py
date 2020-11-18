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

file_path = '/Users/daeyeop/Work/News Crawler/DB file'
file_path_ainews = '/Users/daeyeop/Work/News Crawler/crawling_ainews'
file_path_clo = '/Users/daeyeop/Work/News Crawler/crawling_clo'
file_path_platum = '/Users/daeyeop/Work/News Crawler/crawling_platum'
url_file_path_itnews = '/Users/daeyeop/Work/News Crawler/crawling_itnews/url_database.json'




clomag_crawler(integrated_file_path=file_path, individual_file_path=file_path_clo)
platum_crawler(integrated_file_path=file_path, individual_file_path=file_path_platum)
ainews_crawler(integrated_file_path=file_path, individual_file_path=file_path_ainews)
venturesquare_crawler(file_path)
besuccess_crawler(file_path)
bikorea_crwaler(file_path)
bizwatch_crawler(file_path)
irobotnews_crawler(file_path)
itchosun_crawler(file_path)
hellodd_crawler(file_path)
itdonga_crawler(file_path)
klnews_crawler(file_path)
itnews_crawler(file_path, url_file_path_itnews)
mobileinside_crawler(file_path)
vrn_crawler(file_path)
sciencetimes_crawler(file_path)

print('It would be in test git')

