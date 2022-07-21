from flask import Flask, render_template, json, request,redirect,session,jsonify
from markupsafe import escape
from flask_mysqldb import MySQL
from logging import FileHandler,WARNING
import math
import create_node as neo4j
import numpy as np
import recommend as recommend

# function to get unique values
def unique(list1):
    x = np.array(list1)
    return (np.unique(x))
      

app = Flask(__name__)
file_handler = FileHandler('errorlog.txt')
file_handler.setLevel(WARNING)

app.config['SECRET_KEY'] = 'ILUVTOFART'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'linhchi'
app.config['MYSQL_DB'] = 'recommend'
mysql = MySQL(app)

@app.route("/", methods=["GET"])
def index():
    cur = mysql.connection.cursor() 
    cur.execute(""" SELECT *,(SELECT count(*) FROM titles WHERE
        teachers.id = titles.teacher_id) as total_pages FROM teachers ORDER BY total_pages DESC LIMIT 8""")
    users = cur.fetchall()
    return render_template('index.html', len=len(users), users = users)

@app.route("/teacher/<int:id>/", defaults={ 'page' : 1}, methods=["GET"])
@app.route("/teacher/<int:id>/page/<int:page>", methods=["GET"])
def getTeacher(id, page):
    limit = 5
    offset = page*limit - limit
    currentPage = page
    cur = mysql.connection.cursor() 
    cur.execute(""" SELECT * FROM teachers WHERE id = %s""", (id,))
    teacher = cur.fetchone()
    cur.execute(""" SELECT * FROM titles WHERE teacher_id = %s""", (id,))
    titles = cur.fetchall()
    total_page = math.ceil(len(titles) / limit)
    next = page +1
    prev = page -1
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT * FROM titles WHERE teacher_id = %s LIMIT %s OFFSET %s""", (id, limit, offset))
    titles = cur.fetchall()
    # cur.execute(""" SELECT COUNT(DISTINCT topic) as count, topic FROM titles WHERE teacher_id = %s ORDER By count DESC""", (id,))
    cur.execute(""" SELECT *, (SELECT count(*) FROM titles WHERE
        teachers.id = titles.teacher_id) as total_pages  FROM teachers LIMIT 5""")
    teachers = cur.fetchall()
    print(teachers)
    return render_template('detail.html', teacher = teacher, teachers = teachers, count = len(titles), titles = titles, page = total_page, next = next, prev = prev, current = currentPage)

@app.route("/university/<string:name>/", defaults={ 'page' : 1}, methods=["GET"])
@app.route("/university/<string:name>/page/<int:page>", methods=["GET"])
def getTeacherByUniversity(name, page):
    limit = 10
    offset = page*limit - limit
    currentPage = page
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT *,(SELECT count(*) FROM titles WHERE
        teachers.id = titles.teacher_id) as total_pages FROM teachers WHERE university = %s ORDER BY total_pages DESC""", (name, ))
    users = cur.fetchall()
    total_page = math.ceil(len(users) / limit)
    next = page +1
    prev = page -1
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT *,(SELECT count(*) FROM titles WHERE
        teachers.id = titles.teacher_id) as total_pages FROM teachers WHERE university = %s ORDER BY total_pages DESC LIMIT %s OFFSET %s""", (name, limit, offset))
    users = cur.fetchall() 
    return render_template('university.html', users = users, university = name, len=len(users), page = total_page, current = currentPage, next = next, prev = prev)


@app.route("/teacher/<int:id>/graph", methods=["GET"])
def getTeacherWithGraph(id):
    arr = []
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT * FROM teachers WHERE id = %s""", (id,))
    teacher = cur.fetchone()
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT * FROM titles WHERE teacher_id = %s""", (id,))
    titles = cur.fetchall()
    cur = mysql.connection.cursor()
    cur.execute("""SELECT DISTINCT topic FROM titles""")
    topics = cur.fetchall()
    neo4j.deleteAllNode()
    for title in titles:
        topic = "Topic0"
        name = "Wireless_Sensor_Networks"
        idTopic = 0
        if (title[7] != None):
            topic = "Topic" + str(title[7])
            name = "Wireless_Sensor_Networks"
            idTopic = title[7]
        arr.append(name)
      
        neo4j.createNode(topic, title[0], title[1], title[3], idTopic)
    arr = unique(arr)
    for array in arr:
        neo4j.createNodeMain(array, 1)   
    for topic in topics:
        tip = "Topic" + str(topic[0])
        name = "Wireless_Sensor_Networks"
        idTopic = topic[0]
        if (topic[0] == None):
            idTopic = 0
            tip = "Topic" + "0"
            name = "Wireless_Sensor_Networks"
        neo4j.createConnect(tip, name, idTopic)
    
    return render_template('graph_teacher.html', teacher = teacher, titles = titles)

@app.route("/search-key/", defaults={ 'page' : 1}, methods=['GET', 'POST'])
@app.route("/search-key/page/<int:page>", methods=['GET', "POST"])
def searchKey(page):
    limit = 10
    offset = page*limit - limit
    currentPage = page
    search = request.args.get('key')
    clusterId = recommend.search_key(request.args.get('key'))
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT * FROM titles WHERE topic = %s""", (clusterId,))
    titles = cur.fetchall()
    total_page = math.ceil(len(titles) / limit)
    next = page +1
    prev = page -1
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT * FROM titles WHERE topic = %s LIMIT %s OFFSET %s""", (clusterId, limit, offset))
    titles = cur.fetchall()
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT *,(SELECT count(*) FROM titles WHERE
        teachers.id = titles.teacher_id and titles.topic = %s) as total_pages FROM teachers ORDER BY total_pages DESC LIMIT 10""", (clusterId ))
    teachers = cur.fetchall()

    return render_template('title.html', clusterid = clusterId, titles = titles, count = len(titles), page = total_page, next = next, prev = prev, current = currentPage, search = search, teachers = teachers)

@app.route("/teacher/topic/<int:id>/", defaults={ 'page' : 1}, methods=["GET"])
@app.route("/teacher/topic/<int:id>/page/<int:page>", methods=["GET"])
def getTeacherWithCluster(id, page):
    limit = 5
    clusterId = request.args.get('clusterId')
    offset = page*limit - limit
    currentPage = page
    cur = mysql.connection.cursor() 
    cur.execute(""" SELECT * FROM teachers WHERE id = %s""", (id,))
    teacher = cur.fetchone()
    cur.execute(""" SELECT * FROM titles WHERE teacher_id = %s AND topic = %s""", (id, clusterId))
    titles = cur.fetchall()
    total_page = math.ceil(len(titles) / limit)
    next = page +1
    prev = page -1
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT * FROM titles WHERE teacher_id = %s AND topic = %s LIMIT %s OFFSET %s""", (id, clusterId, limit, offset))
    titles = cur.fetchall()
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT *,(SELECT count(*) FROM titles WHERE
        teachers.id = titles.teacher_id and titles.topic = %s) as total_pages FROM teachers ORDER BY total_pages DESC LIMIT 10""", (clusterId, ))
    teachers = cur.fetchall()

    return render_template('detail_cluster.html', teacher = teacher, teachers = teachers, count = len(titles), titles = titles, page = total_page, next = next, prev = prev, current = currentPage, clusterid = clusterId)

if __name__ == '__main__':
    app.run(port=5002)