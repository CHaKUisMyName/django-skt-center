import json
from typing import List
from bson import ObjectId
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from app_system_setting.models import SystemApp, SystemMenu
from app_user.models.user import User
from app_user.models.user_setting import UserSetting
from app_user.utils import requiredLogin
from base_models.basemodel import UserSnapshot

@requiredLogin
def indexSettingUser(request: HttpRequest):
    userSettings = UserSetting.objects.filter(isActive = True)
    context = {
        "userSettings": userSettings
    }
    return render(request, 'setting_user/indexSetting.html', context)

@requiredLogin
def addSettingUser(request: HttpRequest):
    if request.method == "POST":
        response = HttpResponseRedirect(reverse('indexSettingUser'))
        try:
            isadmin = True if request.POST.get("isadmin") == 'on' else False
            user = request.POST.get("user")
            if not user:
                messages.error(request, "User is required")
                return response
            menus = request.POST.getlist("menus")
            if not menus:
                messages.error(request, "Menu is required")
                return response
            
            userSetting = UserSetting()
            userSetting.user = ObjectId(user)
            menuList = []
            for menu in menus:
                menuList.append(ObjectId(menu))
            userSetting.menus = menuList
            userSetting.isAdmin = isadmin
            userSetting.isActive = True
            currentUser: User = request.currentUser
            if currentUser:
                uCreate = UserSnapshot().UserToSnapshot(currentUser)
                if uCreate:
                    userSetting.createBy = uCreate
            userSetting.save()

            messages.success(request, 'Save Success')
            return response
        except Exception as e:
            print(e)
            messages.error(request, str(e))
            return response

    else:
        users: List[User] = User.objects.filter(isActive = True)
        app: SystemApp = SystemApp.objects.filter(name = "app_user").first()
        if not app:
            messages.error(request, "App not found")
            return response
        menus: List[SystemMenu] = SystemMenu.objects.filter(isActive = True, app = app.id)
        if not menus:
            messages.error(request, "Menu not found")
            return response
        context = {
            "users": users,
            "menus": menus
        }
        return render(request, 'setting_user/addSetting.html', context)


# @requiredLogin
# def addSettingUser(request: HttpRequest):
#     if request.method == "GET":
#         # return JsonResponse({'success': False, 'data': [], 'message': 'Method not allowed'})
#         return render(request, 'setting_user/addSetting.html')
#     try:
#         # -- request.body = b'[{"emp":"...","menu":["..."],"isadmin":false}]'
#         body_unicode = request.body.decode('utf-8')# -- [{"emp":"...","menu":["..."],"isadmin":false}]
#         data = json.loads(body_unicode)  # <-- data เป็น list ของ dict
        
#         for us in data:
#             menus = []
#             for menu in us.get("menu"):
#                 menus.append(ObjectId(menu))

#             userSetting = UserSetting()
#             userSetting.user = ObjectId(us.get("emp"))
#             userSetting.menus = menus
#             userSetting.isAdmin = us.get("isadmin")
#             userSetting.isActive = True
#             # userSetting.save()
        
#         return JsonResponse({'success': True, 'data': [], 'message': 'Save Success'})
#     except Exception as e:
#         return JsonResponse({'success': False, 'data': [], 'message': str(e)})