from datetime import datetime
import json
import secrets
from typing import List
from bson import ObjectId
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone

from app_organization.models.organization import Organization
from app_organization.models.position import Position
from app_user.models.auth_session import AuthSession
from app_user.models.auth_user import AuthUser, VerifyPassword
from app_user.models.user import RoleUser, User, UserStatus
from app_user.models.user_setting import UserSetting
from app_user.utils import isSettingUserAdmin, requiredLogin
from base_models.basemodel import UserSnapshot

# Create your views here.
@requiredLogin
def index(request: HttpRequest):
    users = User.objects.filter(isActive = True)
    isUserAdmin = isSettingUserAdmin(request.currentUser.id)
    context = {
        "users": users,
        "isUserAdmin": isUserAdmin
    }
    return render(request, 'user/index.html', context= context)

@requiredLogin
def addUser(request: HttpRequest):
    if request.method == "POST":
        response = HttpResponseRedirect(reverse('indexUser'))
        try:
            isUserAdmin = isSettingUserAdmin(request.currentUser.id)
            if not request.currentUser.isAdmin or isUserAdmin == False:
                messages.error(request, "Not Permission")
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
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            address = request.POST.get("address")
            note = request.POST.get("note")
            birthday = request.POST.get("birthday")
            if birthday:
                birthday = datetime.strptime(birthday, "%d/%m/%Y")
            else:
                birthday = None
            sDate = request.POST.get("sdate")
            if not sDate:
                messages.error(request, "Start Job Date is required")
                return response
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
            user.isDelete = False
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
            'userStatus': userStatus,
        }
        return render(request, 'user/add.html', context= context)

def AddAlienUser(request: HttpRequest):
    try:
        user = User()
        user.fNameEN = 'CHaKU'
        user.lNameEN = 'CHaKU'
        user.isAdmin = True
        user.isActive = True
        user.isRegister = True
        user.isDelete = False
        user.save()

        authUser = AuthUser()
        authUser.refUser = user
        authUser.userAuth = 'admin'
        authUser.hashPassword("1234")
        authUser.isActive = True
        authUser.isDelete = False
        authUser.save()

        data = {'status': True, "mss": 'success'}
        return JsonResponse(data)
    except Exception as e:
        data = {'status': False, 'mss': str(e)}
        return JsonResponse(data)

@requiredLogin
def editUser(request: HttpRequest, id: str):
    response = HttpResponseRedirect(reverse('indexUser'))
    try:
        isUserAdmin = isSettingUserAdmin(request.currentUser.id)
        if request.method == "POST":
            
            usId = request.POST.get("usid")
            if not usId:
                messages.error(request, "Not found id !")
                return response
            if ObjectId(request.currentUser.id) != ObjectId(usId):
                if not request.currentUser.isAdmin or isUserAdmin == False:
                    messages.error(request, "Not Permission")
                    return response
            user: User = User.objects.filter(id = usId).first()
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
            if birthday:
                birthday = datetime.strptime(birthday, "%d/%m/%Y")
            else:
                birthday = None
            sDate = request.POST.get("sdate")
            if not sDate:
                messages.error(request, "Start Job Date is required")
                return response
            
            sDate = datetime.strptime(sDate, "%d/%m/%Y")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            address = request.POST.get("address")
            note = request.POST.get("note")
            status = request.POST.get("status") if request.POST.get("status") else user.status.value
            isadmin = True if request.POST.get("isadmin") == 'on' else False

            # -- update data
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
            currentUser: User = request.currentUser
            if currentUser:
                uUpdate = UserSnapshot().UserToSnapshot(currentUser)
                if uUpdate:
                    user.updateBy = uUpdate
            
            posList = request.POST.getlist("pos")
            orgList = request.POST.getlist("org")
            if len(posList) > 0 and len(orgList) > 0:
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
                            roleUser.createDate = timezone.now()
                            roleList.append(roleUser)
                if isDuplicateRoles(roleList):
                    messages.error(request, "Duplicate Roles")
                    return response
                if is_same_roles(user.roles, roleList) == False:
                    updateUserRoles(user, roleList)

            # print(json.dumps([role.serialize() for role in user.roles], ensure_ascii=False))
            # print(user.to_json())
            
            user.save()

            authUser: AuthUser = AuthUser.objects.filter(refUser = user.id).first()
            if authUser:
                if UserStatus(int(status)) != UserStatus.Hire:
                    authUser.isActive = False
                    authUser.save()

            messages.success(request, 'Save Success')
            return response
        else:
            if not id:
                messages.error(request, "Not found id !")
                return response
            if ObjectId(request.currentUser.id) != ObjectId(id):
                if not request.currentUser.isAdmin or isUserAdmin == False:
                    messages.error(request, "Not Permission")
                    return response
            user = User.objects.filter(id = id).first()
            if not user:
                messages.error(request, "User not found")
                return response
            userStatus = [{"id":us.value, "name":us.name}for us in UserStatus]
            userRolesJson = json.dumps([role.serialize() for role in user.roles], ensure_ascii=False)
            context = {
                'userStatus': userStatus,
                'user': user,
                "userRolesJson": userRolesJson,
                "isUserAdmin": isUserAdmin,
            }
            return render(request, 'user/edit.html', context= context)
    except Exception as e:
        print(e)
        messages.error(request, str(e))
    return response

