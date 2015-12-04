'''
Created on 2015年12月4日

@author: suemi
'''
from mongoengine import *

connect('Rnews',host="localhost",port="5000")

class Record(Document):
    userId=StringField(max_length=20)
    articleId=StringField(max_length=20)
    clickDate=LongField()
    title=StringField(max_length=20)
    content=StringField()
    publistDate=DateTimeField()