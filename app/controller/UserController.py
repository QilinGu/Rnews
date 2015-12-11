'''
Created on 2015年12月10日

@author: suemi
'''
from django.views.decorators.http import require_http_methods
from django.http.response import HttpResponseRedirect, JsonResponse
from model.Entity import *


@require_http_methods(["GET"])
def recommend(req):
    recs=list(map(lambda x:getattr(x, "articleId"),Recommendation.objects(userId=req.POST["uid"])))
    articles=Article.objects(eid__in=recs).exclude("content")
    articles=list(map(lambda x:x.__data,articles))
    count=0
    for word in WordBag.objects(eid__in=recs):
        articles[count]["keyWord"]=word.wordList
        count+=1
    return JsonResponse({
                         "success":True,
                         "data":articles
                         })

@require_http_methods(["GET"])
def history(req):
    aids=Record.getArticleForUser(req.POST["uid"])
    articles=list(lambda x:x.__data,Article.objects(eid__in=aids).exclude("content"))
    count=0
    for word in WordBag.objects(eid__in=aids):
        articles[count]["keyWord"]=word.wordList
        count+=1
    return JsonResponse({
                        "success":True,
                        "data":articles
                         })

@require_http_methods(["POST"])
def click(req):
    pass

@require_http_methods(["POST"])
def login(req):
    req.session["uid"]=req.POST["uid"]
    return HttpResponseRedirect("/")

@require_http_methods(["GET"])
def logout(req):
    req.session["uid"]=None
    return HttpResponseRedirect("/")