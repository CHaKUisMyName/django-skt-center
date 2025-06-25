from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from app_organization.models import Organization
from app_position.models import Position
from app_user.models.user import User, UserStatus

# Create your views here.
def index(request: HttpRequest):
    return render(request, 'user/index.html')

def addUser(request: HttpRequest):
    if request.method == "POST":
        response = HttpResponseRedirect(reverse('indexUser'))
        try:
            return response
        except Exception as e:
            print(e)
            messages.error(request, str(e))
            return response
    else:
        userStatus = [{"id":us.value, "name":us.name}for us in UserStatus]
        context = {
            'userStatus': userStatus
        }
        return render(request, 'user/add.html', context= context)

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

