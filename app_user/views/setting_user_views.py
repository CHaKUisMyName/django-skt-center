import json
from bson import ObjectId
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from app_user.models.user_setting import UserSetting
from app_user.utils import requiredLogin

@requiredLogin
def indexSettingUser(request: HttpRequest):
    userSettings = UserSetting.objects.filter(isActive = True)
    context = {
        "userSettings": userSettings
    }
    return render(request, 'setting_user/indexSetting.html', context)

# @requiredLogin
# def addSettingUser(request: HttpRequest):
#     if request.method == "POST":
#         response = HttpResponseRedirect(reverse('indexSettingUser'))
#         try:
#             # -- request.body = b'[{"emp":"...","menu":["..."],"isadmin":false}]'
#             body_unicode = request.body.decode('utf-8')# -- [{"emp":"...","menu":["..."],"isadmin":false}]
#             data = json.loads(body_unicode)  # <-- data เป็น list ของ dict
#             messages.success(request, 'Save Success')
#             return response
#         except Exception as e:
#             print(e)
#             messages.error(request, str(e))
#             return response

#     else:
#         return render(request, 'setting_user/addSetting.html')


@requiredLogin
def addSettingUser(request: HttpRequest):
    if request.method == "GET":
        # return JsonResponse({'success': False, 'data': [], 'message': 'Method not allowed'})
        return render(request, 'setting_user/addSetting.html')
    try:
        # -- request.body = b'[{"emp":"...","menu":["..."],"isadmin":false}]'
        body_unicode = request.body.decode('utf-8')# -- [{"emp":"...","menu":["..."],"isadmin":false}]
        data = json.loads(body_unicode)  # <-- data เป็น list ของ dict
        
        for us in data:
            menus = []
            for menu in us.get("menu"):
                menus.append(ObjectId(menu))

            userSetting = UserSetting()
            userSetting.user = ObjectId(us.get("emp"))
            userSetting.menus = menus
            userSetting.isAdmin = us.get("isadmin")
            userSetting.isActive = True
            # userSetting.save()
        
        return JsonResponse({'success': True, 'data': [], 'message': 'Save Success'})
    except Exception as e:
        return JsonResponse({'success': False, 'data': [], 'message': str(e)})