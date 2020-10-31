import csv

phone = input("请输入手机号\n")
pwd = input("请输入密码\n")

row = [phone, pwd]
out = open("account.csv", "a", newline = "")
csv_writer = csv.writer(out, dialect = "excel")
csv_writer.writerow(row)