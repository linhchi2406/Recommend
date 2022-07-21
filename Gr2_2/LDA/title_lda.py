import re
import importlib
import numpy as np
import pandas as pd
import csv
from pprint import pprint
import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import CoherenceModel
import spacy
import pyLDAvis
import pyLDAvis.gensim_models as gensimvis
import matplotlib.pyplot as plt
from operator import itemgetter, attrgetter  
from nltk.corpus import stopwords

array = []
df = pd.read_csv('test.csv')
df["period"] = df["title"] + df["abstract"]
array = df.period.values.tolist()
stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use'])
data = array
data = [re.sub('\S*@\S*\s?', '', sent) for sent in data]
data = [re.sub('\s+', ' ', sent) for sent in data]
data = [re.sub("\'", "", sent) for sent in data]
bigram = gensim.models.Phrases(data, min_count=5, threshold=100)
trigram = gensim.models.Phrases(bigram[data], threshold=100)
bigram_mod = gensim.models.phrases.Phraser(bigram)
trigram_mod = gensim.models.phrases.Phraser(trigram)
def remove_stopwords(texts):
       return [[word for word in simple_preprocess(str(doc)) 
   if word not in stop_words] for doc in texts]
def make_bigrams(texts):
   return [bigram_mod[doc] for doc in texts]
def make_trigrams(texts):
   [trigram_mod[bigram_mod[doc]] for doc in texts]
def lemmatization(texts, allowed_postags=['NOUN']):
   texts_out = []
   for sent in texts:
      doc = nlp(" ".join(sent))
      texts_out.append([token.lemma_ for token in doc if token.pos_ in allowed_postags])
   return texts_out
data_words_nostops = remove_stopwords(data)
data_words_bigrams = make_bigrams(data_words_nostops)
nlp = spacy.load('en_core_web_md')
# nlp = spacy.load('en', disable=['parser', 'ner'])
data_lemmatized = lemmatization(data_words_bigrams, allowed_postags=[
   'NOUN', 'ADJ', 'VERB'
])
id2word = corpora.Dictionary(data_lemmatized)
texts = data_lemmatized
corpus = [id2word.doc2bow(text) for text in texts]
[[(id2word[id], freq) for id, freq in cp] for cp in corpus[:4]] 
#it will print the words with their frequencies.
lda_model = gensim.models.ldamodel.LdaModel(
   corpus=corpus, id2word=id2word, num_topics= 30, random_state=100, 
   update_every=1, chunksize=100, passes=10, alpha='auto', per_word_topics=True
)
doc_lda = lda_model[corpus]
visualisation = gensimvis.prepare(lda_model, corpus, id2word, mds='mmds')   
pyLDAvis.save_html(visualisation, 'LDA_Visualization.html')
print('\nPerplexity: ', lda_model.log_perplexity(corpus))
def format_topics_sentences(ldamodel, corpus, texts):
    sent_topics_df = pd.DataFrame(pd.np.empty((0, 3)))
    sent_topics_df.columns = ['Dominant_Topic', 'Perc_Contribution', 'Topic_Keywords']

    # Get main topic in each sentence
    for i, row in enumerate(ldamodel[corpus]):
        row = sorted(row[0], key=lambda x: (x[1]), reverse=True)
        # Get the Dominant topic, and Perc Contribution for each sentence
        for j, (topic_num, prop_topic) in enumerate(row):
            if j == 0:
                wp = ldamodel.show_topic(topic_num)
                topic_keywords = ", ".join([word for word, prop in wp])
                data = [int(topic_num), round(prop_topic,4), topic_keywords]
                sent_topics_df.loc[len( sent_topics_df.index)]=list(data)
                # sent_topics_df.append( pd.Series([int(topic_num), round(prop_topic,4), topic_keywords]),ignore_index=True,sort=False)
                # sent_topics_df = pd.concat([sent_topics_df, pd.Series([int(topic_num), round(prop_topic,4), topic_keywords])], axis = 1)
            else:
                break

    # Add original text to the end of the output
    # sent_topics_df.columns = ['Dominant_Topic', 'Perc_Contribution', 'Topic_Keywords']
    # contents = pd.Series(texts)
    # sent_topics_df = pd.concat([sent_topics_df, contents], axis=1)
    return(sent_topics_df)


df_topic_sents_keywords = format_topics_sentences(ldamodel=lda_model, corpus=corpus, texts=data)
df_topic_sents_keywords['Title'] = df.title.values.tolist()
df_topic_sents_keywords['ID'] = df.id.values.tolist()
df_topic_sents_keywords['Teacher_id'] = df.teacher_id.values.tolist()


df_topic_sents_keywords.to_csv('lda_test.csv')


