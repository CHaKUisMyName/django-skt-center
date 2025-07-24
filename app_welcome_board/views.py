from datetime import datetime
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from app_user.utils import requiredLogin

# Create your views here.
@requiredLogin
def index(request: HttpRequest):
    return render(request, 'welcome_board/guest/index.html')

@requiredLogin
def addGuest(request: HttpRequest):
    response = HttpResponseRedirect(reverse('indexWelcomeBoard'))
    if request.method == "POST":
        kuy = request.FILES.get("image")
        print(kuy.name)
        birthday = request.POST.get("sdate")
        if birthday:
            birthday = datetime.strptime(birthday, "%d/%m/%Y %H:%M")
            print(f"date : {birthday}")
        return response
    else:
        return render(request, 'welcome_board/guest/add.html')