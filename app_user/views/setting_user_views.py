from django.http import HttpRequest
from django.shortcuts import render

from app_user.utils import requiredLogin

@requiredLogin
def indexSettingUser(request: HttpRequest):
    return render(request, 'setting_user/indexSetting.html')

