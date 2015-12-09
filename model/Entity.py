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
    def load(clazz,eid):
        queryResult=clazz.objects(eid=eid)
        return queryResult[0] if len(queryResult)>0 else None
    
    @classmethod
    def loadField(clazz,eid,field):
        queryResult=clazz.objects(eid=eid).only(field)
        return getattr(queryResult[0], field) if len(queryResult)>0 else None
     #   return list(map(lambda x:getattr(x, field),queryResult))
    
    @classmethod
    def updateField(clazz,eid,field,value):
        queryResult=clazz.objects(eid=eid)
        obj=None
        if len(queryResult)==0:
            obj=clazz.new()
            obj.eid=eid
        else:
            obj=queryResult[0]
        setattr(obj, field, value)
        obj.save()
        
    
    @classmethod
    def insert(clazz,entity):
        num=clazz.objects(eid=entity.eid).count()
        if num==0:
            entity.save()
            return True
        else:
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
            queryResult[0].delete()
            entity.save()
            
    @classmethod
    def delete(clazz,entity):
        queryResult=clazz.objects(eid=entity.eid)
        if len(queryResult)>0:
            queryResult[0].delete()

class Record(Document):
    userId=StringField(max_length=20)
    articleId=StringField(max_length=20)
    clickDate=LongField()
    
    def getArticle(self):
        queryResult=Article.objects(eid=self.articleId)
        return queryResult[0] if len(queryResult)>0 else None
    
    def getUser(self):
        queryResult=User.objects(eid=self.userId)
        return queryResult[0] if len(queryResult)>0 else None
    
    @staticmethod
    def insert(record):
        num=Record.objects(userId=record.userId,articleId=record.articleId).count()
        if num == 0:
            record.save()
        
    
    @staticmethod
    def isClicked(userId,articleId):
        return True if len(Record.objects(userId=userId,articleId=articleId))>0 else False
    
class Article(Document,BaseEntity):
    eid=StringField(max_length=20,requied=True)
    index=LongField()
    title=StringField(max_length=20,default=None)
    content=StringField(default=None)
    publistDate=DateTimeField(default=None)
    
    
class User(Document,BaseEntity):
    eid=StringField(max_length=20)
    index=LongField()
    recommendation=ListField(StringField(max_length=20))
    
    def getAllClickedFromDB(self):
        queryResults=Record.objects(userId=self.eid).only('articleId')
        return list(map(lambda x:getattr(x,'articleId'),queryResults))
    
    def getAllClickedFromCache(self):
        pass
    
    def getAllClicked(self):
        return self.getAllClickedFromDB()
    
class WordBag(Document,BaseEntity):
    eid=StringField(max_length=20)
    wordList=ListField(StringField())

class ArticleFeaure(Document,BaseEntity):
    eid=StringField(max_length=20)
    topicVector=ListField(DecimalField())

class UserFeature(Document,BaseEntity):
    eid=StringField(max_length=20)
    interest=ListField(DecimalField())
    friends=ListField(StringField(max_length=20))