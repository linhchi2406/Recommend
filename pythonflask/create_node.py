
from py2neo import Graph, Node, Relationship
urldb = "bolt://localhost:11005"
graph = Graph(urldb,auth=("neo4j", "linhchi"))

def createNode(topic, id, title=None, link=None, idTopic= None):
    BN = Node(topic, id=id, title=title, link=link, idTopic = idTopic)
    try:
        graph.begin()
        graph.create(BN)
        graph.commit()
    except Exception as e:
        print(e)

def createConnect(topic1, topic2, role):
    command = """
    MATCH (a:%s), (b:%s)
    merge (a)-[r:role {roles: %s}]->(b)
    return a,b""" %(topic1, topic2, role)
    try:
        graph.run(command)
    except Exception as e:
        print(e)

def deleteAllNode():
    command = """
    MATCH (n)
    DETACH DELETE n """
    try:
        graph.run(command)
    except Exception as e:
        print(e)

def createNodeMain(name, id):
    BN = Node(name, id=id)
    try:
        graph.begin()
        graph.create(BN)
        graph.commit()
    except Exception as e:
        print(e)

