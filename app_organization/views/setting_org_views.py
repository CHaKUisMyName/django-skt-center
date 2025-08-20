from typing import List
from bson import ObjectId
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from app_organization.models.org_setting import OrgSetting
from app_organization.utils import isSettingOrgAdmin
from app_system_setting.models import SystemApp, SystemMenu
from app_user.models.user import User
from app_user.utils import requiredLogin
from django.contrib import messages
from django.utils import timezone

from base_models.basemodel import UserSnapshot



@requiredLogin
def indexSettingOrg(request: HttpRequest):
    orgSettings = OrgSetting.objects.filter(isActive = True)
    isOrgAdmin = isSettingOrgAdmin(request.currentUser.id)
    if not request.currentUser.isAdmin:
        if isOrgAdmin == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    context ={
        "orgSettings": orgSettings
    }
    return render(request, 'setting_org/indexSetting.html', context)

@requiredLogin
def addSettingOrg(request: HttpRequest):
    response = HttpResponseRedirect(reverse('indexSettingOrg'))
    isOrgAdmin = isSettingOrgAdmin(request.currentUser.id)
    if not request.currentUser.isAdmin:
        if isOrgAdmin == False:
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
            dupUser: OrgSetting = OrgSetting.objects.filter(user = user).first()
            if dupUser:
                messages.error(request, "Duplicate User")
                return response
            
            orgSetting = OrgSetting()
            orgSetting.user = ObjectId(user)
            menuList = []
            for menu in menus:
                menuList.append(ObjectId(menu))
            orgSetting.menus = menuList
            orgSetting.isAdmin = isadmin
            orgSetting.isActive = True
            currentUser: User = request.currentUser
            if currentUser:
                uCreate = UserSnapshot().UserToSnapshot(currentUser)
                if uCreate:
                    orgSetting.createBy = uCreate
            orgSetting.save()
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
        selectedUsers = []
        orgSettings: List[OrgSetting] = OrgSetting.objects.filter(isActive = True)
        if orgSettings:
            selectedUsers = [us.user.id for us in orgSettings]


        context = {
            "users": users,
            "menus": menus,
            "selectedUsers": selectedUsers
        }
        return render(request, 'setting_org/addSetting.html',context)
    
@requiredLogin
def editSettingOrg(request: HttpRequest, id: str):
    response = HttpResponseRedirect(reverse('indexSettingOrg'))
    isOrgAdmin = isSettingOrgAdmin(request.currentUser.id)
    if not request.currentUser.isAdmin:
        if isOrgAdmin == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    if request.method == "POST":
        try:
            idsorg = request.POST.get("idsorg")
            if not idsorg:
                messages.error(request, "Id is required")
                return response
            menus = request.POST.getlist("menus")
            if not menus:
                messages.error(request, "Menu is required")
                return response
            orgSetting: OrgSetting = OrgSetting.objects.filter(id = idsorg).first()
            if not orgSetting:
                messages.error(request, "Org Setting not found")
                return response
            isadmin = True if request.POST.get("isadmin") == 'on' else False
            orgSetting.isAdmin = isadmin
            menuList = []
            for menu in menus:
                menuList.append(ObjectId(menu))
            orgSetting.menus = menuList
            orgSetting.updateDate = timezone.now()
            currentUser: User = request.currentUser
            if currentUser:
                uUpdateUser = UserSnapshot().UserToSnapshot(currentUser)
                if uUpdateUser:
                    orgSetting.updateBy = uUpdateUser
            orgSetting.save()

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
        users: List[User] = User.objects.filter(isActive = True)
        app: SystemApp = SystemApp.objects.filter(name = "app_organization").first()
        if not app:
            messages.error(request, "App not found")
            return response
        menus: List[SystemMenu] = SystemMenu.objects.filter(isActive = True, app = app.id)
        if not menus:
            messages.error(request, "Menu not found")
            return response
        orgSetting: OrgSetting = OrgSetting.objects.filter(id = id).first()
        if not orgSetting:
            messages.error(request, "Org Setting not found")
            return response
        menu_ids = [m.id for m in orgSetting.menus]
        context = {
            "users": users,
            "menus": menus,
            "orgSetting": orgSetting,
            "menu_ids": menu_ids
        }
        return render(request, 'setting_org/editSetting.html', context)
    
@requiredLogin
def deleteSettingOrg(request: HttpRequest, id: str):
    try:
        isOrgAdmin = isSettingOrgAdmin(request.currentUser.id)
        if not request.currentUser.isAdmin:
            if isOrgAdmin == False:
                return JsonResponse({'deleted': False, 'message': 'Not Permission'})
        if not request.method == "GET":
            return JsonResponse({'deleted': False, 'message': 'Method not allowed'})
        if not id:
            return JsonResponse({'deleted': False, 'message': 'Not found id'})
        
        orgSetting: OrgSetting = OrgSetting.objects.filter(id = id).first()
        if not orgSetting:
            return JsonResponse({'deleted': False, 'message': 'Org Setting not found'})
        orgSetting.isActive = False
        orgSetting.updateDate = timezone.now()
        currentUser: User = request.currentUser
        if currentUser:
            uUpdate = UserSnapshot().UserToSnapshot(currentUser)
            if uUpdate:
                orgSetting.updateBy = uUpdate
        orgSetting.save()

        return JsonResponse({'deleted': True, 'message': 'Delete success'})
    except Exception as e:
        return JsonResponse({'deleted': False, 'message': str(e)})
    
@requiredLogin
def importSettingOrg(request: HttpRequest):
    return render(request, 'setting_org/importSetting.html')