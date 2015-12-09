'''
Created on 2015年12月5日

@author: suemi
@summary: 进行词义分析的工具类
'''
from model.Entity import *
from gensim import corpora, models
from enum import Enum
from gensim.models import ldamodel
from utils.CacheUtil import CacheUtil
from utils.DBUtil import DBUtil
class WordProviderFromDB(object):
    def __iter__(self):
        for wordBag in WordBag.objects.no_cache():
            yield wordBag.wordList

class CorpusProvider(object):
    def __init__(self,dictionary):
        self.dictioanry=dictionary
        
    def __iter__(self):
        for article in Article.objects.no_cache():
            yield self.dictionary.doc2bow(article.content)
            
class CorpusMode(Enum):
    Bow="bow"
    Mm="mm"
    Blei="lda-c"
    SVMLight="svmlight"
    Low="low"
    
class TopicMethod(Enum):
    LDA="LDA"

class CorpusHandler:
    
    def __init__(self,wordProvider=None,dictionary=None,corpus=None):
        self.wordProvider=wordProvider if wordProvider else WordProviderFromDB()
        self.dictionary=dictionary
        self.corpus=corpus
    
    def generateDictionary(self):
        dictionary=corpora.Dictionary(self.wordProvider)
  #      stop_ids = [dictionary.token2id[stopword] for stopword in stoplist  if stopword in dictionary.token2id]  
        stop_ids=[]
        once_ids = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq == 1]
        dictionary.filter_tokens(stop_ids + once_ids)
        dictionary.compactify()
        self.dictionary=dictionary
        return self.dictionary

    def generateCorpus(self):
        if not self.corpus:
            self.corpus=CorpusProvider(self.dictionary)
        return self.corpus

    def generateTopic(self,method=TopicMethod.LDA,numTopics=20):
        if method==TopicMethod.LDA:
            model=ldamodel.LdaModel(self.corpus,id2word=self.dictionary,num_topics=numTopics)
            dstCorpus=model[self.corpus]
        return dstCorpus
    
    def process(self,method=TopicMethod.LDA,numTopics=20):
        if not self.dictionary:
            self.generateDictionary()
        if not self.corpus:
            self.generateCorpus()
        corpus=self.generateTopic(method, numTopics)
        DBUtil.dumpTopic(corpus)