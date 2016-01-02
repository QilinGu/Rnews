'''
Created on 2015年12月7日
@summary: 核心类，用于为单个用户推荐他感兴趣的新闻
@author: suemi
'''

from core.Predictor import PredictorFactory, SimPredictor, FriendPredictor
from model.Entity import *
from enum import Enum
from utils.CacheUtil import CacheUtil
from utils.DBUtil import DBUtil


class Recommender:
    
    def __init__(self,predictor=None):
        self.predictor=predictor
        
    def select(self,category):
        self.predictor=PredictorFactory.getPredictor(category)
        
    def recommend(self,uid):
        pass
    
    def recommendAll(self):
        pass
    
    def filterClicked(self,userindex,vec):
        return list(filter(lambda x:CacheUtil.isClicked(userindex, x[0]),vec))
    
class ContentBasedRecommender(Recommender):
    
    def __init__(self,topK=5,predictor=None):
        super().__init__(predictor)
        self.topK=topK
        if not predictor:
            self.predictor=SimPredictor()
        
    def recommend(self, uid):
        #articles=self.filterClicked(uid, self.predictor.predictAll(uid))
        articles= self.predictor.predictAll(uid)
        articles.sort(key=lambda x:x[1],reverse=True)
        return articles[:self.topK] if len(articles)>self.topK else articles
    
    def recommendAll(self):
        res=[]
        for i in range(User.objects.count()):
            res.append(self.recommend(i))
            print("User "+ str(i)+" recommended!")
        return res

# class UCFRecommender(Recommender):
#     def __init__(self,topK=5,data=None):
#         self.topK=topK
#         self.data=data if data else DBUtil.toDict()
#         model = MatrixPreferenceDataModel(self.data)
#         similarity = UserSimilarity(model, pearson_correlation)
#         self.instance= UserBasedRecommender(model, similarity, with_preference=True)
#
#     def recommendAll(self):
#         res=[]
#         for i in range(User.objects.count()):
#             tmp=self.instance.recommend(i)
#             vec=tmp[:self.topK] if len(tmp)>self.topK else tmp
#             res.append(vec)
#             print("User "+ str(i)+" recommended!")
#         return res

class UCFRecommender(Recommender):

    def __init__(self,topK=5,predictor=None):
        super().__init__(predictor)
        self.topK=topK
        if not predictor:
            self.predictor=FriendPredictor()

    def recommend(self, uid):
        #articles=self.filterClicked(uid, self.predictor.predictAll(uid))
        articles= self.predictor.predictAll(uid)
        articles.sort(key=lambda x:x[1],reverse=True)
        return articles[:self.topK] if len(articles)>self.topK else articles

    def recommendAll(self):
        res=[]
        for i in range(User.objects.count()):
            res.append(self.recommend(i))
            print("User "+ str(i)+" recommended!")
        return res

class RecommenderCategory(Enum):
    CONTENT="content"
    UCF="ucf"
      
class RecommenderFactory:
    
    @staticmethod
    def getRecommender(category=RecommenderCategory.CONTENT):
        if category==RecommenderCategory.CONTENT:
            return ContentBasedRecommender()
        elif category==RecommenderCategory.UCF:
            return UCFRecommender()