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
        for article in Article.objects.only("wordList"):
            yield article.wordList


class CorpusProvider(object):
    def __init__(self,dictionary):
        self.dictioanry=dictionary
        self.step=0
        
    def __iter__(self):
        # for article in Article.objects.no_cache():
        #     yield self.dictionary.doc2bow(article.content)
        return self
    def __next__(self):
        article=Article.objects[self.step]
        self.step+=1
        return self.dictionary.doc2bow(article.content)

    def __len__(self):
        return  Article.objects.count()
            
class CorpusMode(Enum):
    Bow="bow"
    Mm="mm"
    Blei="lda-c"
    SVMLight="svmlight"
    Low="low"
    
class TopicMethod(Enum):
    LDA="LDA"
    LSI="LSI"

class CorpusHandler:
    
    def __init__(self,wordProvider=None,dictionary=None,corpus=None):
        self.wordProvider=wordProvider if wordProvider else WordProviderFromDB()
        self.dictionary=dictionary
        self.corpus=corpus
    
    def generateDictionary(self):
        dictionary=corpora.Dictionary(self.wordProvider)
        stop_ids=[]
        once_ids = [tokenid for tokenid, docfreq in dictionary.dfs.items() if docfreq == 1]
        dictionary.filter_tokens(stop_ids + once_ids)
        dictionary.compactify()
        self.dictionary=dictionary
        return self.dictionary

    def generateCorpus(self):
        if not self.corpus:
            self.corpus=CorpusProvider(self.dictionary)
        return self.corpus

    def generateTopic(self,method=TopicMethod.LDA,numTopics=10):
        corpus=[self.dictionary.doc2bow(article.wordList) for article in Article.objects.only("wordList")]
        if method==TopicMethod.LDA:
            instance=ldamodel.LdaModel(corpus,id2word=self.dictionary,num_topics=numTopics)
        elif method==TopicMethod.LSI:
            instance=models.LsiModel(corpus,id2word=self.dictionary,num_topics=numTopics)
        dstCorpus=instance[corpus]
        return dstCorpus
    
    def process(self,method=TopicMethod.LDA,numTopics=10):
        if not self.dictionary:
            self.generateDictionary()

        corpus=self.generateTopic(method, numTopics )
        feature=[]
        for doc in corpus:
            vector=[0]*numTopics
            for pair in doc:
                vector[pair[0]]=pair[1]
            feature.append(vector)

        #DBUtil.dumpTopic(feature,numTopics)
        CacheUtil.dumpArticleFeature(feature)
        return corpus

