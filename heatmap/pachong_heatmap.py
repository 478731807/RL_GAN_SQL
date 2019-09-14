# https://mp.weixin.qq.com/s?__biz=MzI5MzQzMjU4Mw==&mid=2247487529&idx=1&sn=1de78b8e7141a118dd9c5c4eed15c8b2&chksm=ec736c41db04e557a639cd09722a3f3bec4643ca8f17bba17e92a2bd2b5802c6604355c5f001&scene=0&xtrack=1&key=dd5051400a9fb58f039a8acf24b9536d9ceca5303e36d6f09878cc021639e70a07a2aabff04519fe73d498d6c2477435848bde455e9d69c01dcd8e875574ba88afd10f012f06dabb3611ff790e6cd4c9&ascene=14&uin=MjA4NjMyMjkzOA%3D%3D&devicetype=Windows+10&version=62060833&lang=zh_CN&pass_ticket=I5KQYeQ4jpPG9uBdFjRVvm16WXRq6ukHz1Wq%2FLH61ndvGmkcVF5dkzqao5OLMBR3

import folium
import time
import requests
from urllib.request import quote
import numpy as np
import pandas as pd
import seaborn as sns
import webbrowser
from folium.plugins import HeatMap
address = ['北京','天津','石家庄','太原','呼和浩特','沈阳','大连','长春',
           '哈尔滨','上海','南京','杭州','宁波','合肥','福州','厦门','南昌',
           '济南','青岛','郑州','武汉','长沙','广州','深圳','南宁','海口',
           '重庆','成都','贵阳','昆明','拉萨','西安','兰州','西宁','银川','乌鲁木齐']


def getid(dizhi):
    url = "http://api.map.baidu.com/geocoder/v2/"
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'}
    payload = {
        'output': 'json',
        'ak': 'X8zlxPUdSe2weshrZ1WqnWxb43cfBI2N'
    }
    addinfo = []
    for i in dizhi:
        payload['address'] = i
        try:
            content = requests.get(url, params=payload, headers=header).json()
            addinfo.append(content['result']['location'])
            print("正在获取{}的地址！".format(i))
        except:
            print("地址{}获取失败，请稍后重试！".format(i))
            pass
        time.sleep(.5)
    print("所有地址均已获取完毕！！！")
    return (addinfo)


if __name__ == "__main__":
    # 计时开始：
    t0 = time.time()
    myaddress = getid(address)
    t1 = time.time()
    total = t1 - t0
    print("消耗时间：{}".format(total))
    lon = np.array([i["lng"] for i in myaddress], dtype=float)
    lat = np.array([i["lat"] for i in myaddress], dtype=float)
    scale = np.random.randint(100, 500, len(address))
    data1 = [[lat[i], lon[i], scale[i]] for i in range(len(address))]

    map_osm = folium.Map(location=[35, 110], zoom_start=5)
    HeatMap(data1).add_to(map_osm)
    file_path = "E:/研一/cities.html"
    map_osm.save(file_path)
    webbrowser.open(file_path)

