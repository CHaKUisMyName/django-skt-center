from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from app_user.models.user import User

# Create your views here.
def index(request: HttpRequest):
    return render(request, 'user/index.html')

def addUser(request: HttpRequest):
    return render(request, 'user/add.html')

def AddAlienUser(request: HttpRequest):
    try:
        user = User()
        user.fNameEN = 'CHaKU'
        user.lNameEN = 'CHaKU'
        user.save()
        data = {'status': True, "mss": 'success'}
        return JsonResponse(data)
    except Exception as e:
        data = {'status': False, 'mss': str(e)}
        return JsonResponse(data)



# ---------- user settings ---------
def indexSettingUser(request: HttpRequest):
    return render(request, 'user/indexSetting.html')

