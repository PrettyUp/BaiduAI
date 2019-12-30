import logging
import random
import sqlite3
import time
import urllib

from lxml import etree
from lxml import html

import requests
class UgirlsDownloader():
    def __init__(self):
        self.db_conn = sqlite3.connect('ugirls.db')
        self.db_cursor = self.db_conn.cursor()
        self.model_count = 0
        pass

    def request_ajax_url(self,ajax_url):
        headers = {
            'Host': 'www.ugirls.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.ugirls.com/Models/',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
        }
        i = 0
        while True:
            i += 1
            logging.warning('开始第%s轮ajax请求' % i)
            data = {
                'page': i,
                'tag_id': ''
            }
            response = requests.post(ajax_url,headers=headers,data=data)
            if response.status_code != 200:
                break
            sel = etree.HTML(response.text)
            model_home_pages = sel.xpath('//a[@class="model_item rectangle vertical"]/@href')
            for model_home_page in model_home_pages:
                logging.warning('\r\n开始访问：%s'%model_home_page)
                self.parse_model_home_page(model_home_page)
        pass

    def request_home_page_url(self):
        for i in range(600):
            model_home_page = 'https://www.ugirls.com/Content/List/Magazine-'+str(i)+'.html'
            logging.warning('\r\n开始请求%s'%model_home_page)
            self.parse_model_home_page(model_home_page)


    def parse_model_home_page(self,model_home_page):
        time_sleep = random.randint(2,9)
        time.sleep(time_sleep)
        headers = {
            'Host': 'www.ugirls.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
            'Accept': 'text/html,application',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        try:
            response = requests.get(model_home_page,headers=headers,timeout=5)
            if response.status_code != 200:
                logging.warning('请求出错：%s'%response.status_code)
                return False
            sel = etree.HTML(response.text)
        except Exception:
            return False
        try:
            model_name = sel.xpath('//div[@class="ren"]//div[@class="ren_head"]/div/a/text()')[0]
        except Exception:
            model_name = ''
        try:
            model_city = sel.xpath('///div[@class="ren"]//div[@class="ren_head"]/p[1]/text()')[0]
        except Exception:
            model_city = ''
        try:
            model_body_temp = sel.xpath('///div[@class="ren"]//div[@class="ren_head"]/p[2]/text()')[0]
            model_body_temp_dict = model_body_temp.split(' ')
            model_height = model_body_temp_dict[0][3:6]
            model_measure_temp_dict = model_body_temp_dict[1].split('/')
            model_bust = model_measure_temp_dict[0][3:]
            model_waist = model_measure_temp_dict[1]
            model_hit = model_measure_temp_dict[2]
        except Exception:
            model_height = '0'
            model_bust = '0'
            model_waist = '0'
            model_hit = '0'
        try:
            model_popular = sel.xpath('///div[@class="ren"]//div[@class="ren_info"]/strong/text()')[0]
        except Exception:
            model_popular = '0'
        try:
            model_fans = sel.xpath('///div[@class="ren"]//div[@class="ren_info"]/a[1]/text()')[0]
        except Exception:
            model_fans = '0'
        try:
            model_albums = sel.xpath('///div[@class="ren"]//div[@class="ren_info"]/a[2]/text()')[0]
        except Exception:
            model_albums = '0'
        try:
            model_videos = sel.xpath('///div[@class="ren"]//div[@class="ren_info"]/a[3]/text()')[0]
        except Exception:
            model_videos = '0'

        # model_home_page = urllib.request.quote(model_home_page)

        self.model_count += 1
        logging.warning('第%s位模特%s信息抽取完成，即将插入数据库' %(self.model_count,model_name))
        sql = "insert into model_infos values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"\
                %(model_name,model_city,model_height,model_bust,model_waist,model_hit,model_popular,model_fans,\
                  model_albums,model_videos,model_home_page)
        self.db_cursor.execute(sql)
        self.db_conn.commit()
        return True
        pass

    def __del__(self):
        self.db_cursor.close()
        self.db_conn.close()
        pass


if __name__ == '__main__':
    ajax_url = 'https://www.ugirls.com/Ajax/Model/getModelListAjax'
    ugirls_downloader = UgirlsDownloader()
    # ugirls_downloader.request_ajax_url(ajax_url)
    ugirls_downloader.request_home_page_url()

