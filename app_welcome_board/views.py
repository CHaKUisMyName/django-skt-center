from datetime import datetime
import os
from pathlib import Path
from django.conf import settings
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage

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
            isactive = True if request.POST.get("isactive") == 'on' else False
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
            wg.isActive = isactive
            wg.status = WelcomeBoardStatus(int(1))
            wg.note = note

            currentUser: User = request.currentUser
            if currentUser:
                uCreate = UserSnapshot().UserToSnapshot(currentUser)
                if uCreate:
                    wg.createBy = uCreate
            wg.save()

            messages.success(request, "Upload success")
            return response
        except Exception as e:
            messages.error(request, str(e))
            return response
    else:
        print(f"{Path(__file__).home()}/desktop/chaku-folder/skt-media")
        return render(request, 'welcome_board/guest/add.html')