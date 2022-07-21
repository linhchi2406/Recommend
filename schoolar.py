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
  db="recommend"
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
    mycursor.execute("SELECT fullname, university FROM teachers")
    myresult = mycursor.fetchall()
    for x in myresult:
        id = id+1
        name = no_accent_vietnamese(str(x[0])).split(' ')
        link = url + "+".join(name)
        if (x[0] != "None"):
            print(link)
            get_URL(link, id, x[1])  
            # getLinkSchoolar(id) 
            print("//////")
   
# Lấy dữ liệu của từng giảng viên
def get_URL(link, id, university):
    time.sleep(6)
    linkTeacher = ""
    page = requests.get(link)
    soup = BeautifulSoup(page.text, "lxml")
    links = soup.find_all("div", class_="gs_ai_t")
    for link in links:
        email = link.find("div", class_="gs_ai_eml").text
        if (university == "hust") :
            if (email == 'Verified email at soict.hust.edu.vn' or email == 'Verified email at hust.edu.vn') :
                url = link.find("a")['href']
                linkTeacher = "https://scholar.google.com" + str(url)
                time.sleep(1)
                # print(linkTeacher)
        elif (university == "uet") :
            if (email == 'Verified email at vnu.edu.vn') :
                url = link.find("a")['href']
                linkTeacher = "https://scholar.google.com" + str(url)
                time.sleep(1)
                # print(linkTeacher)
        else :
            if (email == 'Verified email at dut.udn.vn') :
                url = link.find("a")['href']
                linkTeacher = "https://scholar.google.com" + str(url)
                time.sleep(1)
        cur = mydb.cursor()  
        sql = "UPDATE teachers SET link_schoolar = %s WHERE id = %s"
        val = [linkTeacher, id ] 
        cur.execute(sql,val)
        mydb.commit()
                # print(linkTeacher)
            # saveDataSpec1lized(linkTeacher, mydb)
            # saveSpecializedSoict(linkTeacher, id)
            # Lấy tất cả bài viết của giảng viên
            # driver = webdriver.Chrome(ChromeDriverManager().install())
            # driver.get(linkTeacher)
            # print(1)
            # time.sleep(5)
            # driver.find_element_by_css_selector("button[id='gsc_bpf_more']").click()
            # time.sleep(5)
            # elements = driver.find_elements_by_xpath("//td/a[@class='gsc_a_at']")
            # for elem in elements:
            #     time.sleep(1)
            #     print(elem.get_attribute("href"), id)
            #     cur = mydb.cursor()  
            #     sql = "INSERT INTO titles (soict_id, link_schoolar) VALUES ( %s, %s)"
            #     val = [int(id), elem.get_attribute("href") ] 
            #     cur.execute(sql,val)
            #     mydb.commit()

        break    
def getLinkSchoolar(id):
    cur = mydb.cursor()
    val = [id]
    sql = "SELECT * FROM titles where soict_id = %s"
    cur.execute(sql, val)
    records = cur.fetchall()
    for record in records:
        if (record[0] > 1712) :
            getTitle(record[1], id, record[0])

