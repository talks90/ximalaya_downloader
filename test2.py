# -*- coding:utf-8 -*-

# 抓取解析喜馬拉雅的音頻信息　存儲　mongodb資料庫

import requests
from bs4 import BeautifulSoup
from lxml import etree

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/73.0.3683.86 Safari/537.36'
}
site = 'https://www.ximalaya.com'


def get_detail_url():
    start_urls = [f'{site}/shangye/p{pn}' for pn in range(1, 35)]
    # print(start_urls)
    for start_url in start_urls:
        response = requests.get(start_url, headers=headers).text
        soup = BeautifulSoup(response, 'lxml')
        # print(soup.prettify())
        for item in soup.find_all('div', class_='album-wrapper'):
            # print(item)
            href = site + item.a['href']
            title = item.find('span', class_='v-m').text
            content = {
                'href': href,
                'title': title,
                # 'img_url': item.img['src'],
            }
            # print(content)
            print(f'正在下載《{content["title"]}》頻道')
            get_mp3(href, title)
        break


def get_mp3(url, title):
    response = requests.get(url, headers=headers).text
    num_list = etree.HTML(response).xpath('//div[@class="sound-list _OO"]/ul//a/@href')
    print(num_list)


if __name__ == '__main__':
    get_detail_url()
