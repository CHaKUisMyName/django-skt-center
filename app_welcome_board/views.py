from datetime import datetime
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from app_user.utils import requiredLogin

# Create your views here.
@requiredLogin
def index(request: HttpRequest):
    return render(request, 'welcome_board/guest/index.html')

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

            return response
        except Exception as e:
            messages.error(request, str(e))
            return response
    else:
        return render(request, 'welcome_board/guest/add.html')