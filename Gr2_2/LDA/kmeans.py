import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
data = pd.read_csv('test.csv')
keywords = []
# data = pd.read_json('../input/combined.json', lines=True)
tfidf = TfidfVectorizer(
    min_df = 5,
    max_df = 0.95,
    max_features = 8000,
    stop_words = 'english'
)
tfidf.fit(data.title + data.abstract)
text = tfidf.transform(data.title + data.abstract)
def find_optimal_clusters(data, max_k):
    iters = range(2, max_k+1, 2)
    sse = []
    for k in iters:
        sse.append(MiniBatchKMeans(n_clusters=k, init_size=1024, batch_size=2048, random_state=20).fit(data).inertia_)
        # print('Fit {} clusters'.format(k))
    f, ax = plt.subplots(1, 1)
    ax.plot(iters, sse, marker='o')
    ax.set_xlabel('Cluster Centers')
    ax.set_xticks(iters)
    ax.set_xticklabels(iters)
    ax.set_ylabel('SSE')
    ax.set_title('SSE by Cluster Center Plot')
    
find_optimal_clusters(text, 30)
clusters = MiniBatchKMeans(n_clusters=30, init_size=1024, batch_size=2048, random_state=20).fit_predict(text)
def get_top_keywords(data, clusters, labels, n_terms):
    arr = []
    df = pd.DataFrame(data.todense()).groupby(clusters).mean()
    
    for i,r in df.iterrows():
        print('\nCluster {}'.format(i))
        print(','.join([labels[t] for t in np.argsort(r)[-n_terms:]]))
        text = ','.join([labels[t] for t in np.argsort(r)[-n_terms:]])
        arr.append(text)
    return arr

df = pd.read_csv('chi.csv')
df['Cluster_ID'] = clusters
df.to_csv('chi.csv')
test = get_top_keywords(text, clusters, tfidf.get_feature_names(), 30)
for i in df.Cluster_ID.values.tolist():
    keywords.append(test[i])
df['Keyword'] = keywords
df.to_csv('chi.csv')
# get_top_keywords(text, clusters, tfidf.get_feature_names(), 20)