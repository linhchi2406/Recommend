from asyncio.windows_events import NULL
import requests
import sys
from bs4 import BeautifulSoup
import pymysql
import re
import lxml
from time import sleep
import time


mydb = pymysql.connect(
  host="localhost",
  port =3306,
  user="root",
  password="linhchi",
  db="recommend"
)
arr = []

url ="https://scholar.google.com/citations?hl=en&view_op=search_authors&mauthors="

# tạo các URL search theo tên teacher
def getURL(mydb):
    mycursor = mydb.cursor()
    mycursor.execute("SELECT id, link_schoolar FROM teachers")
    myresult = mycursor.fetchall()
    for x in myresult:
        if (x[0] > 253) :
            if (x[1] != None and x[1] != "") :
                get_URL(x[0], x[1])
# Lấy dữ liệu của từng giảng viên
def get_URL(id, link):
    time.sleep(6)
    page =  requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    links = soup.find_all("a", class_="gsc_a_at")
    for elem in links:
        time.sleep(4)
        getTitle("https://scholar.google.com" + elem["href"], id)
        print(id, elem["href"])
#Lấy tất cả thông tin về các sản phẩm của giảng viên
def getTitle(link, id) :
    time.sleep(5)
    page =  requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    title = None
    description = None
    if (soup.find("a", class_="gsc_oci_title_link") != None):
        title = soup.find("a", class_="gsc_oci_title_link").text
    elif(soup.find("a", id="gsc_oci_title") != None):
        title = soup.find("a", id="gsc_oci_title").text
    else:   
        title = soup.find("div", id="gsc_oci_title_wrapper").text

    if(soup.find("div", class_="gsh_csp") != None):
        description = soup.find("div", class_="gsh_csp").text
    elif(soup.find("div", class_="gsh_small") != None):
        description = soup.find("div", class_="gsh_small").text
    elif(soup.find("div", class_="gsc_oci_value") != None):
        description = soup.find("div", class_="gsc_oci_value").text
    
    mydb = pymysql.connect(
    host="localhost",
    port =3306,
    user="root",
    password="linhchi",
    db="recommend"
    )
    cur = mydb.cursor()  
    sql = "INSERT INTO titles (teacher_id, title, abstract, link, schoolar) VALUES ( %s, %s, %s, %s, %s)"
    val = [int(id), title, description, link, "1"]
    print(id, title);
    cur.execute(sql,val)
    mydb.commit()
    mydb.close()
if __name__ == '__main__':
    # get_url(soup);
    getURL(mydb)
