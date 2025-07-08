from django.http import HttpRequest
from django.shortcuts import render

from app_user.utils import requiredLogin

# Create your views here.
@requiredLogin
def index(request: HttpRequest):
    return render(request, 'dashboard/index.html')