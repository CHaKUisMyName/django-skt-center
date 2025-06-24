from typing import List
from bson import ObjectId
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone

from app_position.models import Position, PositionSnapShot
from app_user.models.user import User
from base_models.basemodel import UserSnapshot

# Create your views here.
def index(request: HttpRequest):
    positions = Position.objects.filter(isActive = True, isDelete = False)
    context = {
        "positions": positions
    }
    return render(request, 'position/index.html', context= context)

def addPosition(request: HttpRequest):
    if request.method == "POST":
        response = HttpResponseRedirect(reverse('indexPosition'))
        try:
            code = request.POST.get("code")
            if not code:
                messages.error(request, "Code is required")
                return response
            nameth = request.POST.get("nameth")
            nameen = request.POST.get("nameen")
            if not nameen:
                messages.error(request, "NameEN is required")
                return response
            parent = None if request.POST.get("parent") == "none" else request.POST.get("parent")
            isactive = True if request.POST.get("isactive") == 'on' else False
            note = request.POST.get("note")
            
            position: Position = Position()
            position.code = code
            position.nameTH = nameth
            position.nameEN = nameen
            position.isActive = isactive
            position.isDelete = False
            position.parent = parent
            position.note = note
            currentUser: User = request.currentUser
            if currentUser:
                uCreate = UserSnapshot().UserToSnapshot(currentUser)
                if uCreate:
                    position.createBy = uCreate
            # print(position.to_json())
            position.save()
            
            messages.success(request, 'Save Success')
        except Exception as e:
            print(e)
            messages.error(request, str(e))
        return response
    else:
        pos: List[Position] = Position.objects.filter(isActive = True, isDelete = False)
        context = {
            "pos": pos,
        }
        return render(request, 'position/add.html', context= context)
    
def editPosition(request: HttpRequest, id: str):
    response = HttpResponseRedirect(reverse('indexPosition'))
    try:
        if request.method == "POST":
            posId = request.POST.get("posId")
            if not posId:
                messages.error(request, "Not found id !")
                return response
            position: Position = Position.objects.get(id = ObjectId(posId))
            if not position:
                messages.error(request, "Position not found")
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
            parent = None if request.POST.get("parent") == "none" else request.POST.get("parent")
            isactive = True if request.POST.get("isactive") == 'on' else False
            note = request.POST.get("note")

            snapShot = PositionSnapShot()
            snapShot.code = position.code
            snapShot.nameTH = position.nameTH
            snapShot.nameEN = position.nameEN

            position.code = code
            position.nameTH = nameth
            position.nameEN = nameen
            position.note = note
            position.isActive = isactive

            if parent:
                findParent = Position.objects.get(id = ObjectId(parent))
                if not findParent:
                    messages.error(request, "Parent not found")
                    return response

            if position.parent:
                snapShot.parentCode = position.parent.code
                snapShot.parentNameTH = position.parent.nameTH
                snapShot.parentNameEN = position.parent.nameEN
            else:
                snapShot.parentCode = None
                snapShot.parentNameTH = None
                snapShot.parentNameEN = None

            position.parent = parent

            currentUser: User = request.currentUser
            if currentUser:
                uUpdate = UserSnapshot().UserToSnapshot(currentUser)
                if uUpdate:
                    position.updateBy = uUpdate
                    snapShot.createBy = uUpdate
                position.updateDate = timezone.now()

            if not position.snapShots:
                position.snapShots = list()
            position.snapShots.append(snapShot)

            position.save()
            
            messages.success(request, 'Save Success')
            return response

        else:
            position: Position = Position.objects.get(id = id)
            if not position:
                messages.error(request, "Position not found")
                return response
            # -- filter dropdown โดยไม่่นับตัวเอง
            findParent = Position.objects.filter(isActive = True, isDelete = False, id__ne= id)
            pos = list()
            if findParent:
                pos = findParent
            context = {
                "pos": pos,
                "position": position,
                }
            return render(request, 'position/edit.html', context= context)
    except Exception as e:
        print(e)
        messages.error(request, str(e))
    return response

def deletePosition(request: HttpRequest, id: str):
    try:
        if not request.method == "GET":
            return JsonResponse({'deleted': False, 'message': 'Method not allowed'})
        if not id:
            return JsonResponse({'deleted': False, 'message': 'Not found id'})
        position: Position = Position.objects.get(id = ObjectId(id))
        if not position:
            return JsonResponse({'deleted': False, 'message': 'Position not found'})

        currentUser: User = request.currentUser
        if currentUser:
            uDelete = UserSnapshot().UserToSnapshot(currentUser)
            if uDelete:
                position.updateBy = uDelete
            position.updateDate = timezone.now()
        position.isActive = False
        position.isDelete = True
        position.save()
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