
# coding: utf-8

# In[19]:

class UrlManager(object):
    
    def __init__(self):
        self.new_urls = set()
        self.old_urls = set()

    def add_new_url(self , url):
        if url is None:
            return
        if url not in self.new_urls and url not in self.old_urls:
            self.new_urls.add(url)
    
    def add_new_urls(self , urls):
        if urls is None or len(urls) == 0:
            return
        for url in urls:
            self.add_new_url(url)
         
    def has_new_url(self):
        return len(self.new_urls) != 0

    def get_new_url(self):
        new_url = self.new_urls.pop()
        self.old_urls.add(new_url)
        return new_url

from bs4 import BeautifulSoup
import json

class HtmlParser(object):
    
    def _get_albums_urls(self, page_url, user_nick, soup):        
        new_urls = set()
        links = soup.find_all('a' , class_="albums")
        print links
        for link in links:
            new_url = link['href']
            album_id = new_url[-7:-1]
            new_full_url = "https://" + user_nick + ".tuchong.com/rest/2/albums/" + album_id + "/images"
            new_urls.add(new_full_url)
            print new_full_url
        
        return new_urls
    
    def parse_albums_urls(self,page_url, user_nick, html_cont):
        if page_url is None or html_cont is None:
            return

        soup = BeautifulSoup(html_cont , 'html.parser' , from_encoding='utf-8')
        new_urls = self._get_albums_urls(page_url, user_nick, soup)
        
        return new_urls
        
    def _get_new_data(self, page_url, datas):        
        
        res_data = []
        for img in datas['data']['image_list']:
            print str(img['img_id']) + ".jpg"
            data = {}
            data['link'] = "https://photo.tuchong.com/" + str(img['user_id']) + "/f/" + str(img['img_id']) + ".jpg"
            data['fname'] = str(img['img_id']) + ".jpg"
            res_data.append(data)
        
        return res_data
    
    def parse_image(self,page_url,html_cont):
        
        if page_url is None or html_cont is None:
            return
        
        res =  json.loads(html_cont)
        
        new_data = self._get_new_data(page_url , res)
        
        return new_data
    
from os.path import os
import requests

class HtmlOutputer(object):
    
    def __init__(self):
        self.datas = []
    
    def collect_data(self , data):
        if data is None:
            return
        self.datas = data
    
    def output_html(self, user_nick):
        count = 0
        
        dir_name = "image_" + user_nick
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        
        for _data in self.datas:
            
            print '正在下载第'+str(count+1)+'张图片，图片地址:'+_data['link']
            
            try:
                pic= requests.get(_data['link'], timeout=10)
            except:
                print '【错误】当前图片无法下载'
                continue
            
            string = dir_name + '/' + _data['fname']
            
            fp = open(string.decode('utf-8').encode('cp936'),'wb')
            fp.write(pic.content)
            fp.close()
        
            count += 1
            
        self.datas = []
    

import urllib2

class HtmlDownloader(object):
    
    
    def download(self,url):
        if url is None:
            return None
        
        response = urllib2.urlopen(url, timeout=10)
        
        if response.getcode() != 200:
            return None
        
        return response.read()
    
class SpiderMain(object):
    
    def __init__(self):
        self.urls       = url_manager.UrlManager()
        self.downloader = html_downloader.HtmlDownloader()
        self.parser     = html_parser.HtmlParser()
        self.outputer   = html_outputer.HtmlOutputer()
        
    def craw(self, root_url, user_nick):
        
        html_cont = self.downloader.download(root_url)
        new_urls = self.parser.parse_albums_urls(root_url, user_nick, html_cont)
        
        count = 1
        for link in new_urls:
            
            self.urls.add_new_url(link)
            while self.urls.has_new_url():
                try:
                    new_url = self.urls.get_new_url()
                    html_cont = self.downloader.download(new_url)
                    print "craw %d : %s"%(count , new_url)
                    new_data = self.parser.parse_image(new_url,html_cont)
                    # self.urls.add_new_urls(new_urls)
                    self.outputer.collect_data(new_data)
                    
                    count = count + 1
                except:
                    print "craw fail"
            
            self.outputer.output_html(user_nick)


if __name__ == "__main__":
      
    print u'please enter the name of the folder you want to save.\n'
    user_nick = str(raw_input())
    
    print u'please enter the url of the author''s mainpage. \n eg: https://jianjianjnu.tuchong.com/albums'
    root_url = str(raw_input())
    root_url = root_url if root_url.startswith('http') else 'http://%s' % root_url
    obj_spider = SpiderMain()
    obj_spider.craw(root_url, user_nick)
    
    print "Complete"


# In[ ]:



