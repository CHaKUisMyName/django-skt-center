from django.http import HttpRequest
from django.shortcuts import render

from app_user.utils import requiredLogin

@requiredLogin
def index(request: HttpRequest):
    return render(request, 'sds/index.html')