'''
Created on 2015年12月9日
@summary: 根据模型预测某用户对某新闻的感兴趣程度得分
@author: suemi
'''
import time

from core.Provider import UserInterestProvider, ArticleFeatureProvider
from enum import Enum

from core.Trainer import UserFriendProvider
from model.Entity import *
from utils.CacheUtil import CacheUtil
from utils.FormatUtil import FormatUtil
from sklearn.neighbors.unsupervised import NearestNeighbors
import numpy as np

class Predictor(object):
    
    def __init__(self,ufProvider=None,afProvider=None):
        self.ufProvider=ufProvider if ufProvider else UserInterestProvider()
        self.afProvider=afProvider if afProvider else ArticleFeatureProvider()
    
    def getParam(self,userId):
        return self.ufProvider.provide(userId)
    
    def getFeature(self,articleId):
        return self.afProvider.provide(articleId)  
    
    def predict(self,userId,articleId):
        pass
    
    def predictAll(self,userId):
        pass
    
    def clear(self):
        del self.ufProvider,self.afProvider


class SimPredictor(Predictor):
    '''
    @summary: 通过用户与新闻的主题向量的余弦相似度来得出用户评分
    @addition:候选集选取使用聚类,将用户分到某一类,该类中所有的文章成为候选集
    '''
    
    def __init__(self,ufProvider=None,afProvider=None):
        super().__init__()
        self.model=None
        self.maxNum=10
        self.default=None


    def coldStart(self):
        tmp=[]
        for i in range(Article.objects.count()):
            tmp.append((i,len(CacheUtil.loadClickedForArticle(i))))
        tmp.sort(key=lambda x:x[1],reverse=True)
        total=sum(list(map(lambda x:x[1],tmp[0:self.maxNum])))
        self.default=list(map(lambda x:(x[0],x[1]/total),tmp[0:self.maxNum]))
        return self.default

    def config(self,maxNum=None,ufProvider=None,afProvider=None):
        self.ufProvider=ufProvider if ufProvider else self.ufProvider
        self.afProvider=afProvider if afProvider else self.afProvider
        self.maxNum=maxNum if maxNum else self.maxNum
    
    def predict(self, userId, articleId):
        af=np.array(self.getFeature(articleId))
        uf=np.array(self.getParam(userId))
        if sum(uf)==0:
            if not self.default:
                self.coldStart()
            for pair in self.default:
                if pair[0]==articleId:
                    return pair[1]
            return 0
        return np.dot(af,uf)/(np.sqrt(np.dot(uf,uf))*np.sqrt(np.dot(af,af)))
    
    def predictAll(self, userIndex):
        if not self.default:
            self.coldStart()
        uf=self.getParam(userIndex)
        if sum(uf)==0:
            return self.default
        # data,transfer=self.afProvider.filterClicked()
        if not self.model:
            self.model=NearestNeighbors(n_neighbors=self.maxNum,algorithm='auto').fit(self.afProvider.provideAll())
        distance,candidates=self.model.kneighbors([uf])
        res=[]
        for i in range(self.maxNum):
            res.append((candidates[0][i],1-distance[0][i]))
        return res
    
    def clear(self):
        del self.model


class FriendPredictor(Predictor):
    '''
    @summary: 根据基于用户的协同过滤来计算用户对新闻的感兴趣程度
    @addition: 候选集是用户领域中的所有用户看过的文章和用户看过的文章的领域的并集的并集
    '''
    
    def __init__(self,provider=None):
        super().__init__()
        self.ufProvider=provider if provider else UserFriendProvider()
        self.ufProvider.provideAll()
        self.default=None
        self.maxNum=10

    def coldStart(self):
        tmp=[]
        for i in range(Article.objects.count()):
            tmp.append((i,len(CacheUtil.loadClickedForArticle(i))))
        tmp.sort(key=lambda x:x[1],reverse=True)
        total=sum(list(map(lambda x:x[1],tmp[0:self.maxNum])))
        self.default=list(map(lambda x:(x[0],x[1]/total),tmp[0:self.maxNum]))
        return self.default
    
    def config(self,provider):
        self.ufProvider=provider if provider else self.ufProvider
    
    def predict(self,userId,articleId):
        friends=self.ufProvider.provide(userId)
        if len(friends)==0:
            if not self.default:
                self.coldStart()
            for pair in self.default:
                if pair[0]==articleId:
                    return pair[1]
            return 0
        userList=Record.getUserForArticle(articleId)
        score=0
        for uid in userList:
            score+=self.ufProvider.similarity(userId,uid)
        return score
        
    def predictAll(self, userIndex):
        friends=self.ufProvider.provide(userIndex)
        if not self.default:
            self.coldStart()
        if len(friends)==0:
            return self.default
        score={}
        for pair in friends:
            for aid in CacheUtil.loadClickedForUser(pair[0]):
                if not aid in score:
                    score[aid]=0
                score[aid]+=pair[1]
        return FormatUtil.dict2tuple(score)

class PredictorCategory(Enum):
    SIM="sim"
    FRIEND="friend"

class PredictorFactory(object):
    
    @staticmethod
    def getPredictor(category):
        if category==PredictorCategory.SIM:
            return SimPredictor()
        elif category==PredictorCategory.FRIEND:
            return FriendPredictor()
        
        
    
            