# -- check ว่ามีการแก้ไข role มาหรือไม่
def is_same_roles(old_roles: list[RoleUser], new_roles: list[RoleUser]) -> bool:
    def to_key_set(roles):
        return set(
            (str(r.posId.id), str(r.orgId.id), r.isActive, r.isDelete)
            for r in roles
            if r.isActive and not r.isDelete
        )
    
    return to_key_set(old_roles) == to_key_set(new_roles)

# -- check ว่ามีการเลือก role ซ้ำกันเองหรือไม่
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
    # Map ของ role เดิมทั้งหมด
    old_map = {
        (str(r.posId.id), str(r.orgId.id), r.isActive, r.isDelete): r
        for r in user.roles
    }

    # Key ใหม่ (เฉพาะที่ active)
    new_keys = set((str(r.posId.id), str(r.orgId.id), True, False) for r in new_roles)

    updated_roles = []

    for r in new_roles:
        key_active = (str(r.posId.id), str(r.orgId.id), True, False)
        key_removed = (str(r.posId.id), str(r.orgId.id), False, True)

        if key_active in old_map:
            # ✅ ยังมีอยู่แบบ active → reuse ได้เลย
            updated_roles.append(old_map[key_active])

        elif key_removed in old_map:
            # ✅ เคยถูกลบ → snapshot เก่า แล้วเพิ่มใหม่ (ใหม่จริง → ไม่ reuse เดิมเลย)
            old = old_map[key_removed]
            now = timezone.now()

            # 🔸 1. snapshot เก่าซ้ำอีกครั้ง
            snapshot = RoleUser(
                posId=old.posId,
                posNameEN=old.posNameEN,
                orgId=old.orgId,
                orgNameEN=old.orgNameEN,
                isActive=False,
                isDelete=True,
                note=old.note,
                createDate=old.createDate,
                updateDate=old.updateDate if old.updateDate else now,
                # updateDate=now
            )
            updated_roles.append(snapshot)

            # 🔹 2. เพิ่มใหม่ (ไม่ reuse, createDate ใหม่แน่นอน)
            new_role = RoleUser(
                posId=r.posId,
                posNameEN=r.posNameEN,
                orgId=r.orgId,
                orgNameEN=r.orgNameEN,
                isActive=True,
                isDelete=False,
                note=r.note,
                createDate=now  # ✅ ใหม่ทุกครั้ง
            )
            updated_roles.append(new_role)

        else:
            # ✅ ใหม่จริง → createDate ใหม่
            new_role = RoleUser(
                posId=r.posId,
                posNameEN=r.posNameEN,
                orgId=r.orgId,
                orgNameEN=r.orgNameEN,
                isActive=True,
                isDelete=False,
                note=r.note,
                createDate=timezone.now()
            )
            updated_roles.append(new_role)

    # 3. role เดิมที่หายไปจาก new_roles → ถือว่าถูกลบ → snapshot ทิ้ง
    for key, old in old_map.items():
        base_key = (str(old.posId.id), str(old.orgId.id), True, False)
        if base_key not in new_keys:
            removed = RoleUser(
                posId=old.posId,
                posNameEN=old.posNameEN,
                orgId=old.orgId,
                orgNameEN=old.orgNameEN,
                isActive=False,
                isDelete=True,
                note=old.note,
                createDate=old.createDate,
                updateDate=timezone.now()
            )
            updated_roles.append(removed)

    user.roles = updated_roles

