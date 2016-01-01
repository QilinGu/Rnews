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
    '''
    
    def __init__(self,ufProvider=None,afProvider=None):
        super().__init__()
        self.model=None
        self.maxNum=10
    
    def config(self,maxNum=None,ufProvider=None,afProvider=None):
        self.ufProvider=ufProvider if ufProvider else self.ufProvider
        self.afProvider=afProvider if afProvider else self.afProvider
        self.maxNum=maxNum if maxNum else self.maxNum
    
    def predict(self, userId, articleId):
        af=np.array(self.getFeature(articleId))
        uf=np.array(self.getParam(userId))
        return np.dot(af,uf)/(np.sqrt(np.dot(uf,uf))*np.sqrt(np.dot(af,af)))
    
    def predictAll(self, userIndex):
        if not self.model:
            self.model=NearestNeighbors(n_neighbors=self.maxNum,algorithm='auto').fit(self.afProvider.provideAll())
        distance,candidates=self.model.kneighbors([self.getParam(userIndex)])
        res=[]
        for i in range(self.maxNum):
            res.append((candidates[0][i],1-distance[0][i]))
        return res
    
    def clear(self):
        del self.model


class FriendPredictor(Predictor):
    '''
    @summary: 根据基于用户的协同过滤来计算用户对新闻的感兴趣程度
    '''
    
    def __init__(self,provider=None):
        super().__init__()
        self.ufProvider=provider if provider else UserFriendProvider()
        self.ufProvider.provideAll()
    
    def config(self,provider):
        self.ufProvider=provider if provider else self.ufProvider
    
    def predict(self,userId,articleId):
        userList=Record.getUserForArticle(articleId)
        score=0
        for uid in userList:
            score+=self.ufProvider.similarity(userId,uid)
        return score
        
    def predictAll(self, userIndex):

        score={}
        for pair in self.ufProvider.provide(userIndex):
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
        
        
    
            