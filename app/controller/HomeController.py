'''
Created on 2015年12月10日

@author: suemi
'''
from django.views.decorators.http import require_http_methods
from django.shortcuts import render_to_response

@require_http_methods(["GET"])
def home(req):
    return render_to_response("index.html")