@requiredLogin
def deleteUser(request: HttpRequest, id: str):
    try:
        isUserAdmin = isSettingUserAdmin(request.currentUser.id)
        if not request.method == "GET":
            return JsonResponse({'deleted': False, 'message': 'Method not allowed'})
        if not id:
            return JsonResponse({'deleted': False, 'message': 'Not found id'})
        if not request.currentUser.isAdmin or isUserAdmin == False:
            return JsonResponse({'deleted': False, 'message': 'Not Permission'})
        
        user: User = User.objects.filter(id = id).first()
        if not user:
            return JsonResponse({'deleted': False, 'message': 'User not found'})
        
        user.isDelete = True
        user.isActive = False
        user.save()

        authUser: AuthUser = AuthUser.objects.filter(refUser = user).first()
        if authUser:
            authUser.isDelete = True
            authUser.isActive = False
            authUser.save()

        authSession: List[AuthSession] = AuthSession.objects.all()
        if authSession:
            for authSS in authSession:
                data = authSS.GetSessionData()
                if str(data["userId"]) == str(user.id):
                    authSS.delete()
        
        return JsonResponse({'deleted': True, 'message': 'Delete success'})
    except Exception as e:
        return JsonResponse({'deleted': False, 'message': str(e)})
    
@requiredLogin
def listUser(request: HttpRequest):
    if not request.method == "GET":
        return JsonResponse({'success': False, 'data': [], 'message': 'Method not allowed'})
    try:
        isActive_str = request.GET.get("isactive")
        isactive = bool(isActive_str)
        users: List[User] = User.objects.all() if isactive is None else User.objects.filter(isActive = isactive)
        return JsonResponse({'success': True, 'data': [ user.serialize() for user in users], 'message': 'Success'})
    except Exception as e:
        return JsonResponse({'success': False, 'data': [], 'message': str(e)})
    
# ---------------------------------------------------------------------------------
# ------------------------------ user login ---------------------------------------
# ---------------------------------------------------------------------------------

def login(request: HttpRequest):
    if request.method == "POST":
        try:
            username = request.POST.get("uname")
            if not username:
                messages.error(request, "User Name is required")
                return HttpResponseRedirect(reverse('login'))
            password = request.POST.get("password")
            if not password:
                messages.error(request, "Password is required")
                return HttpResponseRedirect(reverse('login'))
            
            authUser: AuthUser = AuthUser.objects.filter(userAuth = username).first()
            if not authUser:
                messages.error(request, "Not Found User.")
                return HttpResponseRedirect(reverse('login'))
            
            if VerifyPassword(password, authUser.passWord) == False:
                return HttpResponseRedirect(reverse('login'))
            
            session = AuthSession()
            session.session = secrets.token_hex(20)
            session.expireDate = timezone.now() + timezone.timedelta(days=1)
            
            session.SaveSessionData({"userId": str(authUser.refUser.id)})
            session.save()

            authUser.lastLogin = timezone.now()
            authUser.save()

            response = HttpResponseRedirect('/')
            response.set_cookie('session', session.session, expires = session.expireDate)
            return response

            
        except Exception as e:
            print(e)
            messages.error(request, str(e))
            return HttpResponseRedirect(reverse('login'))
    else:
        return render(request, 'login.html')
    
