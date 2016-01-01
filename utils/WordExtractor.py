'''
Created on 2015年12月7日
@summary: 主要处理分词相关问题
@author: suemi
'''
from enum import Enum
import jieba
import jieba.analyse
from model.Entity import *

class ExMode(Enum):
    EXACT="exact"
    CUTALL="cutall"
    TFIDF="tfidf"
    TEXTRANK="textrank"
    HMM="hmm"
    SEARCH="search"

class WordExtractor:
    def __init__(self,userDict=None,conf={}):
        self.userDict=userDict
        self.conf={}
        self.configFromDict(conf)
        if self.userDict:
            jieba.load_userdict(userDict)
        self.configDefault()
    
    def configDefault(self):
        self.conf["mode"]=ExMode.TFIDF if not "mode" in self.conf else self.conf["mode"]
        self.conf["topK"]=20 if not "topK" in self.conf else self.conf["topK"]
        self.conf["withWeight"]=False if not "withWeight" in self.conf else self.conf["withWeight"]
        self.conf["threshold"]=None if not "threshold" in self.conf else self.conf["threshold"]
        if not "allowPOS" in self.conf:
            if self.conf["mode"] == ExMode.TFIDF:
                self.conf["allowPOS"]=()
            elif self.conf["mode"]==ExMode.TEXTRANK:
                self.conf["allowPOS"]=('ns', 'n', 'vn', 'v')
           
    def config(self,key,val):
        self.conf[key]=val
        
    def configFromDict(self,conf):
        for key,val in conf.items():
            self.conf[key]=val
        
    def extractAllWords(self,sentence):
        return list(jieba.cut(sentence,cut_all=True))
    
    def extractExactWords(self,sentence):
        return list(jieba.cut(sentence,cut_all=False))
    
    def extractWordsByHMM(self,sentence):
        return list(jieba.cut(sentence,HMM=True))
    
    def extractKeyWordByTFIDF(self,sentence):
        wordList=[]
        if self.conf["threshold"]:
            threshold=self.conf["threshold"]
            tmpList=jieba.analyse.extract_tags(sentence,topK=self.conf["topK"],withWeight=True,allowPOS=self.conf["allowPOS"])
            for pair in tmpList:
                if pair[1]>=threshold:
                    wordList.append(pair[0])
        else:
            wordList=list(jieba.analyse.extract_tags(sentence,topK=self.conf["topK"],withWeight=self.conf["withWeight"],allowPOS=self.conf["allowPOS"]))
        return wordList
        
    def extractKeyWordByTextRank(self,sentence):
        wordList=[]
        if self.conf["threshold"]:
            threshold=self.conf["threshold"]
            tmpList=jieba.analyse.textrank(sentence,topK=self.conf["topK"],withWeight=True,allowPOS=self.conf["allowPOS"])
            for pair in tmpList:
                if pair[1]>=threshold:
                    wordList.append(pair[0])
        else:
            wordList=list(jieba.analyse.textrank(sentence,topK=self.conf["topK"],withWeight=self.conf["withWeight"],allowPOS=self.conf["allowPOS"]))
        return wordList
    
    def extractSearchWords(self,sentence):
        return list(jieba.cut_for_search(sentence))
    
    def extract(self,sentence):
        words=[]
        if self.conf["mode"]==ExMode.TFIDF:
            words=self.extractKeyWordByTFIDF(sentence)
        elif self.conf["mode"]==ExMode.EXACT:
            words=self.extractExactWords(sentence)
        elif self.conf["mode"]==ExMode.CUTALL:
            words=self.extractAllWords(sentence)
        elif self.conf["mode"]==ExMode.HMM:
            words=self.extractWordsByHMM(sentence)
        elif self.conf["mode"]==ExMode.SEARCH:
            words=self.extractSearchWords(sentence)
        elif self.conf["mode"]==ExMode.TEXTRANK:
            words=self.extractKeyWordByTextRank(sentence)
        return words
    
    def process(self):
        for article in Article.objects:
            try:
                words=self.extract(article.content)
                article.wordList=words
                article.save()
            except Exception as e:
                print(e.message)
                continue
            
                
    
    
    
    