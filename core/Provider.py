'''
Created on 2015年12月8日
@summary: 进一步提取用户和新闻的特征
@author: suemi
'''
from email._header_value_parser import Word

from model.Entity import *
from enum import Enum
from utils.CacheUtil import CacheUtil
import numpy as np
from utils.DBUtil import DBUtil
class Provider:
    
    def __init__(self):
        self.cache=None
        self.autoUpdate=False
    
    def provideFromCache(self,index,load=False):
        return None
    
    def provideFromDB(self,index):
        return None
    
    def provideFromCompute(self,index):
        return None
    
    def provideAllFromDB(self):
        return None
    
    def provideAllFromCache(self):
        return None
    
    def provideAllFromCompute(self):
        return None
      
    def provide(self,index):
        '''
        @summary: 为单个对象提供特征向量
        '''
        res=self.provideFromCache(index,True)
        if res==None:
            res=self.provideFromDB(index)
        if res==None:
            res=self.provideFromCompute(index)
        return res
    
    def provideAll(self):
        '''
        @summary: 以矩阵的形式为所有对象提供特征向量
        '''
        if self.isCached():
            return self.cache
        res=self.provideAllFromCache()
        if not res:
            res=self.provideAllFromDB()
        if not res:
            res=self.provideAllFromCompute()
        self.setCache(res)
        return res
    
    def clear(self):
        '''
        @summary: 清空对象占有的缓存
        '''
        del self.cache
    
    def setCache(self,data):
        '''
        @summary: 设置对象的特征缓存
        '''
        self.cache=data
    
    def isCached(self):
        return True if self.cache else False
    
    def onUpdate(self):
        '''
        @summary: 打开自动更新，当通过计算得出结果时，会自动更新数据库中的相关记录
        '''
        self.autoUpdate=True
        
    def offUpdate(self):
        self.autoUpdate=False
    
    def isUpdate(self):
        return self.autoUpdate
    
class ArticleFeatureProvider(Provider):
    '''
    @summary: 提供由新闻主题生成的特征
    '''
    
    def __init__(self,corpus=None):
        super().__init__()
        self.corpus=corpus
        self.unClicked=None
        self.transfer=None
        
    def setCorpus(self,corpus):
        self.corpus=corpus
    
    def provideFromDB(self,articleIndex):
        return Article.loadField(articleIndex,"topicVector")
    
    def provideFromCompute(self,index):
        if not self.corpus:
            return None

        res=list(map(lambda x:x[1],self.corpus[index]))
        if self.isUpdate():
            article=Article.objects[index]
            article.topicVector=res
            article.save()
        return res

    def provideFromCache(self,index,load=False):
        if not self.isCached() and load:
            self.setCache(CacheUtil.loadArticleFeature())
        if not self.isCached():
            return None
        index=Article.loadField(index,"index")
        return self.cache[index]
    
    def provideAllFromDB(self):
        feature=list(map(lambda x:x.topicVector,Article.objects.only("topicVector")))
        if len(feature)>0:
            self.setCache(feature)
            return feature
        else:
            return None
    
    def provideAllFromCache(self):
        if not self.isCached():
            self.setCache(CacheUtil.loadArticleFeature())
        if len(self.cache)>0:
            return self.cache
        else:
            self.cache=None
            return None
    
    def provideAllFromCompute(self):
        feature=[]
        for doc in self.corpus:
            feature.append(list(map(lambda x:x[1],doc)))
        if len(feature)==0:
            feature=None
        elif self.isUpdate():
            DBUtil.dumpArticleFeature(feature)
        self.setCache(feature)
        return feature

    def filterClicked(self):
        if self.unClicked:
            return self.unClicked,self.transfer
        feature=self.provideAll()
        unClicked=[];transfer=[];count=0
        for i in range(len(feature)):
            if len(CacheUtil.loadClickedForArticle(i))==0:
                transfer.append(i)
                unClicked.append(feature[i])
        self.unClicked=unClicked
        self.transfer=transfer
        return unClicked,transfer
    
    
