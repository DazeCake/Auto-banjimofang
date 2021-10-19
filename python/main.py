#!/usr/bin/python3

import requests
import random
import time
import csv
import re
from datetime import datetime
import os
from apscheduler.schedulers.blocking import BlockingScheduler

# 课程id
course = ""
# gps的xy坐标
gps = [0, 0]
# 地址
address = ""


# 获取cookie和token
def getcookie(url):
    s_body = requests.get(url)
    s_cookie = s_body.headers.get("Set-Cookie")
    s_token = re.search('name="_token" value="([^"]+)"', s_body.text).group(1)
    d_cookie = {"cookies": s_cookie.split(";")[0], "token": s_token}
    return d_cookie


# 登陆函数
def login(phone, pwd):
    login_url = "http://banjimofang.com/student/login"

    # 获取前置cookie
    d_cookie = getcookie(login_url)
    # 模拟登陆
    cookies = d_cookie.get("cookies")
    token = d_cookie.get("token")
    spost = "_token=" + token + "&username=" + phone + "&password=" + pwd
    headers = {
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Cache-Control": "no-cache",
        "Content-Length": str(len(spost)),
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "banjimofang.com",
        "Cookie": cookies
    }
    data = {
        "_token": token,
        "username": phone,
        "password": pwd
    }
    res = requests.post(login_url, headers=headers, data=data)
    if "当前账号" in res.text:
        new_cookie = res.headers.get("Set-Cookie").split(";")[0]
        return new_cookie
    else:
        print("用户: "+str(phone)+" 账号或密码错误")
        return None


# 随机生成合理的体温
def temp():
    t = random.uniform(36.5, 37.2)
    return format(t, '.1f')


# 提交体温数据
def postTemp(cookie):
    if cookie == None:
        print("登陆失败")
        return
    temp_url = "http://banjimofang.com/student/course/" + \
        str(course)+"/covid19d3"
    # spost = "t1=" + "37.0" + "&t2=" + "37.0" + "&t3=" + "37.0"
    headers = {
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "banjimofang.com",
        "Referer": temp_url,
        "Cookie": cookie
    }
    data = {
        "t1": str(temp()),
        "t2": str(temp()),
        "t3": str(temp())
    }
    resNew = requests.post(temp_url, headers=headers, data=data)
    if "提交成功" in resNew.text:
        print("体温提交成功！")
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    else:
        print("体温提交失败！")
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


# 获取签到id
def getPunchsID(cookie):
    sign_url = "http://banjimofang.com/student/course/"+str(course)+"/punchs"
    headers = {
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "banjimofang.com",
        "Referer": sign_url,
        "Cookie": cookie
    }
    data = {}
    res = requests.post(sign_url, headers=headers, data=data)
    return res.text[res.text.index("id=\"punchcard_")+14:res.text.index("id=\"punchcard_")+20]


# 签到函数
def sign(cookie):
    if cookie == None:
        print("登陆失败")
        return
    sign_url = "http://banjimofang.com/student/course/"+str(course)+"/punchs"
    headers = {
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "banjimofang.com",
        "Referer": sign_url,
        "Cookie": cookie
    }
    data = {
        "id": getPunchsID(cookie),
        "lat": gps[1],
        "lng": gps[0],
        "acc": "15",
        "res": "",
        "gps_addr": address
    }
    res = requests.post(sign_url, headers=headers, data=data)
    if "签到成功" in res.text:
        print("签到成功")
    else:
        print("签到失败")


def call_temp():
    with open("account.csv", "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        column = [row for row in reader]

    for index in range(len(column)):
        postTemp(login(column[index]["phone"], column[index]["pwd"]))


def call_sign():
    with open("account.csv", "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        column = [row for row in reader]

    for index in range(len(column)):
        sign(login(column[index]["phone"], column[index]["pwd"]))


if __name__ == '__main__':
    print("班级魔方自动化程序开始运行")
    scheduler = BlockingScheduler()
    scheduler.add_job(call_temp, 'cron', hour='6')
    scheduler.add_job(call_temp, 'cron', hour='12', minute='0')
    scheduler.add_job(call_temp, 'cron', hour='17', minute='1')
    scheduler.add_job(call_sign, 'cron', hour='21', minute='15')

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
