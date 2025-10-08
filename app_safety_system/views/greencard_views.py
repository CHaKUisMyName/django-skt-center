from typing import List
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render

from app_user.models.user import User, UserStatus
from app_user.utils import requiredLogin

@requiredLogin
def index(request: HttpRequest):
    return render(request, 'greencard/index.html')

@requiredLogin
def getUserJson(request: HttpRequest):
    try:
        if not request.method == "GET":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        listData: List[User] = User.objects.filter(isActive = True, status = UserStatus.Hire.value).order_by('code')
        if not listData:
            return JsonResponse({'success': True, 'data': [], 'message': 'Success'})
        users = [ user.serialize() for user in listData]
        return JsonResponse({'success': True, 'data': users, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})