from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render
from app_organization.models.org_setting import OrgSetting
from app_organization.utils import isSettingOrgAdmin
from app_user.utils import requiredLogin
from django.contrib import messages



@requiredLogin
def indexSettingOrg(request: HttpRequest):
    orgSettings = OrgSetting.objects.filter(isActive = True)
    isOrgAdmin = isSettingOrgAdmin(request.currentUser.id)
    if not request.currentUser.isAdmin:
        if isOrgAdmin == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    context ={
        "orgSettings": orgSettings
    }
    return render(request, 'setting_org/indexSetting.html', context)