from asyncio.windows_events import NULL
import requests
import sys
from bs4 import BeautifulSoup
import pymysql
import re
import lxml
from time import sleep
import time
from selenium import webdriver
from selenium.webdriver.chrome import service
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


mydb = pymysql.connect(
  host="localhost",
  port =3306,
  user="root",
  password="linhchi",
  db="soict"
)
arr = []

url ="https://scholar.google.com/citations?hl=en&view_op=search_authors&mauthors="

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
def getURL(mydb, url):
    id = 0
    mycursor = mydb.cursor()
    mycursor.execute("SELECT fullname FROM teacher_duts")
    myresult = mycursor.fetchall()
    for x in myresult:
        id = id+1
        name = no_accent_vietnamese(str(x[0])).split(' ')
        link = url + "+".join(name)
        if (x[0] != "None"):
            get_URL(link, id)  
            print("//////")
   
# Lấy dữ liệu của từng giảng viên
def get_URL(link, id):
    time.sleep(4)
    page = requests.get(link)
    soup = BeautifulSoup(page.text, "lxml")
    links = soup.find_all("div", class_="gs_ai_t")
    for link in links:
        email = link.find("div", class_="gs_ai_eml").text
        if (email == 'Verified email at dut.udn.vn') :
            url = link.find("a")['href']
            linkTeacher = "https://scholar.google.com" + str(url)
            # print(linkTeacher, id)
            # saveDataSpecialized(linkTeacher, mydb)
            # saveSpecializedSoict(linkTeacher, id)
            getTitle(linkTeacher, id)

def getSpecialized(soup):
    specializeds = soup.find("div", id="gsc_prf_int")
    specializeds = specializeds.find_all("a")
    array = []
    if (specializeds != None) : 
        for specialized in specializeds:
            array.append(specialized.text)
    return array
# Lưu dữ liệu chuyên ngành vào DB
def saveDataSpecialized(link, mydb):
    time.sleep(2)
    page =  requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    val = getSpecialized(soup)
    if len(val) > 0 :
        cur = mydb.cursor()
        for item in val:
            sql = "SELECT * FROM specializeds where name = %s"
            cur.execute(sql, item)
            record = cur.fetchall()
            if(len(record) == 0):
                sql = "INSERT INTO specializeds (name) VALUES (%s)"
                cur.execute(sql, item)
            mydb.commit()

def saveSpecializedSoict(link, id) :
    time.sleep(2)
    page =  requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    specializeds = soup.find("div", id="gsc_prf_int")
    specializeds = specializeds.find_all("a")
    for specialized in specializeds:
        cur = mydb.cursor()
        val = specialized.text
        sql = "SELECT * FROM specializeds where name = %s"
        cur.execute(sql, val)
        record = cur.fetchall()
        if (len(record) != 0):
            sql = "INSERT INTO dut_specializeds (teacher_dut_id, specialized_id) VALUES (%s, %s)"
            val = [id, record[0][0]]
            cur.execute(sql, val)
        mydb.commit()

def getTitle(link, id) :
    time.sleep(6)
    page =  requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    titles = soup.find_all("tr", class_="gsc_a_tr")
    cur = mydb.cursor()
    for title in titles:
        # sql = "INSERT INTO dut_titles (name, description, teacher_dut_id) VALUES (%s, %s, %s)"
        # val = [title.find("a", class_="gsc_a_at").text, title.find("span", class_="gsc_a_h gsc_a_hc gs_ibl").text ]        
        # cur.execute(sql,val)
        # mydb.commit()
        saveTitle("https://scholar.google.com" + title.find("a")["href"], id)
def saveTitle(link, id):
    print(1)
    if (id > 3) :
        time.sleep(8)
        page =  requests.get(link)
        description = ''
        name = ''
        print(link)
        soup = BeautifulSoup(page.content, "html.parser")
        if (soup.find("a", class_="gsc_oci_title_link") != None):
            name = soup.find("a", class_="gsc_oci_title_link").text
        elif(soup.find("a", id="gsc_oci_title") != None):
            name = soup.find("a", id="gsc_oci_title").text
        else:   
            name = soup.find("div", id="gsc_oci_title_wrapper").text

        if(soup.find("div", class_="gsh_csp") != None):
            description = soup.find("div", class_="gsh_csp").text
        elif(soup.find("div", class_="gsh_small") != None):
            description = soup.find("div", class_="gsh_small").text
        elif(soup.find("div", class_="gsc_oci_value") != None):
            description = soup.find("div", class_="gsc_oci_value").text
        cur = mydb.cursor()
        sql = "SELECT * FROM dut_titles where name = %s"
        val = [name]
        cur.execute(sql, val)
        record = cur.fetchall()
        if(len(record) == 0):
            sql = "INSERT INTO dut_titles (name, description, link, teacher_dut_id) VALUES (%s, %s, %s, %s)"
            cur.execute(sql, [name, description, link, id ])
        mydb.commit()

if __name__ == '__main__':
    getURL(mydb, url)
