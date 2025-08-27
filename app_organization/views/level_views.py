from typing import List
from django.utils import timezone
from bson import ObjectId
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from app_organization.models.level import Level, LevelSnapShot
from app_organization.utils import HasOrgPermission
from app_user.models.user import User
from app_user.utils import requiredLogin
from base_models.basemodel import UserSnapshot


@requiredLogin
def index(request: HttpRequest):
    levels = Level.objects.filter(isDelete = False)
    isOrgAdmin = HasOrgPermission(str(request.currentUser.id), True)
    canModify = HasOrgPermission(str(request.currentUser.id))
    context = {
        "levels": levels,
        "isOrgAdmin": isOrgAdmin,
        "canModify": canModify,
    }
    return render(request, 'level/index.html', context= context)

@requiredLogin
def addLevel(request: HttpRequest):
    if request.method == "POST":
        response = HttpResponseRedirect(reverse('indexLevel'))
        try:
            hasPermission = HasOrgPermission(str(request.currentUser.id))
            if not request.currentUser.isAdmin:
                if hasPermission == False:
                    messages.error(request, "Not Permission")
                    return response
            code = request.POST.get("code")
            if not code:
                messages.error(request, "Code is required")
                return response
            nameth = request.POST.get("nameth")
            nameen = request.POST.get("nameen")
            if not nameen:
                messages.error(request, "NameEN is required")
                return response
            parent = None if request.POST.get("parent") == "none" else ObjectId(request.POST.get("parent"))
            isactive = True if request.POST.get("isactive") == 'on' else False
            note = request.POST.get("note")

            level = Level()
            level.code = code
            level.nameTH = nameth
            level.nameEN = nameen
            level.isActive = isactive
            level.isDelete = False
            level.note = note
            level.parent = ObjectId(parent) if parent else None
            currentUser: User = request.currentUser
            if currentUser:
                uCreate = UserSnapshot().UserToSnapshot(currentUser)
                if uCreate:
                    level.createBy = uCreate
            level.save()
            
            messages.success(request, 'Save Success')
        except Exception as e:
            print(e)
            messages.error(request, str(e))
        return response
    else:
        findParent = Level.objects.filter(isActive = True, isDelete = False)
        parents: Level = list()
        if findParent:
            parents = findParent
        context = {
            "parents": parents
        }
        return render(request, 'level/add.html', context= context)

@requiredLogin
def editLevel(request: HttpRequest, id: str):
    response = HttpResponseRedirect(reverse('indexLevel'))
    try:
        hasPermission = HasOrgPermission(str(request.currentUser.id))
        if not request.currentUser.isAdmin:
            if hasPermission == False:
                messages.error(request, "Not Permission")
                return response
        if request.method == "POST":
            lvId = request.POST.get("lvId")
            if not lvId:
                messages.error(request, "Not found id !")
                return response
            level: Level = Level.objects.get(id = ObjectId(lvId))
            if not level:
                messages.error(request, "Level not found")
                return response
            code = request.POST.get("code")
            if not code:
                messages.error(request, "Code is required")
                return response
            nameth = request.POST.get("nameth")
            nameen = request.POST.get("nameen")
            if not nameen:
                messages.error(request, "NameEN is required")
                return response
            
            parent = None if request.POST.get("parent") == "none" else ObjectId(request.POST.get("parent"))
            isactive = True if request.POST.get("isactive") == 'on' else False
            note = request.POST.get("note")

            snapShot = LevelSnapShot()
            snapShot.code = level.code
            snapShot.nameTH = level.nameTH
            snapShot.nameEN = level.nameEN

            level.code = code
            level.nameTH = nameth
            level.nameEN = nameen
            level.note = note
            level.isActive = isactive

            if parent:
                findParent = Level.objects.get(id = ObjectId(parent))
                if not findParent:
                    messages.error(request, "Parent not found")
                    return response

            if level.parent:
                snapShot.parentCode = level.parent.code
                snapShot.parentNameTH = level.parent.nameTH
                snapShot.parentNameEN = level.parent.nameEN
            else:
                snapShot.parentCode = None
                snapShot.parentNameTH = None
                snapShot.parentNameEN = None

            level.parent = ObjectId(parent) if parent else None

            currentUser: User = request.currentUser
            if currentUser:
                uUpdate = UserSnapshot().UserToSnapshot(currentUser)
                if uUpdate:
                    level.updateBy = uUpdate
                    snapShot.createBy = uUpdate
                level.updateDate = timezone.now()

            if not level.snapShots:
                level.snapShots = list()
            level.snapShots.append(snapShot)
            
            level.save()
            
            messages.success(request, 'Save Success')
            return response

        else:
            level: Level = Level.objects.get(id = ObjectId(id))
            if not level:
                messages.error(request, "Level not found")
                return response
            # -- filter dropdown โดยไม่่นับตัวเอง
            findParent = Level.objects.filter(isActive = True, isDelete = False, id__ne= ObjectId(id))
            parents = list()
            if findParent:
                parents = findParent
            context = {
                "parents": parents,
                "level": level,
                }
            return render(request, 'level/edit.html', context= context)
    except Exception as e:
        print(e)
        messages.error(request, str(e))
    return response

@requiredLogin
def deleteLevel(request: HttpRequest, id: str):
    try:
        if not request.method == "GET":
            return JsonResponse({'deleted': False, 'message': 'Method not allowed'})
        if not id:
            return JsonResponse({'deleted': False, 'message': 'Not found id'})
        hasPermission = HasOrgPermission(str(request.currentUser.id))
        if not request.currentUser.isAdmin:
            if hasPermission == False:
                return JsonResponse({'deleted': False, 'message': 'Not Permission'})
        level: Level = Level.objects.get(id = ObjectId(id))
        if not level:
            return JsonResponse({'deleted': False, 'message': 'Level not found'})

        currentUser: User = request.currentUser
        if currentUser:
            uDelete = UserSnapshot().UserToSnapshot(currentUser)
            if uDelete:
                level.updateBy = uDelete
            level.updateDate = timezone.now()
        level.isActive = False
        level.isDelete = True
        level.save()
        returnData = {
            'deleted': True,
            'message': 'Delete success'
        }
        return JsonResponse(returnData)
    except Exception as e:
        returnData = {
            'deleted': False,
            'message': str(e)
        }
        return JsonResponse(returnData)