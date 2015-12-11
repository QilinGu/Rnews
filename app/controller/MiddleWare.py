'''
Created on 2015年12月10日

@author: suemi
'''
from django.http.response import Http404

class LoginFilter(object):
    def process_request(self,req):
        url=req.get_full_path()
        uid=req.session.get("uid")
        if not url in ["/"] and not uid:
            raise Http404
        else:
            return None