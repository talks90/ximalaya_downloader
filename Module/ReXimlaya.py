# -*- coding: UTF-8 -*-
#! Phython3
from Module import net_fn
from bs4 import BeautifulSoup
import os
import re
from tqdm import tqdm
import concurrent.futures


class ReXimlaya:
    def __init__(self):
        self.Net = net_fn.Net()
        self.save_dirs = r'F:\Downloads\喜馬拉雅'  # 檔案儲存位址

        self.max_download_process = 10  # 最大線程數
        self.target_url = ""
        self.target_maxpage = 0

        self.pg_header_str = ""
        self.pg_header = None
        self.pg_rs = None
        self.pg_bs = None

        self.album_type = ""
        self.album_id = ""
        self.album_num = 0
        self.album_name = ""

        self.track_names = []
        self.track_links = []

    def parse_bs(self, target_rs):
        target_decode = target_rs.content.decode()
        target_bs = BeautifulSoup(target_decode, 'html.parser')
        return target_bs

    def get_url(self, url):
        short_url = re.findall('[^/#]*', url)
        return short_url

    def get_pg_info(self):
        self.pg_header_str = "Accept: */*###Accept - Encoding: gzip, deflate, br###Accept-Language: zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7###User-Agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36###xm-sign: e97b5fe70a72779a7420954a40597ce8(16)1557543596528(99)1557543602476"
        self.pg_header = self.Net.get_header_dict(self.pg_header_str)
        self.pg_rs = self.Net.Get(url=self.target_url, header_string=self.pg_header_str)
        self.pg_bs = self.parse_bs(self.pg_rs)

        h2_text = self.pg_bs.find('h2', class_="_OO").text
        h2_size = re.findall(r'(\d+-*\d*)', h2_text)

        self.album_num = int(h2_size[0])
        self.album_type = self.get_url(obj.target_url)[5]
        self.album_id = self.get_url(obj.target_url)[7]

        if self.pg_bs.find_all("span", class_="_dN2"):
            self.target_maxpage = int(self.pg_bs.find_all("span", class_="_dN2")[-1].text) + 1
        else:
            self.target_maxpage = 2

        for num in range(1, self.target_maxpage):
            revision_url = f'https://www.ximalaya.com/revision/play/album?albumId={self.album_id}&pageNum={num}&sort=-1&pageSize=30'
            rs_reurl = self.Net.Get(url=revision_url, header_string=self.pg_header_str, SSL_verify=False)
            url_json = rs_reurl.json()
            audio_dic = url_json["data"]["tracksAudioPlay"]

            for a in audio_dic:
                self.track_names.append(re.sub(r"[\/:*?<>|]+", "-", a["trackName"]))
                self.track_links.append(a["src"])

    def make_album_dir(self, target_bs):
        title_name = target_bs.find('h1', class_="title _t4_").string
        self.album_name = re.sub(r"[\/:*?<>|]+", "-", title_name)      # 存檔注意檔名規則
        paths = f"{self.save_dirs}\\{self.album_name}"
        if not os.path.exists(paths):
            os.makedirs(paths, exist_ok=True)
            return True
        else:
            print(f'{self.album_name}資料夾已存在')
            return False

    def download_audio(self):
        self.get_pg_info()
        self.make_album_dir(self.pg_bs)  # 新建目錄

        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_download_process) as executor:
            for n in tqdm(range(self.album_num), desc=f"[{self.album_name}]總共{self.album_num}個檔案，目前下載進度"):
                link = self.track_links[n]
                filename = f"{self.save_dirs}\\{self.album_name}\\{self.track_names[n]}.m4a"
                executor.map(self.Net.Download(link, filename), chunksize=10)
                # print(f'{self.track_names[n]} 下載成功')


if __name__ == "__main__":
    obj = ReXimlaya()  # 初始化物件
    obj.target_url = input(f"請輸入網址：").strip()  # 輸入網址

    obj.download_audio()
