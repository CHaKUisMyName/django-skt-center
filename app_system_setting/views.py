from datetime import datetime
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from bson import ObjectId

from app_system_setting.models import SystemApp, SystemMenu
from app_user.models.user import User
from app_user.utils import requiredLogin
from base_models.basemodel import UserSnapshot

# ----------- System App Name -----------
@requiredLogin
def indexApp(request: HttpRequest):
    # sysApp = SystemApp.objects(isActive=True)
    sysApp = SystemApp.objects()
    context = {
        "sysApp": sysApp
    }
    return render(request, "system_app/index_app.html", context= context)

@requiredLogin
def addApp(request: HttpRequest):
    if request.method == "POST":
        response = HttpResponseRedirect(reverse('indexApp'))
        try:
            appname = request.POST.get("appname")
            if not appname:
                messages.error(request, "App Name is required")
                return response
            
            currentUser: User = request.currentUser

            sysApp = SystemApp()
            sysApp.name = appname
            sysApp.isActive = True
            if currentUser:
                uCreate = UserSnapshot().UserToSnapshot(currentUser)
                if uCreate:
                    sysApp.createBy = uCreate
                sysApp.createDate = timezone.now()

            sysApp.save()

            messages.success(request, 'Save Success')
        except Exception as e:
            print(e)
            messages.error(request, str(e))
        return response

    return render(request, "system_app/add_app.html")

@requiredLogin
def editApp(request: HttpRequest, id):
    response = HttpResponseRedirect(reverse('indexApp'))
    if request.method == "POST":
        try:
            idApp = request.POST.get("idApp")
            if not idApp:
                messages.error(request, "Not found id !")
                return response
            
            appname = request.POST.get("appname")
            if not appname:
                messages.error(request, "App Name is required")
                return response
            
            app = SystemApp.objects(id = idApp).first()
            if not app:
                messages.error(request, "Not Found Data !")
                return response
            
            app.name = appname
            currentUser: User = request.currentUser
            if currentUser:
                uUpdate = UserSnapshot().UserToSnapshot(currentUser)
                if uUpdate:
                    app.updateBy = uUpdate
                app.updateDate = timezone.now()
            app.save()

            messages.success(request, 'Save Success')
        except Exception as e:
            print(e)
            messages.error(request, str(e))
        return response
    else:
        try:
            app = SystemApp.objects(id = id).first()
            if  not app:
                messages.error(request, "Not Found Data !")
                return response
            context = {
                "app": app
            }
            return render(request, "system_app/edit_app.html",context= context)
        except Exception as e:
            print(e)
            messages.error(request, str(e))
            return response

@requiredLogin       
def deleteApp(request: HttpRequest, id):
    try:
        app = SystemApp.objects(id = id).first()
        if not app:
            returnData = {
                'deleted': False,
                'message': 'Not Found Data'
            }
            return returnData
        currentUser = request.currentUser
        if currentUser:
            uDelete = UserSnapshot().UserToSnapshot(currentUser)
            if uDelete:
                app.updateBy = uDelete
            app.updateDate = timezone.now()
        app.isActive = False
        app.save()
        returnData = {
            'deleted': True,
            'message': 'Delete Success'
        }
        return JsonResponse(returnData)
    except Exception as e:
        returnData = {
            'deleted': False,
            'message': str(e)
        }
        return JsonResponse(returnData)

# ---------- System Menu Name ----------     
@requiredLogin
def indexMenu(request: HttpRequest):
    menus = SystemMenu.objects.select_related()
    context = {
        "menus": menus
    }
    return render(request, "system_menu/index_menu.html", context= context)

@requiredLogin
def addMenu(request: HttpRequest):
    if request.method == "POST":
        response = HttpResponseRedirect(reverse('indexMenu'))
        try:
            menu = request.POST.get("menu")
            if not menu:
                messages.error(request, "Menu Name is required")
                return response
            app = request.POST.get("app")
            if not app:
                messages.error(request, "Menu Name is required")
                return response
            
            sysMenu = SystemMenu()
            sysMenu.name = menu
            sysMenu.app = ObjectId(app) # -- ต้องใช้ ObjectId หรือ Object ทั้ง class
            sysMenu.isActive = True
            currentUser: User = request.currentUser
            if currentUser:
                uCreate = UserSnapshot().UserToSnapshot(currentUser)
                if uCreate:
                    sysMenu.createBy = uCreate
                sysMenu.createDate = timezone.now()

            sysMenu.save()
            print(sysMenu.to_json())

            messages.success(request, 'Save Success')
        except Exception as e:
            print(e)
            messages.error(request, str(e))
        return response
    else:
        sysApp = SystemApp.objects(isActive = True)
        context = {
            "sysApp": sysApp
        }

    return render(request, "system_menu/add_menu.html",context= context)

@requiredLogin
def editMenu(request: HttpRequest, id):
    response = HttpResponseRedirect(reverse('indexMenu'))
    if request.method == "POST":
        try:
            menuId = request.POST.get("menuId")
            if not menuId:
                messages.error(request, "Not found id !")
                return response
            app = request.POST.get("app")
            if not app:
                messages.error(request, "App is required")
                return response
            appName = request.POST.get("menu")
            if not appName:
                messages.error(request, "Menu Name is required")
                return response
            
            menu = SystemMenu.objects(id = menuId).first()
            if not menu:
                messages.error(request, "Not Found Data !")
                return response
            
            menu.name = appName
            menu.app = ObjectId(app)
            currenUser: User = request.currentUser
            if currenUser:
                uUpdate = UserSnapshot().UserToSnapshot(currenUser)
                if uUpdate:
                    menu.updateBy = uUpdate
                menu.updateDate = timezone.now()
            menu.save()

            messages.success(request, 'Save Success')

        except Exception as e:
            print(e)
            messages.error(request, str(e))
        return response
    else:
        try:
            sysApp = SystemApp.objects(isActive = True)
            menu = SystemMenu.objects(id = id).first()
            if not menu:
                messages.error(request, "Not Found Data !")
                return response
            print(menu.app.name)
            context ={
                "menu":menu,
                "sysApp": sysApp
            }
            return render(request, "system_menu/edit_menu.html",context = context)

        except Exception as e:
            print(e)
            messages.error(request, str(e))
        return response

@requiredLogin
def deleteMenu(request: HttpRequest, id):
    try:
        menu = SystemMenu.objects(id = id).first()
        if not menu:
            returnData={
                'deleted': False,
                'message': 'Not Found Data'
            }
            return JsonResponse(returnData)
        menu.isActive = False
        currentUser = request.currentUser
        if currentUser:
            uDelete = UserSnapshot().UserToSnapshot(currentUser)
            if uDelete:
                menu.updateBy = uDelete
            menu.updateDate = timezone.now()
        menu.save()
        
        returnData={
            'deleted': True,
            'message': 'Deleted Success',
        }
        return JsonResponse(returnData)
    except Exception as e:
        returnData = {
            'deleted': False,
            'message': str(e)
        }
        return JsonResponse(returnData)
    
