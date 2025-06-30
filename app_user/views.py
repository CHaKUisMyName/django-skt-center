from datetime import datetime
import json
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
    # users = User.objects.all()
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
            if isDuplicateRoles(roleList):
                messages.error(request, "Duplicate Roles")
                return response
            
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

def editUser(request: HttpRequest, id: str):
    response = HttpResponseRedirect(reverse('indexUser'))
    try:
        if request.method == "POST":
            usId = request.POST.get("usid")
            if not usId:
                messages.error(request, "Not found id !")
                return response
            user: User = User.objects.get(id = usId)
            if not user:
                messages.error(request, "User not found")
                return response
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
            birthday = request.POST.get("birthday")
            print(f"""bd : {birthday}""")
            if birthday:
                birthday = datetime.strptime(birthday, "%d/%m/%Y")
            sDate = request.POST.get("sdate")
            print(f"""sd : {sDate}""")
            if sDate:
                sDate = datetime.strptime(sDate, "%d/%m/%Y")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            address = request.POST.get("address")
            note = request.POST.get("note")
            status = request.POST.get("status")
            isadmin = True if request.POST.get("isadmin") == 'on' else False
            
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
            if isDuplicateRoles(roleList):
                messages.error(request, "Duplicate Roles")
                return response
            
            updateUserRoles(user, roleList)
            user.save()
            # print(json.dumps([role.serialize() for role in user.roles], ensure_ascii=False))
        else:
            user = User.objects.get(id = id)
            if not user:
                messages.error(request, "User not found")
                return response
            userStatus = [{"id":us.value, "name":us.name}for us in UserStatus]
            userRolesJson = json.dumps([role.serialize() for role in user.roles], ensure_ascii=False)
            context = {
                'userStatus': userStatus,
                'user': user,
                "userRolesJson": userRolesJson,
            }
            return render(request, 'user/edit.html', context= context)
    except Exception as e:
        print(e)
        messages.error(request, str(e))
    return response

def isDuplicateRoles(roles: List[RoleUser]):
    # -- set to keep track of elements that have been seen
    seen = set()
    # -- list to store duplicates found in the input list
    duplicates = []
    for r in roles:
        key = (str(r.posId.id), str(r.orgId.id))
        if key in seen:
            duplicates.append(key)
        else:
            seen.add(key)
    return True if len(duplicates) > 0 else False


def updateUserRoles(user: User, new_roles: list[RoleUser]):
    # map ของของเก่า: key = (posId, orgId)
    old_map = {
        (str(r.posId.id), str(r.orgId.id)): r
        for r in user.roles
        if r.isActive and not r.isDelete
    }
    print(f"""old map : {old_map}""")

    new_keys = set((str(r.posId.id), str(r.orgId.id)) for r in new_roles)

    updated_roles = []

    # 1. เพิ่ม/แทนที่ของใหม่
    for r in new_roles:
        key = (str(r.posId.id), str(r.orgId.id))
        updated_roles.append(RoleUser(
            posId=r.posId,
            posNameEN=r.posNameEN,
            orgId=r.orgId,
            orgNameEN=r.orgNameEN,
            isActive=True,
            isDelete=False,
            note=r.note
        ))

    # 2. เปลี่ยนสถานะของเก่าที่ยังมีอยู่แต่หายไปในของใหม่
    for key, old in old_map.items():
        if key not in new_keys:
            updated_roles.append(RoleUser(
                posId=old.posId,
                posNameEN=old.posNameEN,
                orgId=old.orgId,
                orgNameEN=old.orgNameEN,
                isActive=False,
                isDelete=True,
                note=old.note
            ))

    user.roles = updated_roles


# ---------- user settings ---------
def indexSettingUser(request: HttpRequest):
    return render(request, 'user/indexSetting.html')

