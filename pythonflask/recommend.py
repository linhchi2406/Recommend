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
# import pymysql

# mydb = pymysql.connect(
#   host="localhost",
#   port =3306,
#   user="root",
#   password="linhchi",
#   db="recommend"
# )

# Reading the file
df = pd.read_csv("title.csv")

#Reading the first five records
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

def search_title(title):
    tf = TfidfVectorizer()
    tfidf_matrix = tf.fit_transform(df.cleaned_title)
    processed = re.sub("[^a-zA-Z0-9 ]", "", title.lower())
    query_vec = tf.transform([title])
    similarity = cosine_similarity(query_vec, tfidf_matrix).flatten()
    indices = np.argpartition(similarity, -5)[-5:]
    results = df.iloc[indices]
    return results.head(5).id.values.tolist()

def search_key(text):
    tf = TfidfVectorizer()
    tfidf_matrix = tf.fit_transform(df.Keyword)
    processed = re.sub("[^a-zA-Z0-9 ]", "", text.lower())
    query_vec = tf.transform([text])
    similarity = cosine_similarity(query_vec, tfidf_matrix).flatten()
    indices = np.argpartition(similarity, -5)[-5:]
    results = df.iloc[indices]
    return results.head(1).Cluster_ID.values.tolist()
