'''
Created on 2015年12月4日

@author: suemi
'''
from mongoengine import *

connect('Rnews',host="localhost",port=5000)


class BaseEntity:
    
    @classmethod
    def load(clazz,eid):
        queryResult=clazz.objects(eid=eid)
        return queryResult[0] if len(queryResult)>0 else None
    
    @classmethod
    def loadField(clazz,eid,field):
        queryResult=clazz.objects(eid=eid)
        return list(map(lambda x:getattr(x, field),queryResult))

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
    def isClicked(userId,articleId):
        return True if len(Record.objects(userId=userId,articleId=articleId))>0 else False
    
class Article(Document,BaseEntity):
    eid=StringField(max_length=20,requied=True)
    title=StringField(max_length=20,default=None)
    content=StringField(default=None)
    publistDate=DateTimeField(default=None)
    
#     @staticmethod
#     def load(articleId):
#         queryResult=Article.objects(id=articleId)
#         return queryResult[0] if len(queryResult)>0 else None
#     
#     @staticmethod
#     def loadField(articleId,field):
#         queryResult=Article.objects(id=articleId).only(field)
#         return 
    
    
class User(Document):
    eid=StringField(max_length=20)
    recommendation=ListField(StringField(max_length=20))
    friends=ListField(StringField(max_length=20))
    
    def getAllClickedFromDB(self):
        queryResults=Record.objects(userId=self.eid).only('articleId')




