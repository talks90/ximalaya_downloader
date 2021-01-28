from Module import net_fn
from bs4 import BeautifulSoup
import requests
from queue import Queue
import os
import re
import time
from tqdm import tqdm
import json
import platform
from threading import Thread

# self.save_dirs = r'C:\Users\Liky\Desktop\English'  # 檔案儲存位址
save_dirs = r'F:\Downloads\喜馬拉雅'  # 檔案儲存位址
track_names = []
track_links = []
url = ""


class ximlaya:
    def __init__(self):
        self.Net = net_fn.Net()
        # self.audio_link_queue = Queue()
        self.max_download_thread = 3  # 最大線程數
        self.down_thread_log = []  # 線程紀錄
        self.album_name = ""
        self.album_type = ""
        self.album_id = ""
        self.header = {
            'Accept': '*/*',
            'Accept - Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
            # 'xm - sign': '9273ddeffcbfeca6eea0cabb6acb1d24(2)1557539813220(18)1557539816877',
        }
        self.album_num = 0

    def elem_selector(self, bs_page, sel_item, sel_class= None):
        sel_result = bs_page.findall(sel_item, sel_class)
        return sel_result

    def get_url(self, url):
        short_url = re.findall('[^/#]*', url)
        # return short_url[6], short_url[8]
        return short_url

    def get_target_maxpage(self):
        header_parse = "Accept: */*###Accept - Encoding: gzip, deflate, br###Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7###User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
        rs = self.Net.Get(url=url, header_string=header_parse)
        data = rs.content.decode()
        bs = BeautifulSoup(data, 'html.parser')
        # print(bs)

        a_name = bs.find('h1', class_="title _t4_").string
        fixed_text = "{}".format(a_name).replace("|", "-")
        # print(type(fixed_text))
        # a_name.replace_with(fixed_text)

        # print(fixed_text)
        self.album_name = fixed_text  # re.findall('[^/#]*', url)
        # print(album_name)

        os.makedirs(f"{save_dirs}\\{self.album_name}", exist_ok=True)

        h2_text = bs.find('h2', class_="_OO").text
        h2_size = re.findall('(\d+-*\d*)', h2_text)
        # print(int(h2_size[0]))
        self.album_num = int(h2_size[0])
        # print(self.album_num)

        if bs.find_all("span", class_="_dN2"):
            max_page = int(bs.find_all("span", class_="_dN2")[-1].text) + 1
        else:
            max_page = 2


        return max_page

    def get_target_info(self):

        for num in range(1, self.get_target_maxpage()):  # self.get_audio_page()
            url_json = f'https://www.ximalaya.com/revision/play/album?albumId={self.album_id}&pageNum={num}&sort=-1&pageSize=30'
            print(requests.get(url_json, headers=self.header, verify=False))
            r2 = requests.get(url_json, headers=self.header, verify=False).json()

            audio_dic = r2["data"]["tracksAudioPlay"]

            for audio in audio_dic:
                # print(audio["trackName"], audio["src"])
                track_names.append(audio["trackName"].replace("|", "-"))
                track_links.append(audio["src"])
                # self.audio_link_queue.put(audio["src"])
            # return track_names, track_links


    def download_file(self, name, url):
        # local_filename = url.split('/')[-1]
        # NOTE the stream=True parameter below
        # with requests.get(url, headers=self.header, verify=False, stream=True) as r:
        with requests.get(url, stream=True) as r:
            with open(f"{save_dirs}\\{self.album_name}\\{name}.m4a", 'wb') as f:
                print(f"{save_dirs}\\{self.album_name}\\")
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        # f.flush()
        # return local_filename

    def get_audio_download_thread(self):

        self.get_target_info()

        for name, link in tqdm(zip(track_names, track_links), desc=f"總共{obj.album_num}個檔案，目前下載"):
            self.download_file(name, link)
            time.sleep(.5)
            # t = Thread(target=self.download_file(name, link))
            # print("開始進行獲取檔案")
            # self.down_thread_log.append(t)

        # for t in self.down_thread_log:
        #     t.start()
        #     t.join(.1)


if __name__ == "__main__":
    obj = ximlaya()
    # obj.get_audio_page()
    url = input(f"請輸入網址：").strip()
    # url = "https://www.ximalaya.com/ertong/11689194/"
    # print(obj.re_url(url)[5], obj.re_url(url)[7])
    obj.album_type = obj.get_url(url)[5]
    obj.album_id = obj.get_url(url)[7]

    obj.get_target_info()
