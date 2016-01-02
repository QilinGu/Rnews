'''
Created on 2015年12月5日
@summary: 对算法运行中的一些中间文件进行管理
@author: suemi
'''
import os,sys
from gensim import corpora
import pickle as pk

from scipy.sparse import lil_matrix

from model.Entity import *

class CacheUtil:
    path={}
    path["data"]="/Volumes/MAC/Rnews/data/"
    path["dictionary"]=path["data"]+"rnews.dict"
    path["corpus"]=path["data"]+"corpus.mm"
    path["topic"]=path["data"]+"topic.mm"
    path["articleFeature"]=path["data"]+"articleFeature.pk"
    path["userInterest"]=path["data"]+"userInterest.pk"
    path["userFriends"]=path["data"]+"userFriends.pk"
    path["recommendation"]=path["data"]+"recommendation.pk"
    path["userIds"]=path["data"]+"userIds.pk"
    path["articleIds"]=path["data"]+"articleIds.pk"
    path["record"]=path["data"]+"record.pk"
    path["userClicked"]=path["data"]+"userClick.pk"
    path["articleClicked"]=path["data"]+"articleClick.pk"
    userIds=None
    articleIds=None
    record=None
    userClicked=None
    articleClicked=None
    userClickedTest=None
    articleClickedTest=None

    @staticmethod
    def clear():
        pass
    
    @staticmethod
    def loadDictionary():
        return corpora.dictionary.Dictionary.load(CacheUtil.path["dictionary"])
    
    @staticmethod
    def dumpDictionary(dictionary):
        dictionary.save(CacheUtil.dictionaryPath)
    
    @staticmethod
    def dumpArticleFeature(feature):
        pk.dump(feature,open(CacheUtil.path["articleFeature"],'wb'))
        
    @staticmethod
    def loadArticleFeature():
        if not os.path.exists(CacheUtil.path["articleFeature"]):
            return None
        return pk.load(open(CacheUtil.path["articleFeature"],'rb'))
        
    @staticmethod
    def dumpUserInterest(interest):
        pk.dump(interest,open(CacheUtil.path["userInterest"],'wb'))
        
    @staticmethod
    def loadUserInterest():
        if not os.path.exists(CacheUtil.path["userInterest"]):
            return None
        return pk.load(open(CacheUtil.path["userInterest"],'rb'))
    
    @staticmethod
    def dumpUserFriends(friends):
        pk.dump(friends,open(CacheUtil.path["userFriends"],'wb'))
        
    @staticmethod
    def loadUserFriends():
        if not os.path.exists(CacheUtil.path["userFriends"]):
            return None
        return pk.load(open(CacheUtil.path["userFriends"],'rb'))

    @staticmethod
    def dumpRecommendation(recommendation):
        res={}
        for i in range(len(recommendation)):
            print(recommendation[i])
            tmp=list(map(lambda x:CacheUtil.loadArticleId(x[0]),recommendation[i]))
            res[CacheUtil.loadUserId(i)]=tmp
        pk.dump(res,open(CacheUtil.path["recommendation"],'wb'))


    @staticmethod
    def loadRecommendation():
        return pk.load(open(CacheUtil.path["recommendation"],'rb'))

    @staticmethod
    def loadUserId(index):
        if not CacheUtil.userIds:
            if  os.path.exists(CacheUtil.path["userIds"]):
                CacheUtil.userIds=pk.load(open(CacheUtil.path["userIds"],"rb"))
            else:
                CacheUtil.userIds=list(map(lambda x:x.eid,User.objects.only("eid")))
                pk.dump(CacheUtil.userIds,open(CacheUtil.path["userIds"],"wb"))
        return CacheUtil.userIds[index]

    @staticmethod
    def loadArticleId(index):
        if not CacheUtil.articleIds:
            if  os.path.exists(CacheUtil.path["articleIds"]):
                CacheUtil.articleIds=pk.load(open(CacheUtil.path["articleIds"],"rb"))
            else:
                CacheUtil.articleIds=list(map(lambda x:x.eid,Article.objects.only("eid")))
                pk.dump(CacheUtil.articleIds,open(CacheUtil.path["articleIds"],"wb"))
        return CacheUtil.articleIds[index]
    
    @staticmethod
    def isClicked(userIndex,articleIndex):
        if CacheUtil.record!=None:
            return CacheUtil.record[userIndex,articleIndex]!=0
        elif os.path.exists(CacheUtil.path["record"]):
            CacheUtil.record=pk.load(open(CacheUtil.path["record"],"rb"))
        else:
            tmp=lil_matrix((User.objects.count(),Article.objects.count()),dtype=int)
            for click in Record.objects(isTrain=True):
                tmp[click.userIndex,click.articleIndex]=1
            CacheUtil.record=tmp
            pk.dump(tmp,open(CacheUtil.path["record"],"wb"))
        return CacheUtil.record[userIndex,articleIndex]!=0

    @staticmethod
    def loadClickedForUser(index):
        if CacheUtil.userClicked!=None:
            return CacheUtil.userClicked[index]
        elif os.path.exists(CacheUtil.path["userClicked"]):
            CacheUtil.userClicked=pk.load(open(CacheUtil.path["userClicked"],"rb"))
        else:
            #clicked=[[]]*User.objects.count()
            clicked=[[] for i in range(User.objects.count())]
            for click in Record.objects(isTrain=True):
                clicked[click.userIndex].append(click.articleIndex)
            CacheUtil.userClicked=clicked
            pk.dump(clicked,open(CacheUtil.path["userClicked"],"wb"))
        return CacheUtil.userClicked[index]

    @staticmethod
    def loadClickedForArticle(index,isTrain=True):
        if CacheUtil.articleClicked!=None:
            return CacheUtil.articleClicked[index]
        elif os.path.exists(CacheUtil.path["articleClicked"]):
            CacheUtil.articleClicked=pk.load(open(CacheUtil.path["articleClicked"],"rb"))
        else:
            clicked=[[] for i in range(Article.objects.count())]
            for click in Record.objects(isTrain=True):
                clicked[click.articleIndex].append(click.userIndex)
            CacheUtil.articleClicked=clicked
            pk.dump(clicked,open(CacheUtil.path["articleClicked"],"wb"))
        return CacheUtil.articleClicked[index]

