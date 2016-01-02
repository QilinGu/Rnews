'''
Created on 2015年12月5日
@summary: 处理一些批量写入数据库的事宜
@author: suemi
'''
import codecs
import numpy as np
from model.Entity import *
from utils.FormatUtil import FormatUtil
class DBUtil:
    
    @staticmethod
    def dumpRawData(filePath,start=0,end=1000000):
        src=codecs.open(filePath,'r','utf8')
        line=src.readline()
        user_count=User.objects.count()
        article_count=Article.objects.count()
        count=0
        record_count=Record.objects.count()
        start=record_count if record_count<start else start
        while line:
            if count<start:
                count+=1
                continue
            elif count>end:
                break
            tmp=line.split("\t")
            record=Record()
            record.clickDate=tmp[2]

            user=User()
            user.eid=tmp[0]
            user.index=user_count
            if User.insert(user):
                user_count+=1
                
            article=Article()
            article.eid=tmp[1]
            article.title=tmp[3]
            article.content=tmp[4]
            article.publistDate=FormatUtil.transferDate(tmp[-1])
            article.index=article_count
            print(article.eid)
            if Article.insert(article):
                article_count+=1
            record.articleIndex=article.index
            record.userIndex=user.index
            Record.insert(record)
            count+=1
            del user,record,article
            line=src.readline()
            
    @staticmethod
    def dumpArticleFeature(feature):
        for i in range(Article.objects.count()):
            article=Article.objects[i]
            article.topicVector=feature[i]
            article.save()

     
    @staticmethod
    def dumpTopic(corpus,topicNum):
        i=0
        for doc in corpus:
            vector=[0]*topicNum
            for pair in doc:
                vector[pair[0]]=pair[1]
            article=Article.objects[i]
            article.topicVector=vector
            article.save()
            i+=1
    
    @staticmethod
    def dumpInterest(interests):
        for user in User.objects.no_cache():
            user.interest=interests[user.index]
            user.save()

    @staticmethod
    def dumpFriends(friends):
        FriendRelation.drop_collection()
        for i in range(len(friends)):
            for pair in friends[i]:
                relation=FriendRelation()
                relation.userIndex=i
                relation.targetIndex=pair[0]
                relation.similarity=pair[1]
                relation.save()
            print("Friends of User "+str(i)+" write successfully!")
    

            
    @staticmethod
    def dumpRecommendation(rec):
        Recommendation.drop_collection()
        for i in range(len(rec)):
            for pair in rec[i]:
                recommendation=Recommendation()
                recommendation.userIndex=i
                recommendation.articleIndex=pair[0]
                recommendation.score=pair[1]
                recommendation.save()
            print("Recommendation For User "+str(i)+" already saved!")
    
    @staticmethod
    def toDict():
        res=dict.fromkeys(range(User.objects.count()))
        for i in res.keys():
            res[i]={}
        for click in Record.objects(isTrain=True):
            res[click.userIndex][click.articleIndex]=1
        return res

    @staticmethod
    def randomSplit(ratio):
        for click in Record.objects:
            tmp=np.random.ranf()
            click.isTrain=True if tmp<ratio else False
            click.save()

    @staticmethod
    def splitByClickedDate(day):
        middle=1393603220+day*3600*24
        for click in Record.objects:
            click.isTrain=True if click.clickDate<middle else False
            click.save()



            