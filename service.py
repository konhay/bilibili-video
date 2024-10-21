"""
b 站视频下载程序
version: 1st
author: bing
date: 20241021
"""

import os
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import re
import json
import warnings

warnings.filterwarnings('ignore')

#使用登录后cookie下载视频有更高的清晰度
cookie = "buvid3=6F3D3E00-9BA4-C8A7-D410-97E6E30138D752529infoc; b_nut=1707920652; _uuid=E7...."

while True:
    opt = input("请输入下载类型（1-按用户 2-按视频）: ")

    if opt == "1":
        user = input("请输入用户编号: ")
        print("开始挖掘她的全部视频：", user)

        # get video url
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"') #防止403 Nginx forbidden.
        driver = webdriver.Chrome(chrome_options=options)
        vlist = []
        p = 1
        while True:
            url = "https://space.bilibili.com/"+user+"/video?pn="+str(p)
            driver.get(url)
            time.sleep(3)
            html = driver.execute_script('return document.documentElement.outerHTML')
            bsObj = BeautifulSoup(html, 'html.parser')
            content = bsObj.findAll("li", {"class": "small-item fakeDanmu-item"})
            if len(content)==0: break
            for i in content:
                vid = i.attrs['data-aid']
                vlist.append(vid)
                print(vid)
            p+=1
        print("len(vlist) is", len(vlist))
        driver.quit()

        # download video (https://zhuanlan.zhihu.com/p/703972838)
        for i in vlist:
            if os.path.isfile("video\\"+user+i+".mp4"):
                print(i, "existed.")
                continue

            url = "https://www.bilibili.com/video/"+i+"/"
            headers = {
                "Referer": url,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Cookie": cookie
            }
            try:
                response = requests.get(url=url, headers=headers, verify=False)
                html = response.text
                # title = re.findall('title="(.*?)"', html)[0]
                # print("title:", title)
                info = re.findall('window.__playinfo__=(.*?)</script>', html)[0]
                json_data = json.loads(info)
                video_url = json_data['data']['dash']['video'][0]['baseUrl']
                # print("video:", video_url)
                # audio_url = json_data['data']['dash']['audio'][0]['baseUrl']
                # print("audio:", audio_url)
                video_content = requests.get(url=video_url, headers=headers).content
                # audio_content = requests.get(url=audio_url, headers=headers).content
                with open('video\\' + user+i + '.mp4', mode='wb') as v:
                    v.write(video_content)
                    print(user+i + '.mp4 saved')
                # with open('video\\' + user+i + '.mp3', mode='wb') as a:
                #     a.write(audio_content)
                # print(user + i + '.mp3 saved')
            except Exception as e:
                print(i, "failed.")
                continue
        break

    elif opt == "2":
        url = input("请输入视频地址: ").strip()
        try:
            vid = [y for y in [x for x in url.split("/") if "BV" in x][0].split("=") if "BV" in y][0]
        except Exception as e:
            print("invalid url.")
            continue
        url = "https://www.bilibili.com/video/"+vid+"/"
        print("开始下载该视频：", url)

        headers = {
            "Referer": url,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Cookie": cookie
        }

        response = requests.get(url=url, headers=headers, verify=False)
        html = response.text
        info = re.findall('window.__playinfo__=(.*?)</script>', html)[0]
        json_data = json.loads(info)
        video_url = json_data['data']['dash']['video'][0]['baseUrl']
        video_content = requests.get(url=video_url, headers=headers).content

        with open('video\\' + vid + '.mp4', mode='wb') as v:
            v.write(video_content)
            print(vid + '.mp4 saved')
        break

    else:
        continue
