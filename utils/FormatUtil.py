'''
Created on 2015年12月9日

@author: suemi
'''
from datetime import datetime

class FormatUtil(object):
   
    @staticmethod
    def transferDate(dateStr):
        try:
            year=int(dateStr[0:4])
            month=int(dateStr[5:7])
            day=int(dateStr[8:10])
            hour=int(dateStr[11:-2].split(':')[0])
            minute=int(dateStr[11:-2].split(':')[1])
            return datetime(year,month,day,hour,minute)
        except Exception as ex:
            return None
    
    @staticmethod
    def tuple2dict(vec):
        res={}
        for pair in vec:
            res[pair[0]]=pair[1]
        return res
    
    @staticmethod
    def dict2tuple(src):
        res=[]
        for key,val in src.items():
            res.append((key,val))
        return res
       