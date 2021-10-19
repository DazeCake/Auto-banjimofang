import main
import sys
import csv

if main.login(sys.argv[1],sys.argv[2]) != None:
    with open("account.csv", "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        column = [row for row in reader]
    for index in range(len(column)):
        if column[index]["phone"] != sys.argv[1]:
            continue
        else:
            print("Existing")
            sys.exit()
    row = [sys.argv[1], sys.argv[2]]
    out = open("account.csv", "a", newline = "")
    csv_writer = csv.writer(out, dialect = "excel")
    csv_writer.writerow(row)
    print(True)
else:
    print(False)