from datetime import datetime
from typing import List
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from app_organization.models import Organization
from app_position.models import Position
from app_user.models.user import RoleUser, User, UserStatus
from base_models.basemodel import UserSnapshot

# Create your views here.
def index(request: HttpRequest):
    users = User.objects.filter(isActive = True)
    context = {
        "users": users
    }
    return render(request, 'user/index.html', context= context)

def addUser(request: HttpRequest):
    if request.method == "POST":
        response = HttpResponseRedirect(reverse('indexUser'))
        try:
            code = request.POST.get("code")
            if not code:
                messages.error(request, "Code is required")
                return response
            fNameTH = request.POST.get("fnameth")
            lNameTH = request.POST.get("lnameth")
            fNameEN = request.POST.get("fnameeng")
            if not fNameEN:
                messages.error(request, "First Name EN is required")
                return response
            lNameEN = request.POST.get("lnameeng")
            if not lNameEN:
                messages.error(request, "Last Name EN is required")
                return response
            nickName = request.POST.get("nickname")
            nation = request.POST.get("nation")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            address = request.POST.get("address")
            note = request.POST.get("note")
            birthday = request.POST.get("birthday")
            if birthday:
                birthday = datetime.strptime(birthday, "%d/%m/%Y")
            sDate = request.POST.get("sdate")
            if sDate:
                sDate = datetime.strptime(sDate, "%d/%m/%Y")
            status = request.POST.get("status")
            isadmin = True if request.POST.get("isadmin") == 'on' else False

            print(code, fNameTH, lNameTH, fNameEN, lNameEN, nickName, nation, email, phone, address, note, birthday, sDate, status, isadmin)

            posList = request.POST.getlist("pos")
            orgList = request.POST.getlist("org")

            roleData =[{"posId": pos, "orgId": org} for pos, org in zip(posList, orgList)]
            roleList: List[RoleUser] = list()
            for role in roleData:
                posId = role.get("posId")
                orgId = role.get("orgId")
                if posId and orgId:
                    pos: Position = Position.objects.get(id = posId)
                    org: Organization = Organization.objects.get(id = orgId)
                    if pos and org:
                        roleUser = RoleUser()
                        roleUser.posId = pos
                        roleUser.posNameEN = pos.nameEN
                        roleUser.orgId = org
                        roleUser.orgNameEN = org.nameEN
                        roleUser.isActive = True
                        roleUser.isDelete = False
                        roleList.append(roleUser)

            print(roleData)

            user = User()
            user.code = code
            user.fNameTH = fNameTH
            user.lNameTH = lNameTH
            user.fNameEN = fNameEN
            user.lNameEN = lNameEN
            user.nickName = nickName
            user.nation = nation
            user.email = email
            user.phone = phone
            user.address = address
            user.note = note
            user.birthDay = birthday
            user.startJobDate = sDate
            user.status = UserStatus(int(status))
            user.isAdmin = isadmin
            user.isActive = True
            user.isRegister = False
            user.roles = roleList
            currentUser: User = request.currentUser
            if currentUser:
                uCreate = UserSnapshot().UserToSnapshot(currentUser)
                if uCreate:
                    user.createBy = uCreate
            
            user.save()

            messages.success(request, 'Save Success')
            return response
        except Exception as e:
            print(e)
            messages.error(request, str(e))
            return response
    else:
        userStatus = [{"id":us.value, "name":us.name}for us in UserStatus]
        context = {
            'userStatus': userStatus
        }
        return render(request, 'user/add.html', context= context)

def AddAlienUser(request: HttpRequest):
    try:
        user = User()
        user.fNameEN = 'CHaKU'
        user.lNameEN = 'CHaKU'
        user.save()
        data = {'status': True, "mss": 'success'}
        return JsonResponse(data)
    except Exception as e:
        data = {'status': False, 'mss': str(e)}
        return JsonResponse(data)



# ---------- user settings ---------
def indexSettingUser(request: HttpRequest):
    return render(request, 'user/indexSetting.html')

