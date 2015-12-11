'''
Created on 2015年12月8日
@summary: 进一步提取用户和新闻的特征
@author: suemi
'''
from model.Entity import *
from enum import Enum
from utils.CacheUtil import CacheUtil
import numpy as np
from core.Trainer import FriendTrainer
from utils.DBUtil import DBUtil
class Provider:
    
    def __init__(self):
        self.cache=None
        self.autoUpdate=False
    
    def provideFromCache(self,eid,load=False):
        return None
    
    def provideFromDB(self,eid):
        return None
    
    def provideFromCompute(self,eid):
        return None
    
    def provideAllFromDB(self):
        return None
    
    def provideAllFromCache(self):
        return None
    
    def provideAllFromCompute(self):
        return None
      
    def provide(self,eid):
        '''
        @summary: 为单个对象提供特征向量
        '''
        res=self.provideFromCache(eid,False)
        if not res:
            res=self.provideFromDB(eid)
        if not res:
            res=self.provideFromCompute(eid)
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
        super.__init__()
        self.corpus=corpus
        
    def setCorpus(self,corpus):
        self.corpus=corpus
    
    def provideFromDB(self,articleId):
        return ArticleFeaure.loadField("topicVector")
    
    def provideFromCompute(self,eid):
        if not self.corpus:
            return None
        index=Article.loadField(eid,"index")
        res=list(map(lambda x:x[1],self.corpus[index]))
        if self.isUpdate():
            af=ArticleFeaure()
            af.eid=eid
            af.topicVector=res
            ArticleFeaure.persist(af)
        return res
    
    def provideFromCache(self,eid,load=False):
        if not self.isCached() and load:
            self.setCache(CacheUtil.loadArticleFeature())
        if not self.isCached():
            return None
        index=Article.loadField(eid,"index")
        return self.cache[index]
    
    def provideAllFromDB(self):
        feature=[]
        for item in ArticleFeaure.objects.no_cache():
            feature.append(item.topicVector)
        if len(feature)>0:
            self.setCache(feature)
            return feature
        else:
            return None
    
    def provideAllFromCache(self):
        if not self.isCached():
            self.setCache(CacheUtil.loadArticleFeature())
        return self.cache
    
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
    
    
class UserInterestProvider(Provider):
    '''
    @summary: 通过简单对用户看过的所有新闻的特征向量求均值得到用户特征以备后面使用基于用户的协同过滤
    '''
    
    def __init__(self,articleFeatureProvider=None):
        super.__init__()
        if articleFeatureProvider:
            self.articleFeatureProvider=articleFeatureProvider
        else:
            self.articleFeatureProvider=ArticleFeatureProvider()
        self.interestNum=len(self.articleFeatureProvider.provide(Article.objects[0].eid))
    def provideFromDB(self,uid):
        return UserFeature.loadField(uid,"interest")
    
    def provideFromCache(self,uid,load=False):
        if not self.isCached() and load:
            self.setCache(CacheUtil.loadUserInterest())
        if not self.isCached():
            return None
        index=User.loadField(uid,"index")
        return self.cache[index]
    
    def provideFromCompute(self,uid):
        user=User()
        user.eid=uid
        clicked=user.getAllClicked()
        vec=np.array([0.0]*self.interestNum)
        for articleId in clicked:
            vec+=np.array(self.articleFeatureProvider.provide(articleId))
        vec/=len(clicked)
        res=list(vec)
        if self.isUpdate():
            UserFeature.persist(UserFeature(eid=uid,interest=res))
        return res
    
    def provideAllFromDB(self):
        interest=[]
        for item in UserFeature.objects.no_cache():
            interest.append(item.interest)
        if len(interest)>0:
            self.setCache(interest)
            return interest
        else:
            return None
    
    def provideAllFromCompute(self):
        if not self.articleFeatureProvider:
            return None
        interest=[]
        for user in User.objects.no_cache():
            clicked=user.getAllClicked() 
            vec=np.array([0.0]*self.interestNum)
            for articleId in clicked:
                vec+=np.array(self.articleFeatureProvider.provide(articleId))
            vec/=len(clicked)
            interest.append(list(vec))
        if len(interest)>0:
            self.setCache(interest)
            if self.isUpdate():
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


class UserFriendProvider(Provider):
    '''
    @summary: 取与用户相似的用户以进行基于用户的协同过滤
    '''
    def __init__(self,trainer=None):
        super.__init__()
        self.trainer=trainer if trainer else FriendTrainer()
        
    def provideFromCache(self,uid,load=False):
        if not self.isCached() and load:
            self.setCache(CacheUtil.loadUserFriends())
        if self.isCached():
            if self.cache.has_key(uid):
                return self.cache[uid]
        return None
    
    def provideFromDB(self,uid):
        friend=[]
        for relation in FriendRelation.objects(userId=uid):
            friend.append((relation.targetId,relation.similarity))
        return friend
    
    def provideFromCompute(self,uid):
        res=self.trainer.train()
        if self.isUpdate() and res:
            DBUtil.dumpFriendsForUser(uid, res)
        return res
    
    def provideAllFromCache(self):
        if not self.isCached():
            self.setCache(CacheUtil.loadUserFriends())
        return self.cache
    
    def provideAllFromDB(self):
        friends={}
        for relation in FriendRelation.objects:
            uid=relation.userId
            if not friends.has_key(uid):
                friends[uid]=[]
            friends[uid].append((relation.targetId,relation.similarity))
        self.setCache(friends)
        return friends
    
    def provideAllFromCompute(self):
        friends=None
        if self.trainer:
            friends=self.trainer.trainAll()
            self.setCache(friends)
        if self.isUpdate() and friends:
            DBUtil.dumpFriends(friends)
        return friends
    
    def simmilarity(self,userId,targetId):
        relations=FriendRelation.objects(userId=userId,targetId=targetId).only("similarity")
        return 0 if len(relations)==0 else relations[0].similarity
            
    

class RecommendProvider(Provider):
    '''
    @summary: 提供推荐结果，供Evaluator分析使用
    '''
    def provideFromDB(self,eid):
        res=list(map(lambda x:(x.articleId,x.score),Recommendation.objects(userId=eid)))
        return res if len(res)>0 else None
    
    def provideAllFromDB(self):
        res=[]
        for user in User.objects.no_cache():
            tmp=self.provideFromDB(user.eid)
            res.append(tmp if tmp else [])
        if len(res)==0:
            res=None
        self.setCache(res) 
        return res
    
    def provideIndexMatrix(self):
        res=[]
        for user in User.objects:
            tmp=list(map(lambda x:CacheUtil.articleToIndex(x.articleId),Recommendation.objects(userId=user.eid)))
            res.append(tmp)
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
            elif featureCategory==UFCategory.FRIEND:
                return UserFriendProvider()
            elif featureCategory==UFCategory.RECOMMEND:
                return RecommendProvider()
            else:
                return Provider()
        else:
            return Provider()