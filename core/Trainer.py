'''
Created on 2015年12月9日
@summary: 将用户是否点击某个新闻看成是一个分类或回归问题，对每个用户训练和预测他对某个新闻的得分，最简单的例子是用户特征与新闻特征直接计算余弦相似度
@author: suemi
'''
from core.Provider import UserInterestProvider, ProviderFactory, Provider
from sklearn.neighbors.unsupervised import NearestNeighbors

from model.Entity import FriendRelation, User
from utils.CacheUtil import CacheUtil
from utils.DBUtil import DBUtil
from enum import Enum
class Trainer(object):

    def __init__(self, num,provider=None):
        self.autoUpdate=False
        self.num=num
        self.provider=provider
    
    def train(self,userId):
        pass

    def trainAll(self):
        pass
    
    def clear(self):
        pass
    
    def onUpdate(self):
        self.autoUpdate=True
        
    def offUpdate(self):
        self.autoUpdate=False
    
    def isUpdate(self):
        return self.autoUpdate

class FriendTrainer(Trainer):
    '''
    @summary: 计算与用户相似的用户，为基于用户的协同过滤算法做准备
    '''
    
    def __init__(self,num=5,provider=None):
        super().__init__(num,provider)
        self.num=num
        self.provider=provider if provider else UserInterestProvider()
        self.model=None
        
    def config(self,num=None,category=None):
        self.model=None
        self.num=num if num else self.num
        self.provider=ProviderFactory.getProvider(featureCategory=category) if category else self.provider
    
    def train(self, userId):
        if not self.model:
            self.model=NearestNeighbors(n_neighbors=self.num+1).fit(self.provider.provideAll())
        distance,neighborList=self.model.kneighbors([self.provider.provide(userId)])
        if distance[0][2]==0:
            return []
        similarity=self.distanceToSimilarity(distance[0][1:])
        res=[]
        for i in range(self.num):
            res.append((neighborList[i],similarity[i]))
        return res
        
    def trainAll(self):
        if not self.model:
            self.model=NearestNeighbors(n_neighbors=self.num+1,algorithm='auto').fit(self.provider.provideAll())
        res=[]
        distances,friends=self.model.kneighbors(self.provider.provideAll())
        for count in range(len(friends)):
            friend=[]
            if distances[count][2]==0:
                res.append(friend)
                continue
            similarity=self.distanceToSimilarity(distances[count])[1:]
            neighborList= friends[count][1:]

            for i in range(self.num):
                friend.append((neighborList[i],similarity[i]))
            res.append(friend)
            print("User "+str(count)+" finded!")
        if self.isUpdate():
            # DBUtil.dumpFriends(res)
            CacheUtil.dumpUserFriends(res)
            DBUtil.dumpFriends(res)
        return res
        
    def clear(self):
        del self.model
    
    def distanceToSimilarity(self,distance):
        return list(map(lambda x:1-x,distance))

class UserFriendProvider(Provider):
    '''
    @summary: 取与用户相似的用户以进行基于用户的协同过滤
    '''
    def __init__(self,trainer=None):
        super().__init__()
        self.trainer=trainer if trainer else FriendTrainer()

    def provideFromCache(self,userIndex,load=False):

        if not self.isCached() and load:
            self.setCache(CacheUtil.loadUserFriends())
        if self.isCached():
            return self.cache[userIndex]
        return None

    def provideFromDB(self,uid):
        friend=list(map(lambda x:(x.targetIndex,x.similarity),FriendRelation.objects(userIndex=uid)))
        if len(friend)>0:
            self.setCache(friend)
            return friend
        else:
            return None

    def provideFromCompute(self,uid):
        res=self.trainer.train(uid)
        self.setCache(res)
        return res

    def provideAllFromCache(self):
        if not self.isCached():
            self.setCache(CacheUtil.loadUserFriends())
        return self.cache

    def provideAllFromDB(self):
        friends=[[]]*User.objects.count()
        for relation in FriendRelation.objects:
            friends[relation.userIndex].append((relation.targetId,relation.similarity))
        if len(friends[0])>0:
            self.setCache(friends)
            return friends
        else:
            return None

    def provideAllFromCompute(self):
        friends=None
        if self.trainer:
            friends=self.trainer.trainAll()
            self.setCache(friends)
        if self.isUpdate() and friends:
            CacheUtil.dumpUserFriends(friends)
            #DBUtil.dumpFriends(friends)
        return friends

    def simmilarity(self,userIndex,targetIndex):
        relations=FriendRelation.objects(userIndex=userIndex,targetIndex=targetIndex).only("similarity")
        return 0 if len(relations)==0 else relations[0].similarity


class TrainerCategory(Enum):
    FRIEND="friend"
  
class TrainerFactory(object):
    
    @staticmethod
    def getTrainer(category):
        return FriendTrainer()
    
