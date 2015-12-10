'''
Created on 2015年12月10日

@author: suemi
'''
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def recommend(req):
    pass

@require_http_methods(["GET"])
def history(req):
    pass

@require_http_methods(["POST"])
def click(req):
    pass

@require_http_methods(["POST"])
def login(req):
    pass

@require_http_methods(["GET"])
def logout(req):
    pass