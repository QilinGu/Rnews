'''
Created on 2015年12月9日
@summary: 根据模型预测某用户对某新闻的感兴趣程度得分
@author: suemi
'''
from core.Provider import UserInterestProvider, ArticleFeatureProvider

class Predictor(object):
    
    def __init__(self,ufProvider=None,afProvider=None):
        self.ufProvider=ufProvider if ufProvider else UserInterestProvider()
        self.afProvider=afProvider if afProvider else ArticleFeatureProvider()
    
    def getParam(self,userId):
        return self.ufProvider.provide(userId)
    
    def getVector(self,articleId):
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
    
    def predict(self, userId, articleId):
        pass


class FriendPredictor(Predictor):
    '''
    @summary: 根据基于用户的协同过滤来计算用户对新闻的感兴趣程度
    '''
    
    def predict(self,userId,articleId):
        pass

class PredictorFactory(object):
    
    @staticmethod
    def getPredictor(category):
        pass
        
        
    
            