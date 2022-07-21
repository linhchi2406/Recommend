import pymysql
import pandas as pd
import csv
mydb = pymysql.connect(
  host="localhost",
  port =3306,
  user="root",
  password="linhchi",
  db="recommend"
)
header = ['id', 'Title', 'Abstract', 'Teacher Id', 'Link', 'Dblp', 'Schoolar']
index = ['ONE', 'TWO', 'THREE', 'FOUR', 'FIVE', 'SIX', 'SEVEN']

# with open('./teacher.csv', 'w') as f:
#     writer = csv.writer(f)
#     writer.writerow(header)
mycursor = mydb.cursor()
mycursor.execute("SELECT id, title, abstract, teacher_id, link, dblp, schoolar FROM titles")
myresult = mycursor.fetchall()
index = 0
with open('teachers.csv', 'w',  encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for row in myresult:
        index = index + 1
        array = [row[0], row[1], row[2], row[3], row[4], row[5], row[6]]
        writer.writerow(array)
        print(array)