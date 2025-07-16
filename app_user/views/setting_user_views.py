import json
from typing import List
from bson import ObjectId
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone

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
    response = HttpResponseRedirect(reverse('indexSettingUser'))
    if request.method == "POST":
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
            dupUser: UserSetting = UserSetting.objects.filter(user = user).first()
            if dupUser:
                messages.error(request, "Duplicate User")
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
        app: SystemApp = SystemApp.objects.filter(name = "app_organization").first()
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
    
@requiredLogin
def editSettingUser(request: HttpRequest, id: str):
    response = HttpResponseRedirect(reverse('indexSettingUser'))
    if request.method == "POST":
        try:
            sid = request.POST.get("id")
            if not id:
                messages.error(request, "Id is required")
                return response
            isadmin = True if request.POST.get("isadmin") == 'on' else False
            
            menus = request.POST.getlist("menus")
            if not menus:
                messages.error(request, "Menu is required")
                return response
            
            userSetting = UserSetting.objects.filter(id = sid).first()
            if not userSetting:
                messages.error(request, "User Setting not found")
                return response
            
            userSetting.isAdmin = isadmin
            menuList = []
            for menu in menus:
                menuList.append(ObjectId(menu))
            userSetting.menus = menuList
            userSetting.updateDate = timezone.now()

            currentUser: User = request.currentUser
            if currentUser:
                uUpdate = UserSnapshot().UserToSnapshot(currentUser)
                if uUpdate:
                    userSetting.updateBy = uUpdate
            userSetting.save()

            messages.success(request, 'Save Success')
            return response
        except Exception as e:
            print(e)
            messages.error(request, str(e))
            return response
    else:
        users: List[User] = User.objects.filter(isActive = True)
        app: SystemApp = SystemApp.objects.filter(name = "app_organization").first()
        if not app:
            messages.error(request, "App not found")
            return response
        menus: List[SystemMenu] = SystemMenu.objects.filter(isActive = True, app = app.id)
        if not menus:
            messages.error(request, "Menu not found")
            return response
        userSetting: UserSetting = UserSetting.objects.filter(id = id).first()
        if not userSetting:
            messages.error(request, "User Setting not found")
            return response
        
        menu_ids = [m.id for m in userSetting.menus]

        context = {
            "users": users,
            "menus": menus,
            "userSetting": userSetting,
            "menu_ids": menu_ids
        }
        return render(request, 'setting_user/editSetting.html',context)
    
@requiredLogin
def deleteSettingUser(request: HttpRequest, id: str):
    try:
        if not request.method == "GET":
            return JsonResponse({'deleted': False, 'message': 'Method not allowed'})
        if not id:
            return JsonResponse({'deleted': False, 'message': 'Not found id'})
        
        userSetting: UserSetting = UserSetting.objects.filter(id = id).first()
        if not userSetting:
            return JsonResponse({'deleted': False, 'message': 'User Setting not found'})
        userSetting.isActive = False
        userSetting.updateDate = timezone.now()
        currentUser: User = request.currentUser
        if currentUser:
            uUpdate = UserSnapshot().UserToSnapshot(currentUser)
            if uUpdate:
                userSetting.updateBy = uUpdate
        userSetting.save()
        
        return JsonResponse({'deleted': True, 'message': 'Delete success'})
    except Exception as e:
        return JsonResponse({'deleted': False, 'message': str(e)})

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