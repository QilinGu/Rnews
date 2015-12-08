'''
Created on 2015年12月8日
@summary: 进一步提取用户和新闻的特征
@author: suemi
'''
from model.Entity import *
from enum import Enum
from utils.CacheUtil import CacheUtil
import numpy as np
class FeatureProvider:
    
    def __init__(self):
        pass
        
    def provide(self,eid):
        pass
    
    def provideAll(self):
        pass
    
class ArticleFeatureProvider(FeatureProvider):
    
    def __init__(self,corpus=None):
        self.corpus=corpus
        
    def setCorpus(self,corpus):
        self.corpus=corpus
    
    def provideFromDB(self,articleId):
        return ArticleFeaure.loadField("topicVector")
    
    def provideFromCorpus(self,eid):
        index=Article.loadField(eid,"index")
        return list(map(lambda x:x[1],self.corpus[index]))
    
    def provideFromCache(self,eid):
        if not self.feature:
            self.feature=CacheUtil.loadArticleFeature()
        if not self.feature:
            return None
        index=Article.loadField(eid,"index")
        return self.feature[index]
    
    def provideAllFromDB(self):
        feature=[]
        for item in ArticleFeaure.objects.no_cache():
            feature.append(item.topicVector)
        if len(feature)>0:
            self.feature=feature
            return feature
        else:
            return None
    
    def provideAllFromCache(self):
        if not self.feature:
            self.feature=CacheUtil.loadArticleFeature()
        return self.feature
    
    def provideAllFromCorpus(self):
        feature=[]
        for doc in self.corpus:
            feature.append(list(map(lambda x:x[1],doc)))
        self.feature=feature
        return feature
    
    def provide(self,eid):
        res=self.provideFromCache(eid)
        if not res:
            res=self.provideFromDB(eid)
        if not res and self.corpus:
            res=self.provideFromCorpus(eid)
        return res
    
    def provideAll(self):
        if self.feature:
            return self.feature
        feature=self.provideAllFromCache()
        if not feature and self.corpus:
            feature=self.provideAllFromCorpus()
            if feature:
                CacheUtil.dumpArticleFeature(feature)
        self.feature=feature
        return feature
            
    
class UserInterestProvider(FeatureProvider):
    
    def provideFromDB(self,uid):
        return UserFeature.loadField(uid,"interest")
    
    def provideFromCache(self,uid):
        if not self.interest:
            self.interest=CacheUtil.loadUserInterest()
        if not self.interest:
            return None
        index=User.loadField(uid,"index")
        return self.interest[index]
    
    def provideByAvgTopic(self,uid):
        user=User()
        user.eid=uid
        clicked=user.getAllClickedFromDB()
    
    def provideAllFromDB(self):
        pass
    
    def provideAllByAvgTopic(self):
        pass
    
    def provideAllFromCache(self):
        pass
    
    def provide(self,uid):
        pass
    
    def provideAll(self):
        pass
    
class UserParamProvider(FeatureProvider):
    pass


class AFCategory(Enum):
    TOPIC="topic"

class UFCategory(Enum):
    INTEREST="interest"
    PARAM="param"
    
class Category(Enum):
    USER="user"
    ARTICLE="article"
    RECORD="record"

class ProviderFactory:
    '''
    @summary: 工厂模式，通过选项返回合适的FeatureProvider
    '''
    
    @staticmethod
    def getProvider(destCategory,featureCategory):
        pass