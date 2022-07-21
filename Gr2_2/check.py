from asyncio.windows_events import NULL
import requests
import sys
from bs4 import BeautifulSoup
import pymysql
import re
import lxml
import time

mydb = pymysql.connect(
  host="localhost",
  port =3306,
  user="root",
  password="linhchi",
  db="recommend"
)

if __name__ == '__main__':
    # get_url(soup);
# Đỗ Bá Lâm : 70
# Nguyễn Bình Minh : 65
    array = [33]
    cur = mydb.cursor()
    sql = "SELECT title, id, schoolar, dblp FROM titles where teacher_id = %s"
    # sql = "SELECT title FROM title_dblps where soict_id = %s"
    # sql = "SELECT  FROM specializeds INNER JOIN soict_specializeds on soict_specializeds.specialized_id = specializeds.id where soict_specializeds.soict_id = %s"

    val = [72]
    cur.execute(sql, val)
    records = cur.fetchall()
    mydb.commit()
    for record in records:
        print(record)
