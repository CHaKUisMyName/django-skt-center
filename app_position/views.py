from typing import List
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from app_position.models import Position
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
        else:
            position: Position = Position.objects.get(id = id)
            if not position:
                messages.error(request, "Position not found")
                return response
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