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
    spost = "_token=" + str(token) + "&username=" + str(phone) + "&password=" + str(pwd)
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

# 随机生成合理的gps偏移
def getGpsOffset():
    gpsOffsetX = random.uniform(-0.00004, 0.00004)
    gpsOffsetY = random.uniform(-0.00004, 0.00004)
    report_gpsX = format(gps[0] + gpsOffsetX, '.5f')
    report_gpsY = format(gps[1] + gpsOffsetY, '.5f')
    report_gps = str(report_gpsX) + "," + str(report_gpsY)
    return report_gps

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

# 获取日报的form_id
def getReportID(cookie):
    report_url = "http://www.banjimofang.com/student/course/"+course+"/profiles/29"
    headers = {
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "banjimofang.com",
        "Referer": report_url,
        "Cookie": cookie
    }
    data = {}
    res = requests.post(report_url, headers=headers, data=data)
    regex = r"(?<=name=\"form_id\" value=\").*?(?=\">)"
    match = re.search(regex, res.text, flags=0)
    if match == None:
        print("获取表单ID失败")
    return(match.group(0))


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

# 日报函数
def report(cookie):
    if cookie == None:
        print("登陆失败")
        return
    report_url = "http://www.banjimofang.com/student/course/"+course+"/profiles/29"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "banjimofang.com",
        "Referer": report_url,
        "Cookie": cookie,
        "Upgrade-Insecure-Requests": "1",
        "Origin": "http://banjimofang.com",
        # "Connection": "keep-alive"
    }
    gpsOffset = getGpsOffset()
    data = {
        "form_id": str(getReportID(cookie)),
        "formdata[b]": address + "|"+gpsOffset,
        "formdata[a][]": "2",
        "formdata[c]": '',
        "formdata[d]": str(temp()),
        "_bjmf_fields_s":'{"gps":{"b"}}',
        "formdata[gps_address]": address + "|"+gpsOffset,
        "formdata[gps_xy]": gpsOffset
    }
    # res = requests.post(report_url, headers=headers, data=json.dumps(data,separators=(",",";")))
    res = requests.post(report_url, headers=headers, data=data)
    if "新增成功" in res.text:
        print("日报提交成功")
    else:
        print("日报提交失败")

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

def call_report():
    with open("account.csv", "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        column = [row for row in reader]
    print(column)
    for index in range(len(column)):
        report(login(column[index]["phone"], column[index]["pwd"]))

#随机在8-10点调用日报函数
def randomCall():
    randomHour = format(random.uniform(8, 9), '.0f')
    randomMinute = format(random.uniform(1, 59), '.0f')
    randomSecond = format(random.uniform(1, 59), '.0f')
    today = datetime.date.today()
    run_date = str(today) +" " + randomHour + ":" + randomMinute + ":" + randomSecond
    print("您的日报提交将在" + run_date +"进行")
    reportScheduler = BlockingScheduler(timezone='Asia/Shanghai')
    reportScheduler.add_job(call_report, 'date', run_date=run_date)
    reportScheduler.start()

if __name__ == '__main__':
    print("班级魔方自动化程序开始运行")
    scheduler = BlockingScheduler(timezone='Asia/Shanghai')
    scheduler.add_job(call_temp, 'cron', hour='6')
    scheduler.add_job(call_temp, 'cron', hour='12', minute='0')
    scheduler.add_job(call_temp, 'cron', hour='17', minute='1')
    scheduler.add_job(call_sign, 'cron', hour='21', minute='15')
    scheduler.add_job(randomCall, 'cron', hour='2', minute='0')

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass