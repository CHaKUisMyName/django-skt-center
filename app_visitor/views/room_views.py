from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from app_user.models.user import User
from app_user.utils import requiredLogin
from app_visitor.models.room import Room
from app_visitor.utils import HasVstPermission
from base_models.basemodel import UserSnapshot


@requiredLogin
def index(request: HttpRequest):
    rooms: Room = Room.objects.filter(isActive = True)
    hasPermission = HasVstPermission(str(request.currentUser.id), "Room")
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    context = {
        "rooms": rooms,
    }
    return render(request,'room/index.html', context)

@requiredLogin
def add(request: HttpRequest):
    hasPermission = HasVstPermission(str(request.currentUser.id), "Room")
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    if request.method == "POST":
        response = HttpResponseRedirect(reverse('indexRoom'))
        try:
            name = request.POST.get('name')
            if not name:
                messages.error(request, "Name is required")
                return response
            note = request.POST.get('note')

            room: Room = Room()
            room.name = name
            room.note = note
            room.isActive = True
            currentUser: User = request.currentUser
            if currentUser:
                uCreate = UserSnapshot().UserToSnapshot(currentUser)
                if uCreate:
                    room.createBy = uCreate
            room.save()
            messages.success(request, 'Save Success')
        except Exception as e:
            print(e)
            messages.error(request, str(e))
        return response
    else:
        return render(request,'room/add.html')
    
@requiredLogin
def edit(request: HttpRequest, id: str):
    hasPermission = HasVstPermission(str(request.currentUser.id), "Room")
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    response = HttpResponseRedirect(reverse('indexRoom'))
    if request.method == "POST":
        try:
            roomId = request.POST.get('roomId')
            if not roomId:
                messages.error(request, "Not found id")
                return response
            name = request.POST.get('name')
            if not name:
                messages.error(request, "Room Name is required")
                return response
            note = request.POST.get('note')
            room: Room = Room.objects.filter(id = roomId).first()
            if not room:
                messages.error(request, "Room not found")
                return response
            room.name = name
            room.note = note
            room.updateDate = timezone.now()
            currentUser: User = request.currentUser
            if currentUser:
                uUpdate = UserSnapshot().UserToSnapshot(currentUser)
                if uUpdate:
                    room.updateBy = uUpdate
            room.save()
            messages.success(request, 'Save Success')
        except Exception as e:
            print(e)
            messages.error(request, str(e))
        return response
    else:
        if not id:
            messages.error(request, "Not found id")
            return response
        room: Room = Room.objects.filter(id = id).first()
        if not room:
            messages.error(request, "Room not found")
            return response
        context = {
            "room": room,
        }
        return render(request,'room/edit.html', context)

@requiredLogin
def delete(request: HttpRequest, id: str):
    try:
        if not request.method == "GET":
            return JsonResponse({'deleted': False, 'message': 'Method not allowed'})
        hasPermission = HasVstPermission(str(request.currentUser.id), "Room")
        if not request.currentUser.isAdmin:
            if hasPermission == False:
                messages.error(request, "Not Permission")
                return JsonResponse({'deleted': False, 'message': 'Not Permission'})
        if not id:
            return JsonResponse({'deleted': False, 'message': 'Not found id'})
        room: Room = Room.objects.filter(id = id).first()
        if not room:
            return JsonResponse({'deleted': False, 'message': 'Room not found'})
        room.isActive = False
        room.updateDate = timezone.now()
        currentUser: User = request.currentUser
        if currentUser:
            uDelete = UserSnapshot().UserToSnapshot(currentUser)
            if uDelete:
                room.updateBy = uDelete
        room.save()
        r = {
            'deleted': True,
            'message': 'Delete success'
        }
        return JsonResponse(r)
    except Exception as e:
        r = {
            'deleted': False,
            'message': str(e)
        }
        return JsonResponse(r)