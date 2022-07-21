import requests
import json
import csv
from bs4 import BeautifulSoup
import pymysql
import re
import math
import time
from time import sleep
from collections import Counter
mydb = pymysql.connect(
  host="localhost",
  port =3306,
  user="root",
  password="linhchi",
  db="recommend"
)

url ="https://dblp.uni-trier.de/search?q="
# Kiểm tra độ tương đồng giữa 2 string
Word = re.compile(r'\w+')

def get_cosine(vec1, vec2):
     intersection = set(vec1.keys()) & set(vec2.keys())
     numerator = sum([vec1[x] * vec2[x] for x in intersection])
     sum1 = sum([vec1[x]**2 for x in vec1.keys()])
     sum2 = sum([vec2[x]**2 for x in vec2.keys()])
     denominator = math.sqrt(sum1) * math.sqrt(sum2)

     if not denominator:
        return 0.0
     else:
        return float(numerator) / denominator

def text_to_vector(text):
     words = Word.findall(text)
     return Counter(words)

# Chuyển sang dạng không có dấu
def no_accent_vietnamese(s):
    s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    s = re.sub(r'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
    s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
    s = re.sub(r'[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
    s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
    s = re.sub(r'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
    s = re.sub(r'[ìíịỉĩ]', 'i', s)
    s = re.sub(r'[ÌÍỊỈĨ]', 'I', s)
    s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
    s = re.sub(r'[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', s)
    s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
    s = re.sub(r'[ỲÝỴỶỸ]', 'Y', s)
    s = re.sub(r'[Đ]', 'D', s)
    s = re.sub(r'[đ]', 'd', s)
    return s
# tạo các URL search theo tên teacher
def getURL(mydb):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT id, link_dblp FROM teachers")
    myresult = mycursor.fetchall()
    for x in myresult:
        if (x[1] != None and x[1] != "") :
            get_URL(x[0], x[1])
# Lấy Các URL có thể lấy dữ liệu của từng người
def get_URL(id, links):
    for link in links.split(", "):
        getLinkTitle(id, link)

def getLinkTitle(id, link):
    if (id>169):
        time.sleep(5)
        page = requests.get(link)
        soup = BeautifulSoup(page.content, "html.parser")
        for li in soup.find_all("li", class_="entry"):
            nav = li.find("nav", class_="publ")
            cite = li.find("cite").find("span", class_="title").text
            if (checkTitleDuplication(id, cite)==0) :
                print(1)
                val = [id, cite, nav.find_all("li")[0].find("a")['href'], 1]
                saveTitle(val)

def checkTitleDuplication(id, title) :
    array = getTitleSchoolar(id)
    if (len(array) == 0) :
        return 0
    for arr in array:
        if get_cosine(text_to_vector(arr.lower()), text_to_vector(title.lower())) > 0.7 :
            return 1
    return 0

# Tach ten de so sanh, luu DB
def split_name(name):
    array = []
    for test in name.split("-") :
        for test1 in test.split(" "):
            array.append(test1)
    return array

def getTitleSchoolar(id) :
    array = []
    cur = mydb.cursor()
    sql = "SELECT title FROM titles where teacher_id = %s"
    val = [id]
    cur.execute(sql, val)
    records = cur.fetchall()
    mydb.commit()
    for record in records:
        array.append(no_accent_vietnamese(record[0]))
    return array

#Lưu dữ liệu vào bảng danh sách các nghiên cứu
def saveTitle(val) :
    cur = mydb.cursor()
    sql = "INSERT INTO titles (teacher_id, title, link, dblp) VALUES (%s, %s, %s, %s)"
    cur.execute(sql, val)
    mydb.commit()

if __name__ == '__main__':
    # get_url(soup);
    getURL(mydb)
