from typing import List
from bson import ObjectId
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from app_car_schedule.models.car_schedule_setting import CarScheduleSetting
from app_car_schedule.utils import HasCshPermission
from app_system_setting.models import SystemApp, SystemMenu
from app_user.models.user import User, UserStatus
from app_user.utils import requiredLogin
from django.contrib import messages
from django.utils import timezone

from base_models.basemodel import UserSnapshot


@requiredLogin
def index(request: HttpRequest):
    cshSettings = CarScheduleSetting.objects.filter(isActive = True)
    hasPermission = HasCshPermission(id = str(request.currentUser.id), checkAdmin = True)
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    context = {
        "cshSettings": cshSettings,
    }
    return render(request, 'setting_car_schedule/index.html', context)

@requiredLogin
def add(request: HttpRequest):
    response = HttpResponseRedirect(reverse('indexSettingCsh'))
    hasPermission = HasCshPermission(id = str(request.currentUser.id), checkAdmin = True)
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
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
            dupUser: CarScheduleSetting = CarScheduleSetting.objects.filter(user = user).first()
            if dupUser:
                messages.error(request, "Duplicate User")
                return response
            cshSetting = CarScheduleSetting()
            cshSetting.user = ObjectId(user)
            menuList = []
            for menu in menus:
                menuList.append(ObjectId(menu))
            cshSetting.menus = menuList
            cshSetting.isAdmin = isadmin
            cshSetting.isActive = True
            currentUser: User = request.currentUser
            if currentUser:
                uCreate = UserSnapshot().UserToSnapshot(currentUser)
                if uCreate:
                    cshSetting.createBy = uCreate
            cshSetting.save()
            messages.success(request, 'Save Success')
            return response

        except Exception as e:
            print(e)
            messages.error(request, str(e))
            return response
    else:
        users: List[User] = User.objects.filter(isActive = True, status = UserStatus.Hire.value).order_by('code')
        app: SystemApp = SystemApp.objects.filter(name = "app_car_schedule").first()
        if not app:
            messages.error(request, "App not found")
            return response
        menus: List[SystemMenu] = SystemMenu.objects.filter(isActive = True, app = app.id)
        if not menus:
            messages.error(request, "Menu not found")
            return response
        selectedUsers = []
        cshSettings: List[CarScheduleSetting] = CarScheduleSetting.objects.filter(isActive = True)
        if cshSettings:
            selectedUsers = [us.user.id for us in cshSettings]
        context = {
            "users": users,
            "menus": menus,
            "selectedUsers": selectedUsers
        }
        return render(request, 'setting_car_schedule/add.html', context)
    

@requiredLogin
def edit(request: HttpRequest, id: str):
    response = HttpResponseRedirect(reverse('indexSettingCsh'))
    hasPermission = HasCshPermission(id = str(request.currentUser.id), checkAdmin = True)
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    if request.method == "POST":
        try:
            cshId = request.POST.get("cshId")
            if not cshId:
                messages.error(request, "Id is required")
                return response
            menus = request.POST.getlist("menus")
            if not menus:
                messages.error(request, "Menu is required")
                return response
            cshSetting: CarScheduleSetting = CarScheduleSetting.objects.filter(id = cshId).first()
            if not cshSetting:
                messages.error(request, "Car Schedule Setting not found")
                return response
            isadmin = True if request.POST.get("isadmin") == 'on' else False
            cshSetting.isAdmin = isadmin
            menuList = []
            for menu in menus:
                menuList.append(ObjectId(menu))
            cshSetting.menus = menuList
            cshSetting.updateDate = timezone.now()
            currentUser: User = request.currentUser
            if currentUser:
                uUpdateUser = UserSnapshot().UserToSnapshot(currentUser)
                if uUpdateUser:
                    cshSetting.updateBy = uUpdateUser
            cshSetting.save()

            messages.success(request, 'Save Success')
            return response
        except Exception as e:
            print(e)
            messages.error(request, str(e))
            return response
    else:
        if not id:
            messages.error(request, "Id is required")
            return response
        users: List[User] = User.objects.filter(isActive = True).order_by('code')
        app: SystemApp = SystemApp.objects.filter(name = "app_car_schedule").first()
        if not app:
            messages.error(request, "App not found")
            return response
        menus: List[SystemMenu] = SystemMenu.objects.filter(isActive = True, app = app.id)
        if not menus:
            messages.error(request, "Menu not found")
            return response
        cshSetting = CarScheduleSetting.objects.filter(id = id).first()
        if not cshSetting:
            messages.error(request, "Car Schedule Setting not found")
            return response
        menu_ids = [m.id for m in cshSetting.menus]
        context = {
            "users": users,
            "menus": menus,
            "cshSetting": cshSetting,
            "menu_ids": menu_ids
        }
        return render(request, 'setting_car_schedule/edit.html', context)
    
@requiredLogin
def delete(request: HttpRequest, id: str):
    try:
        if not request.method == "GET":
            return JsonResponse({'deleted': False, 'message': 'Method not allowed'})
        hasPermission = HasCshPermission(id = str(request.currentUser.id), checkAdmin = True)
        if not request.currentUser.isAdmin:
            if hasPermission == False:
                return JsonResponse({'deleted': False, 'message': 'Not Permission'})
        if not id:
            return JsonResponse({'deleted': False, 'message': 'Not found id'})
        cshSetting: CarScheduleSetting = CarScheduleSetting.objects.filter(id = id).first()
        if not cshSetting:
            return JsonResponse({'deleted': False, 'message': 'Car Schedule Setting not found'})
        cshSetting.isActive = False
        cshSetting.updateDate = timezone.now()
        currentUser: User = request.currentUser
        if currentUser:
            uUpdate = UserSnapshot().UserToSnapshot(currentUser)
            if uUpdate:
                cshSetting.updateBy = uUpdate
        cshSetting.save()

        return JsonResponse({'deleted': True, 'message': 'Delete success'})
    except Exception as e:
        print(e)
        return JsonResponse({'deleted': False, 'message': str(e)})
    

def deleteCshSettingByUser(requester: User, user: User):
    cshSetting: CarScheduleSetting = CarScheduleSetting.objects.filter(user = user.id).first()
    if cshSetting:
        cshSetting.isActive = False
        cshSetting.updateDate = timezone.now()
        if requester:
            uUpdate = UserSnapshot().UserToSnapshot(requester)
            if uUpdate:
                cshSetting.updateBy = uUpdate
        cshSetting.save()
        