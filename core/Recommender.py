'''
Created on 2015年12月7日
@summary: 核心类，用于为单个用户推荐他感兴趣的新闻
@author: suemi
'''
from core.Predictor import PredictorFactory
from model.Entity import *
from utils.CacheUtil import CacheUtil
class Recommender:
    
    def __init__(self,predictor=None):
        self.predictor=predictor
        
    def select(self,category):
        self.predictor=PredictorFactory.getPredictor(category)
        
    def recommend(self,uid):
        pass
    
    def recommendAll(self):
        pass
    
    def filterClicked(self,uid,vec):
        return filter(lambda x:Record.isClicked(uid, x[0]),vec)
    
class BaseRecommender(Recommender):
    
    def __init__(self,topK=5,provider=None):
        super.__init__(provider)
        self.topK=topK
        
    def recommend(self, uid):
        articles=self.filterClicked(uid, self.predictor.predictAll(uid))
        articles.sort(key=lambda x:x[1],reverse=True)
        return articles[:self.topK] if len(articles)>self.topK else articles
    
    def recommendAll(self):
        res=[]
        for i in range(User.objects.count()):
            uid=CacheUtil.indexToUser[i]
            res.append(self.recommend(uid))
        return res
        
        