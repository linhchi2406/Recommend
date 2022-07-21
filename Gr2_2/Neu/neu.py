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
  db="soict"
)
def get_URL(mydb):
    url = 'https://sitde.neu.edu.vn/vi/gioi-thieu-vien-cnttkts/co-cau-to-chuc-4631?fbclid=IwAR1gMUlRuT3wsKcgOgZoYuYoVH82CQwRq1qPMBmz5kLdxZ24qUMUHwmMa6k'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    trs = soup.find_all("tr")
    for tr in trs:
        tds = tr.find_all("td")
        if(tds[0].find("a")) :
            print(tds[0].find("a").text)
        # for td in tds:
        #     if(td.find("a")) :
        #         print(tds[0].find("a")["href"])

    # saveData(soup, mydb)
    # getName(soup)
    # getTitle()    
def saveData(val, mydb):
    cur = mydb.cursor()
    sql = "INSERT INTO teacher_duts (fullname, position, email, degree, introduce, university, link) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cur.execute(sql, val)
    mydb.commit()

# Tên của giảng viên
def getName(soup):
    array = []
    trs = soup.find_all("tr");
    i = 0
    degree = None
    for tr in trs:
        if (i>0) :
            tds = tr.find_all("td")
            if (len(tds) > 2) :              
                if (tds[2].find("a") != None):
                    fullname = tds[2].find_all("strong")[0].text
                    email = tds[3].find("a").text  
                    link = tds[2].find("a")['href']
                    position = tds[2].text
                    page = requests.get(link)
                    soup = BeautifulSoup(page.content, "html.parser")
                    tables = soup.find_all("tr")
                    for table in tables:
                        texts = table.find_all("td")
                        if (texts[0].text == 'Học vị:'):
                            degree = texts[1].text
                    university = "dut"
                array = []
                array.append(fullname)
                array.append(position)
                array.append(email)
                array.append(degree)
                array.append('')
                array.append(university)
                array.append(link)
                # saveData(array, mydb)
                getTitle(link)
        i =  i+1
#Chức vị trong trường, bộ môn giảng dạy của giảng viên

def getTitle():
    cur = mydb.cursor()
    val = []
    sql = "SELECT id, link FROM teacher_duts"
    cur.execute(sql, val)
    records = cur.fetchall()
    for record in records:
        print(record[0], record[1])
        if(record[0] > 31) :
            time.sleep(3)
            page = requests.get(record[1])
            soup = BeautifulSoup(page.content, "html.parser")
            href = soup.find_all("a")
            for hre in href:
                if(hre.text == 'Bài báo, báo cáo khoa học'):
                    time.sleep(5)
                    page = requests.get(hre["href"])
                    soup = BeautifulSoup(page.content, "html.parser")
                    tables = soup.find("div", id="g7vnContent").find_all("table")
                    tds = tables[1].find_all("td")
                    for td in tds :
                        if(td.find("a") != None):
                            getContent(td.find("a")["href"], record[0])
def getContent(link, id):
    time.sleep(3)
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    content = soup.find("div", class_ = "form4")
    tds = content.find_all("td")
    name = tds[0].text
    description = tds[7].text
    cur = mydb.cursor()
    val = [name, id, link, description]
    sql = "INSERT INTO dut_titles (name, teacher_dut_id, link, description) VALUES (%s, %s, %s, %s)"
    cur.execute(sql, val)
    mydb.commit()

  
if __name__ == '__main__':
    # get_url(soup);
    get_URL(mydb)
