import requests
import json
import csv
from bs4 import BeautifulSoup
import pymysql

mydb = pymysql.connect(
  host="localhost",
  port =3306,
  user="root",
  password="linhchi",
  db="soict"
)
def get_URL(mydb):
    for i in range(1,6):
        url = 'https://soict.hust.edu.vn/can-bo/page/'+ str(i)
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        get_url(soup, mydb)
        
def saveData(url, mydb):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    print("=======================================")
    cur = mydb.cursor()
    sql = "INSERT INTO soict (fullname, position, soict_url, introduce, research) VALUES (%s, %s, %s, %s, %s)"
    val = (get_name(soup), get_degree(soup, get_name(soup)), url, get_introduce(soup),get_research(soup, get_name(soup)) )
    cur.execute(sql, val)
    mydb.commit()

# Tên của giảng viên
def get_name(soup):
    name = soup.find_all("div", class_="article-inner");
    if(name[0].find("p", class_="lead")):
        return (name[0].find("p", class_="lead").find("span").text)    
    elif(name[0].find("p", class_="lead") == None and name[0].find_all("strong")):        
        return (name[0].find("strong").text)
    else:
        return None
#Chức vị trong trường, bộ môn giảng dạy của giảng viên
def get_degree(soup, name):
    if(name != None):
        degrees = soup.find_all("div", class_="col-inner")[0].find_all("p", class_="")
        for degree in degrees: 
            return degree.text
    else :
        return None
# Thông tin giới thiệu của giảng viên
def get_introduce(soup):
    name = soup.find_all("div", class_="col-inner");
    if(len(name) > 1):
        introduce = name[1].find("p", class_="")
        if(introduce != None):
            return introduce.text
        else:
            return None
#Link đến trang soict của từng giảng viên
def get_url(soup, mydb):
    getUrl = soup.find_all("article");
    for link in getUrl:
        urlTeacher = link.find("a");
        saveData(urlTeacher['href'], mydb)

# Lấy tất cả những nghiên cứu mà giảng viên quan tâm
def get_research(soup, name):
    str = ""
    array = []
    if(name != None):
        if(soup.find("div", class_="col-inner") != None):
            researches = soup.find("div", class_="col-inner").find_all("ul")
            for research in researches:
                for research in research.find_all("li") :
                    array.append(research.text)
        array = list( set(array) )
        str = "#".join(array)
    return str

if __name__ == '__main__':
    # get_url(soup);
    get_URL(mydb)


# Importing necessary libraries
import pandas as pd
import numpy as np
import pandas as pd
import numpy as np
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import RegexpTokenizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import string
import random
from PIL import Image
import requests
from io import BytesIO
import matplotlib.pyplot as plt
import pymysql

mydb = pymysql.connect(
  host="localhost",
  port =3306,
  user="root",
  password="linhchi",
  db="recommend"
)

# Reading the file
df = pd.read_csv("chi.csv")

#Reading the first five records

# Function for removing NonAscii characters
def _removeNonAscii(s):
    return "".join(i for i in s if  ord(i)<128)

# Function for converting into lower case
def make_lower_case(text):
    return text.lower()

# Function for removing stop words
def remove_stop_words(text):
    text = text.split()
    stops = set(stopwords.words("english"))
    text = [w for w in text if not w in stops]
    text = " ".join(text)
    return text

# Function for removing punctuation
def remove_punctuation(text):
    tokenizer = RegexpTokenizer(r'\w+')
    text = tokenizer.tokenize(text)
    text = " ".join(text)
    return text

# Function for removing the html tags
def remove_html(text):
    html_pattern = re.compile('<.*?>')
    return html_pattern.sub(r'', text)

# def search_title(title):
#     tf = TfidfVectorizer()
#     tfidf_matrix = tf.fit_transform(df.cleaned_title)
#     processed = re.sub("[^a-zA-Z0-9 ]", "", title.lower())
#     query_vec = tf.transform([title])
#     similarity = cosine_similarity(query_vec, tfidf_matrix).flatten()
#     indices = np.argpartition(similarity, -5)[-5:]
#     results = df.iloc[indices]
#     return results.head(5).title.array.tolist()

# def search_key(text):
#     tf = TfidfVectorizer()
#     tfidf_matrix = tf.fit_transform(df.Keyword)
#     processed = re.sub("[^a-zA-Z0-9 ]", "", text.lower())
#     query_vec = tf.transform([text])
#     similarity = cosine_similarity(query_vec, tfidf_matrix).flatten()
#     indices = np.argpartition(similarity, -5)[-5:]
#     results = df.iloc[indices]
#     return results.head(2).values.tolist()

# def get_teacher(idTeacher) :    
#     cur = mydb.cursor()
#     sql = "SELECT * FROM teachers where id = %s"
#     cur.execute(sql, idTeacher)
#     record = cur.fetchall()
#     return record

def updateData(df):
    topics = df.Cluster_ID.values.tolist()
    titleID = df.id.values.tolist()
    k = 0
    print(len(topics))
    # print(topics[0], titleID[0])
    for topic in topics:
        cur = mydb.cursor()
        val = [topic, titleID[k]]
        sql = "UPDATE titles SET topic = %s WHERE id = %s"
        cur.execute(sql, val)
        k = k+1
        mydb.commit()

        # print(topic, titleID[k])
    # cur = mydb.cursor()
    # sql = "SELECT * FROM titles where id = %s"
    # cur.execute(sql, idTeacher)
    # record = cur.fetchall()
    # return df.Cluster_ID.values.tolist()

# for a in df.Cluster_ID:
#     print(a)
# print(search_title("hello"))
print(updateData(df))