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
        '''
        @summary: 为单个对象提供特征向量
        '''
        pass
    
    def provideAll(self):
        '''
        @summary: 以矩阵的形式为所有对象提供特征向量
        '''
        pass
    
    def clear(self):
        '''
        @summary: 清空对象占有的缓存
        '''
        pass
    
class ArticleFeatureProvider(FeatureProvider):
    '''
    @summary: 提供由新闻主题生成的特征
    '''
    
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
        res=self.provideFromDB(eid)
        if not res:
            res=self.provideFromCache(eid)
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
    
    def clear(self):
        del self.feature
            
    
class UserInterestProvider(FeatureProvider):
    '''
    @summary: 通过简单对用户看过的所有新闻的特征向量求均值得到用户特征以备后面使用基于用户的协同过滤
    '''
    
    def __init__(self,articleFeatureProvider=None):
        if articleFeatureProvider:
            self.articleFeatureProvider=articleFeatureProvider
        else:
            self.articleFeatureProvider=ArticleFeatureProvider()
        self.interestNum=len(self.articleFeatureProvider.provide(Article.objects[0].eid))
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
        clicked=user.getAllClicked()
        vec=np.array([0.0]*self.interestNum)
        for articleId in clicked:
            vec+=np.array(self.articleFeatureProvider.provide(articleId))
        vec/=len(clicked)
        return list(vec)
    
    def provideAllFromDB(self):
        interest=[]
        for item in UserFeature.objects.no_cache():
            interest.append(item.interest)
        if len(interest)>0:
            self.interest=interest
            return interest
        else:
            return None
    
    def provideAllByAvgTopic(self):
        interest=[]
        for user in User.objects.no_cache():
            clicked=user.getAllClicked() 
            vec=np.array([0.0]*self.interestNum)
            for articleId in clicked:
                vec+=np.array(self.articleFeatureProvider.provide(articleId))
            vec/=len(clicked)
            interest.append(list(vec))
        if len(interest)>0:
            self.interest=interest
            return interest
        else:
            return None
    
    def provideAllFromCache(self):
        if not self.interest:
            self.interest=CacheUtil.loadUserInterest()
        return self.interest
    
    def provide(self,uid):
        res=self.provideFromDB(uid)
        if not res:
            res=self.provideFromCache(uid)
        if not res and self.articleFeatureProvider:
            res=self.provideByAvgTopic(uid)
        return res
    
    def provideAll(self):
        if self.interest:
            return self.interest
        interest=self.provideAllFromCache()
        if not interest and self.articleFeatureProvider:
            interest=self.provideAllByAvgTopic()
            if interest:
                CacheUtil.dumpUserInterest(interest)
        self.interest=interest
        return interest
    
    def clear(self):
        del self.interest
    
class UserParamProvider(FeatureProvider):
    '''
    @summary: 使用某种模型对每一个用户进行训练，将参数记录作为用户特征，以备后续预测器使用
    '''


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
        if destCategory==Category.ARTICLE:
            if featureCategory==AFCategory.TOPIC:
                return ArticleFeatureProvider()
        elif destCategory==Category.USER:
            if featureCategory==UFCategory.INTEREST:
                return UserInterestProvider()
            elif featureCategory==UFCategory.PARAM:
                return UserParamProvider()
            else:
                return None
        else:
            return None