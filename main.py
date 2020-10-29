import requests
import random
import time
import re
import apscheduler
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

phone = ""
pwd = ""


def getcookie(url):
    "获取cookie和token"
    s_body = requests.get(url)
    s_cookie = s_body.headers.get("Set-Cookie")
    s_token = re.search('name="_token" value="([^"]+)"', s_body.text).group(1)
    d_cookie = {"cookies": s_cookie.split(";")[0], "token": s_token}
    return d_cookie


def temp():
    t = random.uniform(36.5, 37.2)
    return format(t, '.1f')


def auto(phone, pwd):
    "自动化登陆主函数"
    login_url = "http://banjimofang.com/student/login"
    temp_url = "http://banjimofang.com/student/course/17325/covid19d3"

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
    if res.status_code == 200:
        print("模拟登陆成功！")
    else:
        print("模拟登陆失败！")

    # 获取新cookie
    new_cookie = res.headers.get("Set-Cookie").split(";")[0]

    # 提交体温数据
    spost = "t1=" + "37.0" + "&t2=" + "37.0" + "&t3=" + "37.0"
    headers = {
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "banjimofang.com",
        "Referer": "http://banjimofang.com/student/course/17325/covid19d3",
        "Cookie": new_cookie
    }
    data = {
        "t1": str(temp()),
        "t2": str(temp()),
        "t3": str(temp())
    }
    resNew = requests.post(temp_url, headers=headers, data=data)
    if resNew.status_code == 200:
        print("模拟登陆成功！")
    else:
        print("模拟登陆失败！")
    if "提交成功" in resNew.text:
        print("体温提交成功！")
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    else:
        print("体温提交失败！")
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


def call_auto():
    auto(phone, pwd)


# 定时提交
if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(call_auto, 'cron', hour='6')
    scheduler.add_job(call_auto, 'cron', hour='12')
    scheduler.add_job(call_auto, 'cron', hour='15', minute='1')

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