class UserInterestProvider(Provider):
    '''
    @summary: 通过简单对用户看过的所有新闻的特征向量求均值得到用户特征以备后面使用基于用户的协同过滤
    '''
    
    def __init__(self,articleFeatureProvider=None):
        super().__init__()
        if articleFeatureProvider:
            self.articleFeatureProvider=articleFeatureProvider
        else:
            self.articleFeatureProvider=ArticleFeatureProvider()
        self.interestNum=len(self.articleFeatureProvider.provide(0))
    def provideFromDB(self,index):
        return User.loadField(index,"interest")
    
    def provideFromCache(self,uid,load=False):
        if not self.isCached() and load:
            self.setCache(CacheUtil.loadUserInterest())
        if not self.isCached():
            return None
        index=User.loadField(uid,"index")
        return self.cache[index]
    
    def provideFromCompute(self,index):
        user=User.objects[index]
        clicked=user.getAllClicked()
        vec=np.array([0.0]*self.interestNum)
        for articleIndex in clicked:
            vec+=np.array(self.articleFeatureProvider.provide(articleIndex))
        vec/=max(len(clicked),1)
        res=list(vec)
        if self.isUpdate():
            user.interest=res
            user.save()
        return res
    
    def provideAllFromDB(self):
        interest=list(map(lambda x:x.interest,User.objects.only("interest")))
        if len(interest)>0:
            self.setCache(interest)
            return interest
        else:
            return None
    
    def provideAllFromCompute(self):
        if not self.articleFeatureProvider:
            return None
        interest=[]
        feature=self.articleFeatureProvider.provideAll()
        for user in User.objects:
            clicked=user.getAllClicked()
            vec=np.array([0.0]*self.interestNum)
            for i in clicked:
                tmp=np.array(feature[i])
                vec=vec+tmp
            vec/=max(len(clicked),1)
            interest.append(list(vec))
            # print(vec)
            print("User "+str(user.index)+" has computed!")
        if len(interest)>0:
            self.setCache(interest)
            if self.isUpdate():
                CacheUtil.dumpUserInterest(interest)
                DBUtil.dumpInterest(interest)
            return interest
        else:
            return None
    
    def provideAllFromCache(self):
        if not self.isCached():
            self.setCache(CacheUtil.loadUserInterest())
        return self.cache
    
    
    
    
class UserParamProvider(Provider):
    '''
    @summary: 使用某种模型对每一个用户进行训练，将参数记录作为用户特征，以备后续预测器使用
    '''
    pass



    

class RecommendProvider(Provider):
    '''
    @summary: 提供推荐结果，供Evaluator分析使用
    '''
    def provideFromDB(self,index):
        res=list(map(lambda x:(x.articleIndex,x.score),Recommendation.objects[index]))
        return res
    
    def provideAllFromDB(self):
        res=[]
        for user in User.objects:
            tmp=self.provideFromDB(user.index)
            res.append(tmp if tmp else [])
        self.setCache(res) 
        return res

  
class AFCategory(Enum):
    TOPIC="topic"

class UFCategory(Enum):
    INTEREST="interest"
    PARAM="param"
    FRIEND="friend"
    RECOMMEND="recommend"
    
class Category(Enum):
    USER="user"
    ARTICLE="article"
    RECORD="record"

class ProviderFactory:
    '''
    @summary: 工厂模式，通过选项返回合适的Provider
    '''
    
    @staticmethod
    def getProvider(featureCategory,destCategory=Category.USER):
        if destCategory==Category.ARTICLE:
            if featureCategory==AFCategory.TOPIC:
                return ArticleFeatureProvider()
        elif destCategory==Category.USER:
            if featureCategory==UFCategory.INTEREST:
                return UserInterestProvider()
            elif featureCategory==UFCategory.PARAM:
                return UserParamProvider()
            elif featureCategory==UFCategory.RECOMMEND:
                return RecommendProvider()
            else:
                return Provider()
        else:
            return Provider()