@requiredLogin
def logout(request: HttpRequest):
    try:
        session = request.COOKIES.get("session")
        authSession: AuthSession = AuthSession.objects.filter(session = session).first()
        if authSession:
            authSession.delete()
        response = HttpResponseRedirect(reverse('login'))
        response.delete_cookie('session')
        return response
    except Exception as e:
        print(e)
        messages.error(request, str(e))
        # return HttpResponseRedirect(reverse('login'))
        return HttpResponseRedirect('/')
    
@requiredLogin
def regisUser(request: HttpRequest, id:str):
    try:
        isUserAdmin = isSettingUserAdmin(request.currentUser.id)
        user: User = User.objects.filter(id = id).first()
        if not user:
            messages.error(request, "User not found")
            return HttpResponseRedirect(reverse('indexUser'))
        if not request.currentUser.isAdmin or isUserAdmin == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect(reverse('indexUser'))
        if request.method == "POST":
            username = request.POST.get("username")
            if not username:
                messages.error(request, "Username is required")
                return HttpResponseRedirect(reverse('indexUser'))
            password = request.POST.get("password")
            if not password:
                messages.error(request, "Password is required")
                return HttpResponseRedirect(reverse('indexUser'))

            authUser = AuthUser()
            authUser.refUser = user
            authUser.userAuth = username
            authUser.hashPassword(password)
            authUser.isActive = True
            authUser.isDelete = False
            authUser.save()

            user.isRegister = True
            user.save()

            messages.success(request, 'Register Success')
            return HttpResponseRedirect(reverse('indexUser'))
        else:
            context = {
                "user": user
            }
            return render(request, 'regis.html', context= context)
    except Exception as e:
        print(e)
        messages.error(request, str(e))
        return HttpResponseRedirect(reverse('indexUser'))
    
@requiredLogin
def resetPassword(request: HttpRequest, id:str):
    response = HttpResponseRedirect(reverse('indexUser'))
    try:
        isUserAdmin = isSettingUserAdmin(request.currentUser.id)
        user: User = User.objects.filter(id = id).first()
        if not user:
            messages.error(request, "User not found")
            return response
        if not request.currentUser.isAdmin or isUserAdmin == False:
            messages.error(request, "Not Permission")
            return response
        
        if request.method == "POST":
            usid = request.POST.get("usid")
            if not usid:
                messages.error(request, "Not found user id !")
                return response
            authid = request.POST.get("authid")
            if not authid:
                messages.error(request, "Not found auth id !")
                return response
            username = request.POST.get('username')
            if not username:
                messages.error(request, "Username is required")
                return response
            password = request.POST.get("password")
            if not password:
                messages.error(request, "Password is required")
                return response
            authUser: AuthUser = AuthUser.objects.filter(id = authid).first()
            if not authUser:
                messages.error(request, "Auth User not found")
                return response
            
            authUser.userAuth = username
            authUser.hashPassword(password)
            authUser.save()
            authSession: List[AuthSession] = AuthSession.objects.all()
            if authSession:
                for authSS in authSession:
                    data = authSS.GetSessionData()
                    if str(data["userId"]) == str(authUser.refUser.id):
                        authSS.delete()
                        response.delete_cookie('session')
            messages.success(request, 'Reset Password Success')
            return response
        else:
            authUser: AuthUser = AuthUser.objects.filter(refUser = user.id).first()
            if not authUser:
                messages.error(request, "Auth User not found")
                return response
            context = {
                "user": user,
                "authUser": authUser
            }
            return render(request, 'repassword.html', context)
    except Exception as e:
        print(e)
        messages.error(request, str(e))
        return response


