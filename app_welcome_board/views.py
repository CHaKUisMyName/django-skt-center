from datetime import datetime
from django.utils import timezone
import os
from pathlib import Path
from typing import List
from bson import ObjectId
from django.conf import settings
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from app_user.models.user import User
from app_user.utils import requiredLogin
from app_welcome_board.models.welcome_guest import WelcomeBoardGuest
from app_welcome_board.models.welcomeboard import WelcomeBoardStatus
from base_models.basemodel import UserSnapshot

uploadDir = 'guest-img'

# Create your views here.
@requiredLogin
def index(request: HttpRequest):
    welcomeGuests = WelcomeBoardGuest.objects.filter(isActive=True)
    context = {
        'welcomeGuests': welcomeGuests,
        'mediaRoot': settings.MEDIA_URL,
    }
    return render(request, 'welcome_board/guest/index.html',context = context)

@requiredLogin
def addGuest(request: HttpRequest):
    response = HttpResponseRedirect(reverse('indexWelcomeBoard'))
    if request.method == "POST":
        try:
            img = request.FILES.get("image")
            if not img:
                messages.error(request, "Image is required")
                return response
            print(img.name)

            sDate = request.POST.get("sdate")
            if sDate:
                sDate = datetime.strptime(sDate, "%d/%m/%Y %H:%M")
                print(f"date : {sDate}")
            else:
                messages.error(request, "Start Job Date is required")
                return response
            
            eDate = request.POST.get("edate")
            if eDate:
                eDate = datetime.strptime(eDate, "%d/%m/%Y %H:%M")
                print(f"date : {eDate}")
            else:
                messages.error(request, "End Job Date is required")
                return response
            title = request.POST.get("title")
            note = request.POST.get("note")


            print(f"sdate: {sDate}, edate: {eDate}")
            print(f"if : {sDate >= eDate}")
            if sDate >= eDate:
                messages.error(request, 'Start date must be before end date.')
                return response
            
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, uploadDir))
            filename = fs.save(img.name, img)  # จะเก็บไฟล์และ return filename
            file_path = os.path.join(uploadDir, filename)  # เช่น welcome_board/xxx.jpg
            if not file_path:
                messages.error(request, "Upload failed")
                return response
            
            wg = WelcomeBoardGuest()
            wg.title = title
            wg.path = file_path
            wg.sDate = sDate
            wg.eDate = eDate
            wg.isActive = True
            wg.status = WelcomeBoardStatus(int(1))
            wg.note = note

            currentUser: User = request.currentUser
            if currentUser:
                uCreate = UserSnapshot().UserToSnapshot(currentUser)
                if uCreate:
                    wg.createBy = uCreate
            wg.save()
            broadCastWelcomeBoard()

            messages.success(request, "Upload success")
            return response
        except Exception as e:
            messages.error(request, str(e))
            return response
    else:
        print(f"{Path(__file__).home()}/desktop/chaku-folder/skt-media")
        return render(request, 'welcome_board/guest/add.html')
    

@requiredLogin
def editGuest(request: HttpRequest, id: str):
    response = HttpResponseRedirect(reverse('indexWelcomeBoard'))
    if not id:
        messages.error(request, "Id is required")
        return response
    wg: WelcomeBoardGuest = WelcomeBoardGuest.objects.filter(id= ObjectId(id)).first()
    if not wg:
        messages.error(request, "Guest not found")
        return response
    if request.method == "POST":
        try:
            pass
        except Exception as e:
            messages.error(request, str(e))
            return response
    else:
        context = {
            'guest': wg
        }
        return render(request, 'welcome_board/guest/edit.html',context= context)
    
@requiredLogin
def deleteGuest(request: HttpRequest, id: str):
    try:
        if not request.method == "GET":
            return JsonResponse({'deleted': False, 'message': 'Method not allowed'})
        if not id:
            return JsonResponse({'deleted': False, 'message': 'Not found id'})
        wg: WelcomeBoardGuest = WelcomeBoardGuest.objects.filter(id = ObjectId(id)).first()
        if not wg:
            return JsonResponse({'deleted': False, 'message': 'Guest not found'})
        # currentUser: User = request.currentUser
        # if currentUser:
        #     uDelete = UserSnapshot().UserToSnapshot(currentUser)
        #     if uDelete:
        #         wg.updateBy = uDelete
        #     wg.updateDate = timezone.now()
        # wg.isActive = False
        # wg.save()

        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, uploadDir))
        fs.delete(os.path.join(settings.MEDIA_ROOT, wg.path))
        wg.delete()
        
        broadCastWelcomeBoard()
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
    
def showWelcomeBoard(request: HttpRequest):
    broadCastWelcomeBoard()
    return render(request, 'welcome_board/show.html')

def broadCastWelcomeBoard():
    # now = datetime.now()
    channel_layer = get_channel_layer()
    welcome: List[WelcomeBoardGuest] = WelcomeBoardGuest.objects.filter(isActive=True)
    print(len(welcome))
    if welcome:
        wg = [ w.serialize() for w in welcome]
        payload = {
            "type": "send_welcome_board",
            "path": wg,
            "media_type": "image"
        }
    else:
        payload = {
            "type": "send_welcome_board",
            "path": [{"path":"guest-img/senikame-2.jpg"}],
            "media_type": "video"
        }
    async_to_sync(channel_layer.group_send)(
        "welcome_board",
        payload
    )