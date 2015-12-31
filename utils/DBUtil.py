'''
Created on 2015年12月5日
@summary: 处理一些批量写入数据库的事宜
@author: suemi
'''
import codecs

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
            record.userId=tmp[0]
            record.articleId=tmp[1]
            record.clickDate=tmp[2]
            record.save()
            
            user=User()
            user.eid=record.userId
            user.index=user_count
            if User.insert(user):
                user_count+=1
                
            article=Article()
            article.eid=record.articleId
            article.title=tmp[3]
            article.content=tmp[4]
            article.publistDate=FormatUtil.transferDate(tmp[-1])
            article.index=article_count
            print(article.eid)
            if Article.insert(article):
                article_count+=1
            count+=1
            del user,record,article
            line=src.readline()
            
    @staticmethod
    def dumpArticleFeature(feature):
        count=0
        for article in Article.objects.only("eid").no_cache():
            af=ArticleFeaure()
            af.eid=article.eid
            af.topicVector=feature[count]
            ArticleFeaure.persist(af)
            count+=1
            
     
    @staticmethod
    def dumpTopic(corpus):
        for i in range(len(corpus)):
            doc=corpus[i]
            vector=list(map(lambda x:x[1],doc)) 
            feature=ArticleFeaure()
            feature.eid= Article.objects[i].eid
            feature.topicVector=vector
            ArticleFeaure.persist(feature)
            print("Topic of Article "+feature.eid+" saved successfully!")
    
    @staticmethod
    def dumpInterest(interests):
        for user in User.objects.no_cache():
            uf=UserFeature()
            uf.eid=user.eid
            uf.interest=interests[user.index]
            UserFeature.persist(uf)
           
    @staticmethod
    def dumpFriends(friends):
        FriendRelation.drop_collection()
        for key,val in friends.items():
            for pair in val:
                relation=FriendRelation()
                relation.userId=key
                relation.targetId=val[0]
                relation.similarity=val[1]
                relation.save()
            print("Friends of User "+key+" write successfully!")
    
    @staticmethod
    def dumpFriendsForUser(uid,friend):
        relations=FriendRelation.objects(userId=uid)
        for relation in relations:
            relation.delete()
        for pair in friend:
            relation=FriendRelation()
            relation.userId=uid
            relation.targetId=pair[0]
            relation.similarity=pair[1]
            relation.save()
            
    @staticmethod
    def dumpRecommendation(rec):
        Recommendation.drop_collection()
        for user in User.objects.no_cache():
            for pair in rec[user.index]:
                recommendation=Recommendation()
                recommendation.userId=user.eid
                recommendation.articleId=pair[0]
                recommendation.score=pair[1]
                recommendation.save()
            print("Recommendation For User "+user.eid+" already saved!")
    
    
    @staticmethod
    def dumpRecommendationForUser(uid,rec):
        recommendations=Recommendation.objects(userId=uid)
        for recommendation in recommendations:
            recommendation.delete()
        for pair in rec:
            recommendation=Recommendation()
            recommendation.userId=uid
            recommendation.articleId=pair[0]
            recommendation.score=pair[1]
            recommendation.save()
            