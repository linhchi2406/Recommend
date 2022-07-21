import re
import string

import nltk
import numpy as np
import pandas as pd

from collections import Counter 

from gensim.models import Word2Vec

from nltk import word_tokenize
from nltk.corpus import stopwords

from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import silhouette_samples, silhouette_score

nltk.download("stopwords")
df_raw = pd.read_csv("test.csv")
def clean_text(text, tokenizer, stopwords):
    text = str(text).lower()  # Lowercase words
    text = re.sub(r"\[(.*?)\]", "", text)  # Remove [+XYZ chars] in content
    text = re.sub(r"\s+", " ", text)  # Remove multiple spaces in content
    text = re.sub(r"\w+…|…", "", text)  # Remove ellipsis (and last word)
    text = re.sub(r"(?<=\w)-(?=\w)", " ", text)  # Replace dash between words
    text = re.sub(
        f"[{re.escape(string.punctuation)}]", "", text
    )  # Remove punctuation

    tokens = tokenizer(text)  # Get tokens from text
    tokens = [t for t in tokens if not t in stopwords]  # Remove stopwords
    tokens = ["" if t.isdigit() else t for t in tokens]  # Remove digits
    tokens = [t for t in tokens if len(t) > 1]  # Remove short tokens
    return tokens
custom_stopwords = set(stopwords.words("english") + ["news", "new", "top"])
text_columns = ["title", "abstract"]


df = df_raw.copy()
df["abstract"] = df["abstract"].fillna("")

for col in text_columns:
    df[col] = df[col].astype(str)

# Create text column based on title, description, and content
df["text"] = df[text_columns].apply(lambda x: " | ".join(x), axis=1)
df["tokens"] = df["text"].map(lambda x: clean_text(x, word_tokenize, custom_stopwords))
# Remove duplicated after preprocessing
# _, idx = np.unique(df["tokens"], return_index=True)
# df = df.iloc[idx, :]

# Remove empty values
df = df.loc[df.tokens.map(lambda x: len(x) > 0), ["text", "tokens"]]

print(f"Original dataframe: {df_raw.shape}")
print(f"Pre-processed dataframe: {df.shape}")
docs = df["text"].values
tokenized_docs = df["tokens"].values
vocab = Counter()
for token in tokenized_docs:
    vocab.update(token)
def vectorize(list_of_docs, model):
    features = []

    for tokens in list_of_docs:
        zero_vector = np.zeros(model.vector_size)
        vectors = []
        for token in tokens:
            if token in model.wv:
                try:
                    vectors.append(model.wv[token])
                except KeyError:
                    continue
        if vectors:
            vectors = np.asarray(vectors)
            avg_vec = vectors.mean(axis=0)
            features.append(avg_vec)
        else:
            features.append(zero_vector)
    return features
model = Word2Vec(sentences=tokenized_docs, vector_size=40, workers=1, seed=42)
# model.wv.most_similar("trump")
vectorized_docs = vectorize(tokenized_docs, model=model)
def mbkmeans_clusters(X, k, mb=500, print_silhouette_values=False):
    km = MiniBatchKMeans(n_clusters=k, batch_size=mb).fit(X)
    if print_silhouette_values:
        sample_silhouette_values = silhouette_samples(X, km.labels_)
        silhouette_values = []
        for i in range(k):
            cluster_silhouette_values = sample_silhouette_values[km.labels_ == i]
            silhouette_values.append(
                (
                    i,
                    cluster_silhouette_values.shape[0],
                    cluster_silhouette_values.mean(),
                    cluster_silhouette_values.min(),
                    cluster_silhouette_values.max(),
                )
            )
        silhouette_values = sorted(
            silhouette_values, key=lambda tup: tup[2], reverse=True
        )
    return km, km.labels_
clustering, cluster_labels = mbkmeans_clusters(X=vectorized_docs, k=15, print_silhouette_values=True)
df_clusters = pd.DataFrame({
    "text": docs,
    "tokens": [" ".join(text) for text in tokenized_docs],
    "cluster": cluster_labels
})
df = pd.read_csv('hello.csv')
df['Cluster_ID'] = df_clusters["cluster"]
df.to_csv('hello.csv')
keywords = []
key = []
# print("Top terms per cluster (based on centroids):")
for i in range(15):
    tokens_per_cluster = ""
    most_representative = model.wv.most_similar(positive=[clustering.cluster_centers_[i]], topn=15)
    for t in most_representative:
        tokens_per_cluster += f"{t[0]} "
    keywords.append(tokens_per_cluster)
k=0
for i in df["Cluster_ID"].tolist():
    key.append(keywords[int(i)])
df['Keyword'] = key
df.to_csv('hello.csv')
     # print(f"Cluster {i}: {tokens_per_cluster}")
# test_cluster = 48
# most_representative_docs = np.argsort(
#     np.linalg.norm(vectorized_docs - clustering.cluster_centers_[test_cluster], axis=1)
# )
# print(most_representative_docs[:200])
# for d in most_representative_docs[:200]:
#     print(docs[d])
#     print("-------------")