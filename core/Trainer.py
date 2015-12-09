'''
Created on 2015年12月9日
@summary: 将用户是否点击某个新闻看成是一个分类或回归问题，对每个用户训练和预测他对某个新闻的得分，最简单的例子是用户特征与新闻特征直接计算余弦相似度
@author: suemi
'''
from core.Provider import UserInterestProvider
from sklearn.neighbors.unsupervised import NearestNeighbors
from faulthandler import disable
from utils.CacheUtil import CacheUtil
class Trainer(object):

    def __init__(self, provider):
        pass
    
    def train(self,userId):
        pass

    def trainAll(self):
        pass
    
    def clear(self):
        pass


class FriendTrainer(Trainer):
    '''
    @summary: 计算与用户相似的用户，为基于用户的协同过滤算法做准备
    '''
    
    def __init__(self,friendNum=5,provider=None):
        self.friendNum=friendNum
        self.provider=provider if provider else UserInterestProvider()
        self.model=None
        
    
    def train(self, userId):
        if not self.model:
            self.model=NearestNeighbors(n_neighbors=self.friendNum+1).fit(self.provider.provideAll())
        distance,indexs=self.model.kneighbors([self.provider.provide(userId)])
        similarity=self.distanceToSimilarity(distance[0][1:])
        neighborList=list(map(lambda x:CacheUtil.indexToUser(x),indexs))
        res=[]
        for i in range(self.friendNum):
            res.append((neighborList[i],similarity[i]))
        return res
        
    def trainAll(self):
        if not self.model:
            self.model=NearestNeighbors(n_neighbors=self.friendNum+1,algorithm='auto').fit(self.provider.provideAll())
        res={}
        distances,indexs=self.model.kneighbors(self.provider.provideAll)
        for count in range(len(indexs)):
            uid=CacheUtil.indexToUser(count)
            similarity=self.distanceToSimilarity(distances[count])
            neighborList= list(map(lambda x:CacheUtil.indexToUser(x),indexs[count]))
            res[uid]=[]
            for i in range(self.friendNum):
                res[uid].append((neighborList[i],similarity[i]))
        return res
        
    def clear(self):
        del self.model
    
    def distanceToSimilarity(self,distance):
        return list(map(lambda x:1.0/(x+1),distance))
   
class TrainerFactory(object):
    
    @staticmethod
    def getTrainer(category):
        return FriendTrainer()
    
