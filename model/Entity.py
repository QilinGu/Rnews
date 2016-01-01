'''
Created on 2015年12月4日
@summary: 定义在mongoDB数据库中的实体
@author: suemi
'''
from mongoengine import *

connect('Rnews',host="localhost",port=5000)


class BaseEntity:
    '''
    @summary: 父类，为了便于之后的数据操作，根据Id读取对象和特定属性
    '''
    
    @classmethod
    def load(clazz,index):
        return clazz.objects[index]
    
    @classmethod
    def loadField(clazz,index,field):
        return getattr(clazz.objects[index], field)

    
    @classmethod
    def updateField(clazz,index,field,value):
        obj=clazz.objects[index]
        setattr(obj, field, value)
        obj.save()
        
    
    @classmethod
    def insert(clazz,entity):
        res=clazz.objects(eid=entity.eid)
        if len(res)==0:
            entity.save()
            return True
        else:
            entity.index=res[0].index
            return False
    
    @classmethod
    def persist(clazz,entity):
        '''
        :summary :更新id相同的，如果没有则插入
        :param clazz:
        :param entity:
        '''
        queryResult=clazz.objects(eid=entity.eid)
        if len(queryResult)==0:
            entity.save()
        else:
            entity.index=queryResult[0].index
            queryResult[0].delete()
            entity.save()
            
    @classmethod
    def delete(clazz,entity):
        queryResult=clazz.objects(eid=entity.eid)
        if len(queryResult)>0:
            queryResult[0].delete()

class Record(Document):
    userIndex=LongField()
    articleIndex=LongField()
    clickDate=LongField()
    isTrain=BooleanField(default=True)
    
    @staticmethod
    def insert(record):
        num=Record.objects(userIndex=record.userIndex,articleIndex=record.articleIndex).count()
        if num == 0:
            record.save()
    
    @staticmethod
    def getUserForArticle(articleIndex):
        queryResults=Record.objects(articleIndex=articleIndex,isTrain=True).only("userIndex")
        return list(map(lambda x:getattr(x, "userIndex"),queryResults))
    
    @staticmethod
    def getArticleForUser(userIndex):
        queryResults=Record.objects(userIndex=userIndex,isTrain=True).only("articleIndex")
        return list(map(lambda x:getattr(x, "articleIndex"),queryResults))
        
    
    @staticmethod
    def isClicked(userIndex,articleIndex):
        return True if len(Record.objects(userIndex=userIndex,articleIndex=articleIndex))>0 else False

    @staticmethod
    def isClickedForTest(userIndex,articleIndex):
        return True if len(Record.objects(userIndex=userIndex,articleIndex=articleIndex,isTrain=False))>0 else False


    @staticmethod
    def isClickedForTrain(userIndex,articleIndex):
        return True if len(Record.objects(userIndex=userIndex,articleIndex=articleIndex,isTrain=True))>0 else False
    
class Article(Document,BaseEntity):
    eid=StringField(max_length=20,requied=True)
    index=LongField()
    title=StringField(default=None)
    content=StringField(default=None)
    publistDate=DateTimeField(default=None)
    wordList=ListField(StringField())
    topicVector=ListField(FloatField())
    
class User(Document,BaseEntity):
    eid=StringField(max_length=20)
    index=LongField()
    interest=ListField(FloatField())
    
    def getAllClickedFromDB(self):
        queryResults=Record.objects(userIndex=self.index,isTrain=True).only('articleIndex')
        return list(map(lambda x:getattr(x,'articleIndex'),queryResults))
    
    def getAllClickedFromCache(self):
        pass
    
    def getAllClicked(self):
        return self.getAllClickedFromDB()

    
class FriendRelation(Document):
    userIndex=LongField(required=True)
    targetIndex=LongField(required=True)
    similarity=FloatField()
    
    @staticmethod
    def persist(relation):
        queryResult=FriendRelation.objects(userIndex=relation.userIndex,targetId=relation.targetId)
        if len(queryResult)==0:
            relation.save()
        else:
            queryResult[0].delete()
            relation.save()

class Recommendation(Document):
    userIndex=LongField()
    articleIndex=LongField()
    score=FloatField()

    @staticmethod
    def isRecommended(userIndex,articleIndex):
        return True if len(Recommendation.objects(userIndex=userIndex,articleIndex=articleIndex))>0 else False