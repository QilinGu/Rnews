'''
Created on 2015年12月5日
@summary: 对算法运行中的一些中间文件进行管理
@author: suemi
'''
from utils.CorpusHandler import CorpusMode, TopicMethod
from gensim import corpora
import pickle as pk
import os
from model.Entity import *
class CacheUtil:
    path={}
    path["data"]="/Volumes/MAC/Rnews/data/"
    path["dictionary"]=CacheUtil.path["data"]+"rnews.dict"
    path["corpus"]=CacheUtil.path["data"]+"corpus.mm"
    path["topic"]=CacheUtil.path["data"]+"topic.mm"
    path["articleFeature"]=CacheUtil.path["data"]+"articleFeature.pk"
    path["userInterest"]=CacheUtil.path["data"]+"userInterest.pk"
    path["userFriends"]=CacheUtil.path["data"]+"userFriends.pk"
    UserToClicked=None
    ArticleToClicked=None
    userToIndex=None
    indexToUser=None
    
    @staticmethod
    def clear():
        pass
    
    @staticmethod
    def loadDictionary():
        return corpora.dictionary.Dictionary.load(CacheUtil.path["dictionary"])
    
    @staticmethod
    def loadCorpus(mode=CorpusMode.Mm):
        corpus=None
        CacheUtil.path["corpus"]=CacheUtil.path["data"]+"corpus."+mode
        if mode==CorpusMode.Mm:
            corpus=corpora.MmCorpus(CacheUtil.path["corpus"])
        elif mode==CorpusMode.Blei:
            corpus=corpora.BleiCorpus(CacheUtil.path["corpus"])
        elif mode==CorpusMode.Low:
            corpus=corpora.LowCorpus(CacheUtil.path["corpus"])
        elif mode==CorpusMode.SVMLight:
            corpus=corpora.SvmLightCorpus(CacheUtil.path["corpus"])
        return corpus
    
    @staticmethod
    def dumpDictionary(dictionary):
        dictionary.save(CacheUtil.dictionaryPath)
    
    @staticmethod
    def dumpCorpus(corpus,mode=CorpusMode.Mm):
        CacheUtil.path["corpus"]=CacheUtil.path["data"]+"corpus."+mode
        if mode==CorpusMode.Mm:
            corpora.MmCorpus.serialize(CacheUtil.path["corpus"],corpus)
        elif mode==CorpusMode.Blei:
           corpora.BleiCorpus.serialize(CacheUtil.path["corpus"],corpus)
        elif mode==CorpusMode.Low:
           corpora.LowCorpus.serialize(CacheUtil.path["corpus"],corpus)
        elif mode==CorpusMode.SVMLight:
            corpora.SvmLightCorpus.serialize(CacheUtil.path["corpus"],corpus)
        
    
    @staticmethod
    def dumpTopic(corpus,method=TopicMethod.LDA):
        CacheUtil.path["topic"]=CacheUtil.path["data"]+method+".mm"
        corpora.MmCorpus.serialize(CacheUtil.path["topic"],corpus)
        
    @staticmethod
    def loadTopic(method=TopicMethod.LDA):
        CacheUtil.path["topic"]=CacheUtil.path["data"]+method+".mm"
        return corpora.MmCorpus(CacheUtil.path["topic"])
    
    @staticmethod
    def dumpArticleFeature(feature):
        pk.dump(feature,open(CacheUtil.path["articleFeature"],'w'))
        
    @staticmethod
    def loadArticleFeature():
        if not os.path.exists(CacheUtil.path["articleFeature"]):
            return None
        pk.load(open(CacheUtil.path["articleFeature"],'r'))
        
    @staticmethod
    def dumpUserInterest(interest):
        pk.dump(interest,open(CacheUtil.path["userInterest"],'w'))
        
    @staticmethod
    def loadUserInterest():
        if not os.path.exists(CacheUtil.path["userInterest"]):
            return None
        pk.load(open(CacheUtil.path["userInterest"],'r'))
    
    @staticmethod
    def dumpUserFriends(friends):
        pk.dump(friends,open(CacheUtil.path["userFriends"],'w'))
        
    @staticmethod
    def loadUserFriends():
        if not os.path.exists(CacheUtil.path["userFriends"]):
            return None
        pk.load(open(CacheUtil.path["userFriends"],'r'))
       
    @staticmethod
    def getUserToClicked():
        pass
    
    @staticmethod
    def getArticleToClicked():
        pass
    
    @staticmethod
    def getIndexForUser(uid):
        if not CacheUtil.userToIndex:
            tmp={}
            for user in User.objects.no_cache():
                tmp[user.eid]=user.index
            CacheUtil.userToIndex=tmp
        return CacheUtil.userToIndex[uid]
    
    @staticmethod
    def getUidForIndex(index):
        if not CacheUtil.indexToUser:
            CacheUtil.indexToUser=list(map(lambda x:x.eid,User.objects))
        return CacheUtil.indexToUser[index]