#Lấy tất cả thông tin về các sản phẩm của giảng viên
def getTitle(link, id, ids) :
    # page =  requests.get(link)
    # soup = BeautifulSoup(page.content, "html.parser")
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(link)
    title = None
    description = None
    # if (soup.find("div", class_="gsh_small")) :
    #     if(soup.find("a", class_="gsc_oci_title_link")) :
    #         title = soup.find("a", class_="gsc_oci_title_link").text
    #     elif (soup.find('div', id_="gsc_oci_title")) :
    #         title = soup.find('div', id_="gsc_oci_title").text
    #     else :
    #         title = soup.find("div", id="gsc_oci_title_wrapper").text
    #     description = soup.find("div", class_="gsh_small").text
    if(driver.find_elements_by_xpath("//a[@class='gsc_oci_title_link']")) :
        title = driver.find_elements_by_xpath("//a[@class='gsc_oci_title_link']")[0].text
    elif (driver.find_elements_by_xpath("//div[@id = 'gsc_oci_title']")) :
        title = driver.find_elements_by_xpath("//div[@id='gsc_oci_title']")[0].text
    elif (driver.find_elements_by_xpath("//div[@id='gsc_oci_title_wrapper']")):
        title =driver.find_elements_by_xpath("//div[@id='gsc_oci_title_wrapper']")[0].text
    if (driver.find_elements_by_xpath("//div[@class='gsh_small']")) :
        description = driver.find_elements_by_xpath("//div[@class ='gsh_small']")[0].text
    time.sleep(3)
    driver.quit
    cur = mydb.cursor()  
    sql = "UPDATE titles SET title = %s, description = %s WHERE id = %s"
    val = [title, description, int(ids)]
    print(val);

    cur.execute(sql,val)
    mydb.commit()
    # mydb.close()


#lấy tất cả thông tin về đồng tác giả
def getCoAuthor():
    cur = mydb.cursor()
    val = []
    sql = "SELECT * FROM titles"
    cur.execute(sql, val)
    records = cur.fetchall()
    for record in records:
        if (record[0]>1732):
            print(record[0])
            saveCoAuthor(record[1], record[2], record[0])
    # time.sleep(2)
    # page =  requests.get(link)
    # soup = BeautifulSoup(page.content, "html.parser")
    # links = soup.find_all("td", class_="gsc_a_t")
    # for link in links :
    #     url = "https://scholar.google.com" + str(link.find("a", class_="gsc_a_at")['href'])
    #     print(url)
    #     saveCoAuthor(url, id)

def split_name(name):
    array = []
    for test in name.split("-") :
        for test1 in test.split(" "):
            array.append(test1)
    return array
  

# Lấy đồng tác giả
def saveCoAuthor(link, id, titleId) :
    time.sleep(5)
    page =  requests.get(link)
    soup = BeautifulSoup(page.content, "lxml")
    result = 0
    authors = soup.find("div", class_="gsc_oci_value").text
    authors = authors.split(", ")
    for item in authors:
        array = split_name(no_accent_vietnamese(item))
        cur = mydb.cursor()
        cur1 = mydb.cursor()
        sql1 = "SELECT fullname FROM soict where id = %s"
        sql = "SELECT * FROM coauthor where soict_id = %s"
        val = [id]
        cur.execute(sql, val)
        cur1.execute(sql1, val)
        records = cur.fetchall()
        teachers = cur1.fetchall()
        if (set(array) == set(split_name(no_accent_vietnamese(teachers[0][0])))):
            result = 1
        print("....")
        for record in records:
            array1 = split_name(no_accent_vietnamese(record[1]))
            if (set(array) == set(array1)):
                result = 1
                break
        if (result == 0):
            print("ok")
            ids = 0
            sql = "SELECT id, fullname FROM soict"
            val = []
            cur.execute(sql, val)
            records = cur.fetchall()
            for record in records:
                if (set(array) == set(split_name(no_accent_vietnamese(record[1])))) :
                    ids = record[0]
                    break
            sql = "INSERT INTO coauthor (name, soict_id, teacher_id, title_id) VALUES (%s, %s, %s, %s)"
            val = [item, id, ids, titleId]
            cur.execute(sql, val)
            print("Luu Xong")
            mydb.commit()
 
#lấy tất cả thông tin về chuyên ngành nghiên cứu
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
    time.sleep(10)
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

# Lưu chuyên ngành và giảng viên
def saveSpecializedSoict(link, id) :
    time.sleep(8)
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
            sql = "INSERT INTO soict_specializeds (soict_id, specialized_id) VALUES (%s, %s)"
            val = [id, record[0][0]]
            cur.execute(sql, val)
        mydb.commit()


if __name__ == '__main__':
    # get_url(soup);
    getURL(mydb, url)
