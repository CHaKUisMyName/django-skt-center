from django.http import HttpRequest
from django.shortcuts import render

# Create your views here.
def index(request: HttpRequest):
    return render(request, 'position/index.html')

def add(request: HttpRequest):
    return render(request, 'position/add.html')