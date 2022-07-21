import requests
import json
import csv
from bs4 import BeautifulSoup
import pymysql
from time import sleep
import time

mydb = pymysql.connect(
  host="localhost",
  port =3306,
  user="root",
  password="linhchi",
  db="recommend"
)
def get_URL(mydb):
    url = 'https://www.fit.uet.vnu.edu.vn/giang-vien/'
    page = requests.get(url)
    i=0
    soup = BeautifulSoup(page.content, "html.parser")
    tables = soup.find_all("table")
    time.sleep(4)
    for table in tables:
        # print( table.find("tbody").text)
        abc = table.find("tbody")
        tds = abc.find_all("td")
        length = int((len(tds)) / 5)
        # print(length)
        for j in range(0, length):
            name = tds[5*j+1].text.split('.')[-1]
            email = tds[5*j+2].text
            position = tds[5*j+4].text
            degree = tds[5*j+1].text
            val = [name, email, position, degree, "uet"]
            saveData(val, mydb)
        i = i+1
def saveData(val, mydb):
    cur = mydb.cursor()
    sql = "INSERT INTO teachers (fullname, email, position, degree, university) VALUES (%s, %s, %s, %s, %s)"
    cur.execute(sql, val)
    mydb.commit()
  
if __name__ == '__main__':
    # get_url(soup);
    get_URL(mydb)
