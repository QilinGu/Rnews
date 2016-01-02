'''
Created on 2015年12月8日
@summary: 对算法的效果进行计算评估
@author: suemi
'''
from enum import Enum

import time

from core.Provider import RecommendProvider
from model.Entity import *
from utils.CacheUtil import CacheUtil
from sklearn.metrics import hamming_loss

class Evaluator(object):
    
    def __init__(self, provider=None):
        '''
        Constructor
        '''
        self.provider=provider if provider else RecommendProvider()
        
    def precision(self):
        '''
        @summary: 计算分类准确率
        '''
        pass
    
    def recall(self):
        '''
        @summary: 计算召回率
        '''
        pass
    
    def coverage(self):
        '''
        @summary: 计算覆盖率
        '''
        pass
    
    def diversity(self):
        '''
        @summary: 计算多样性
        '''
        pass


class BaseEvaluator(Evaluator):

    def __init__(self):
        super().__init__()
        self.success=None
    
    def intersection(self):
        if self.success:
            return self.success
        success=0
        if Recommendation.objects.count()<Record.objects(isTrain=False).count():
            for rec in Recommendation.objects:
                # start=time.time()
                if Record.isClickedForTest(rec.userIndex, rec.articleIndex):
                    success+=1
                # end=time.time()
                # print(end-start)
        else:
            for rec in Record.objects(isTrain=False):
                # start=time.time()
                if Recommendation.isRecommended(rec.userIndex, rec.articleIndex):
                    success+=1
                # end=time.time()
                # print(end-start)
        self.success=success
        return success
    
    def precision(self):
        return self.intersection()*1.0/Recommendation.objects.count()
    
    def recall(self):
        return self.intersection()*1.0/Record.objects(isTrain=False).count()
    
    def coverage(self):
        recArticles=list(map(lambda x:x.articleIndex,Recommendation.objects.only("articleIndex")))
        return len(set(recArticles))*1.0/Article.objects.count()
    
    def diversity(self):
        rec=self.provider.provideAll()
        data=self.provider.provideIndexMatrix()
        count=len(data);distance=0.0
        for i in range(count):
            for j in range(i+1,count):
                distance+=hamming_loss(data[i],data[j])
        return 2*distance/(count*(count-1))
                
        
class Metric(Enum):
    PRECISION="precision"
    RECALL="recall"
    DIVERSITY="diversity"
    COVERAGE="coverage"
    ALL="all"
    
                