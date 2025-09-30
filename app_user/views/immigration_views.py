from django.http import HttpRequest
from django.shortcuts import render

from app_user.models.user import User
from app_user.utils import requiredLogin

@requiredLogin
def index(request: HttpRequest):
    users: User = User.objects.filter(isActive = True).order_by('code')
    context = {
        "users": users
    }
    return render(request, 'immigration/index.html', context)