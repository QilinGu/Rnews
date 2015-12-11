'''
Created on 2015年12月10日

@author: suemi
'''
from django.views.generic.base import TemplateView
from django.views.decorators.http import require_http_methods
from model.Entity import *
from django.http.response import JsonResponse


class ArticleView(TemplateView):
    pass

class ArticleDetailView(TemplateView):
    pass

@require_http_methods(["POST"])
def list(req):
    pageIndex=req.POST["pageIndex"] if req.POST["pageIndex"] else 0
    pageNum=req.POST["pageNum"] if req.POST["pageNum"] else 20
    articles=list(map(lambda x:x.__data,Article.objects[pageIndex*pageNum:(pageIndex+1)*pageNum]))
    words=WordBag.objects(eid__in=list(map(lambda x:x["eid"],articles)))
    for i in range(len(articles)):
        articles[i]["keyWord"]=words[i].wordList
    return JsonResponse({
                         "success":True,
                         "data":articles
    })

@require_http_methods(["GET"])
def detail(req,articleId):
    article=Article.objects(eid=articleId).first()
    article=article.__data
    article["keyWord"]=WordBag.objects(eid=articleId).first().wordList
    return JsonResponse({
                         "success":True,
                         "data":article
    })

