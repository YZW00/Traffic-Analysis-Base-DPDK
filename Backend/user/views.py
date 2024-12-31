from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import auth
from django.contrib.auth.models import User
import json
# Create your views here.

def login(request):
    if request.method != 'POST':
        return HttpResponse(json.dumps({'status': 'fail', 'err': 'Wrong request method'}), content_type='application/json')
    else:
        rb = json.loads(request.body)
        try:
            username = rb['user']
            password = rb['password']
            if not username or not password:
                return HttpResponse(json.dumps({'status': 'fail', 'err': 'user or password cant be None'}), content_type='application/json')
            userObj = auth.authenticate(username=username,password=password)  # 类型为<class 'django.contrib.auth.models.User'>

            if not userObj:
                return HttpResponse(json.dumps({'status': 'fail', 'err': 'Wrong Authentication'}), content_type='application/json')
            else:
                auth.login(request, userObj)
                return HttpResponse(json.dumps({'status': 'success'}), content_type='application/json')
        except Exception as e:
            return HttpResponse(json.dumps({'status': 'fail', 'err': str(e)}), content_type='application/json')