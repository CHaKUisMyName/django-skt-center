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
import pytz

from app_user.models.user import User
from app_user.utils import requiredLogin
from app_welcome_board.models.welcome_default import WelcomeBoardDefault
from app_welcome_board.models.welcome_guest import WelcomeBoardGuest
from app_welcome_board.models.welcomeboard import WelcomeBoardStatus
from app_welcome_board.utils import get_all_welcome_data, get_filtered_welcome_data
from base_models.basemodel import UserSnapshot

uploadDir = 'guest-img'
videoUploadDir = 'default-video'
tz = pytz.timezone("Asia/Bangkok")
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB
# -- welcome board guest URL : http://127.0.0.1:8000/wb/gs/show

# --------------------------------------------------------------------------------
# ----------------------------- welcome guest ------------------------------------
# --------------------------------------------------------------------------------
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
            if img.size > MAX_UPLOAD_SIZE:
                messages.error(request, "Image size is too large exceeds 50 MB")
                return response

            sDate = request.POST.get("sdate")
            if sDate:
                sDate = datetime.strptime(sDate, "%d/%m/%Y %H:%M")
                sDate = tz.localize(sDate)
                sDate = sDate.astimezone(pytz.utc)
                print(f"Sdate : {sDate} {sDate.tzinfo}")
            else:
                messages.error(request, "Start Job Date is required")
                return response
            
            eDate = request.POST.get("edate")
            if eDate:
                eDate = datetime.strptime(eDate, "%d/%m/%Y %H:%M")
                eDate = tz.localize(eDate)
                eDate = eDate.astimezone(pytz.utc)
                print(f"Edate : {eDate} {eDate.tzinfo}")
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
            wg.createDate = timezone.now()
            wg.save()
            broadCastWelcomeBoard()

            messages.success(request, "Add success")
            return response
        except Exception as e:
            messages.error(request, str(e))
            return response
    else:
        return render(request, 'welcome_board/guest/add.html')
    
@requiredLogin
def editGuest(request: HttpRequest, id: str):
    response = HttpResponseRedirect(reverse('indexWelcomeBoard'))
    
    if request.method == "POST":
        try:
            wgid = request.POST.get("wgid")
            if not wgid:
                messages.error(request, "id is required")
                return response
            wg: WelcomeBoardGuest = WelcomeBoardGuest.objects.filter(id = ObjectId(wgid)).first()
            if not wg:
                messages.error(request, "Guest not found")
                return response
            img = request.FILES.get("image")
            if not img:
                messages.error(request, "Image is required")
                return response
            print(img.name)
            if img.size > MAX_UPLOAD_SIZE:
                messages.error(request, "Image size is too large exceeds 50 MB")
                return response
            sDate = request.POST.get("sdate")
            if sDate:
                sDate = datetime.strptime(sDate, "%d/%m/%Y %H:%M")
                sDate = tz.localize(sDate)
                sDate = sDate.astimezone(pytz.utc)
                print(f"date : {sDate}")
            else:
                messages.error(request, "Start Job Date is required")
                return response
            
            eDate = request.POST.get("edate")
            if eDate:
                eDate = datetime.strptime(eDate, "%d/%m/%Y %H:%M")
                eDate = tz.localize(eDate)
                eDate = eDate.astimezone(pytz.utc)
                print(f"date : {eDate}")
            else:
                messages.error(request, "End Job Date is required")
                return response
            if sDate >= eDate:
                messages.error(request, 'Start date must be before end date.')
                return response
            
            wg.title = request.POST.get('title') if request.POST.get("title") else wg.title
            wg.note = request.POST.get("note") if request.POST.get("note") else wg.note
            wg.sDate = sDate
            wg.eDate = eDate
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, uploadDir))
            fs.delete(os.path.join(settings.MEDIA_ROOT, wg.path))# -- delete old image
            filename = fs.save(img.name, img)  # จะเก็บไฟล์และ return filename
            file_path = os.path.join(uploadDir, filename)  # เช่น welcome_board/xxx.jpg
            if not file_path:
                messages.error(request, "Upload failed")
                return response
            wg.path = file_path
            currentUser: User = request.currentUser
            if currentUser:
                uUpdate= UserSnapshot().UserToSnapshot(currentUser)
                if uUpdate:
                    wg.updateBy = uUpdate
            wg.updateDate = timezone.now()
            wg.status = WelcomeBoardStatus(int(1))
            wg.save()
            broadCastWelcomeBoard()

            messages.success(request, "Update success")
            return response
        except Exception as e:
            messages.error(request, str(e))
            return response
    else:
        if not id:
            messages.error(request, "Id is required")
            return response
        wg: WelcomeBoardGuest = WelcomeBoardGuest.objects.filter(id= ObjectId(id)).first()
        if not wg:
            messages.error(request, "Guest not found")
            return response
        context = {
            'guest': wg,
            # 'imgPath': os.path.join(settings.MEDIA_ROOT, wg.path),
            'imgPath': wg.path,
            'mediaRoot': settings.MEDIA_URL,
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
    
# --------------------------------------------------------------------------------
# ----------------------------- welcome default ----------------------------------
# --------------------------------------------------------------------------------

@requiredLogin
def addDefault(request: HttpRequest):
    response = HttpResponseRedirect(reverse('addDefaultWelcomeBoard'))
    if request.method == "POST":
        try:
            inputVideo = request.FILES.get("inputVideo")
            if not inputVideo:
                messages.error(request, "Video is required")
                return response
            if inputVideo.size > MAX_UPLOAD_SIZE:
                messages.error(request, "Video size is too large exceeds 50 MB")
                return response
            print(inputVideo.name)
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, videoUploadDir))
            oldWd: WelcomeBoardDefault = WelcomeBoardDefault.objects.filter(isActive=True).first()
            if oldWd:
                fs.delete(os.path.join(settings.MEDIA_ROOT, oldWd.path))# -- delete old image
                oldWd.delete()
            fileName = fs.save(inputVideo.name, inputVideo)
            file_path = os.path.join(videoUploadDir, fileName)
            if not file_path:
                messages.error(request, "Upload failed")
                return response
            wd = WelcomeBoardDefault()
            wd.path = file_path
            wd.isActive = True
            currentUser: User = request.currentUser
            if currentUser:
                uCreate = UserSnapshot().UserToSnapshot(currentUser)
                if uCreate:
                    wd.createBy = uCreate
            wd.createDate = timezone.now()
            wd.save()
            messages.success(request, "Add success")
            return response
        except Exception as e:
            messages.error(request, str(e))
            return response
    else:
        return render(request, 'welcome_board/default/add.html')

# --------------------------------------------------------------------------------
# -------------------------------- welcome show ----------------------------------
# --------------------------------------------------------------------------------

def showWelcomeBoard(request: HttpRequest):
    broadCastWelcomeBoard()
    return render(request, 'welcome_board/show.html')


channel_layer = get_channel_layer()

def broadCastWelcomeBoard():
    async def send_message():
        data = await get_filtered_welcome_data()
        await channel_layer.group_send(
            "filtered_guests",
            {
                "type": "send_welcome_board",
                "media_type": data["media_type"],
                "path": data["path"],
            }
        )
    async_to_sync(send_message)()

def broadCastAllGuests():
    async def send_message():
        data = await get_all_welcome_data()
        await channel_layer.group_send(
            "all_guests",
            {
                "type": "send_welcome_board",
                "media_type": data["media_type"],
                "path": data["path"],
            }
        )
    async_to_sync(send_message)()