from django.http import HttpRequest
from django.shortcuts import render

# Create your views here.
def index(request: HttpRequest):
    return render(request,'visitor/index.html')

def listVisitor(reuqest: HttpRequest):
    return render(reuqest,'visitor/list.html')

def addVisitor(request: HttpRequest):
    return render(request,'visitor/add.html')
# ---------------------------- option zone ----------------------------
def listOption(request: HttpRequest):
    return render(request,'visitor/list_option.html')

def addOption(request: HttpRequest):
    return render(request,'visitor/add_option.html')

# ---------------------------- room zone ----------------------------
def listRoom(request: HttpRequest):
    return render(request,'visitor/list_room.html')

def addRoom(request: HttpRequest):
    return render(request,'visitor/add_room.html')