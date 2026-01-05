from django.utils import timezone
import json
from typing import List
from bson import ObjectId
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from app_user.models.family import FamilyProfile, FamilyType, UserFamily
from app_user.models.user import User, UserStatus, UserType
from app_user.utils import HasUsPermission, requiredLogin
from base_models.basemodel import UserSnapshot
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect

# Create your views here.


@requiredLogin
def index(request: HttpRequest):
    hasPermission = HasUsPermission(id = str(request.currentUser.id), menu = "Family")
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    userFamilies = []
    listData = UserFamily.objects.filter(isActive=True)

    if len(listData) > 0:
        listData = sorted(
            listData,
            key=lambda x: int(x.employee.code) if x.employee.code else 0
        )
        userFamilies = [ us.serialize_datatable() for us in listData]
    context = {
        'userFamilies': userFamilies,
    }
    return render(request, 'family/index.html', context)

@requiredLogin
def add(request: HttpRequest):
    hasPermission = HasUsPermission(id = str(request.currentUser.id), menu = "Family")
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    users: List[User] = User.objects.filter(isActive = True, status = UserStatus.Hire, userType = UserType.Employee).order_by('code')
    dropdownUser = [ us.serialize for us in users]
    context = {
        'dropdownUser': dropdownUser,
    }
    return render(request, 'family/add.html', context)

@requiredLogin
def addJson(request: HttpRequest):
    try:
        if not request.method == "POST":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        emp = request.POST.get('emp')
        fFaName = request.POST.get('fFaName')
        lFaName = request.POST.get('lFaName')
        fMoName = request.POST.get('fMoName')
        lMoName = request.POST.get('lMoName')
        fHName = request.POST.get('fHName')
        lHName = request.POST.get('lHName')
        childrenProfileStr = request.POST.getlist('childrenProfile[]')
        if not emp:
            return JsonResponse({'success': False, 'message': 'Employee is required'})
        dupUser:UserFamily = UserFamily.objects.filter(employee = ObjectId(emp), isActive = True).first()
        if dupUser:
            return JsonResponse({'success': False, 'message': 'Duplicate Data.'})
        
        userFamily: UserFamily = UserFamily()
        userFamily.employee = ObjectId(emp)
        userFamily.fatherProfile = FamilyProfile(fName = fFaName, lName = lFaName, relation = FamilyType.Father) if fFaName or lFaName else None
        userFamily.motherProfile = FamilyProfile(fName = fMoName, lName = lMoName, relation = FamilyType.Mother) if fMoName or lMoName else None
        userFamily.spouseProfile = FamilyProfile(fName = fHName, lName = lHName, relation = FamilyType.Spouse) if fHName or lHName else None

        childrenProfile: List[FamilyProfile] = []
        if childrenProfileStr:
            rawChildJson = [json.loads(x) for x in childrenProfileStr]
            if len(rawChildJson) > 0:
                for pf in rawChildJson:
                    if pf['fName'] or pf['lName']:
                        childPf: FamilyProfile = FamilyProfile(fName = pf['fName'], lName = pf['lName'], relation = FamilyType.Children)
                        childrenProfile.append(childPf)
        userFamily.childrenProfile = childrenProfile
        userFamily.isActive = True
        curUser:User = request.currentUser
        if curUser:
            uCreate = UserSnapshot().UserToSnapshot(curUser)
            if uCreate:
                userFamily.createBy = uCreate
        userFamily.createDate = timezone.now()
        userFamily.save()
        return JsonResponse({'success': True, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})
    
@requiredLogin
def edit(request: HttpRequest, id: str):
    hasPermission = HasUsPermission(id = str(request.currentUser.id), menu = "Family")
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    famData: UserFamily = UserFamily.objects.filter(isActive = True, id = ObjectId(id)).first()
    selectedUser = famData.employee
    context = {
        'selectedUser': selectedUser,
        'famData': famData.serialize(),
    }
    return render(request, 'family/edit.html', context)

@requiredLogin
def editJson(request: HttpRequest):
    try:
        if not request.method == "POST":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        famId = request.POST.get('famId')
        emp = request.POST.get('emp')
        fFaName = request.POST.get('fFaName')
        lFaName = request.POST.get('lFaName')
        fMoName = request.POST.get('fMoName')
        lMoName = request.POST.get('lMoName')
        fHName = request.POST.get('fHName')
        lHName = request.POST.get('lHName')
        childrenProfileStr = request.POST.getlist('childrenProfile[]')
        if not famId:
            return JsonResponse({'success': False, 'message': 'Id is required'})
        if not emp:
            return JsonResponse({'success': False, 'message': 'Employee is required'})
        
        userFamily: UserFamily = UserFamily.objects.filter(id = ObjectId(famId)).first()
        if not userFamily:
            return JsonResponse({'success': False, 'message': "Not Found Data."})
        
        userFamily.fatherProfile = FamilyProfile(fName = fFaName, lName = lFaName, relation = FamilyType.Father) if fFaName or lFaName else None
        userFamily.motherProfile = FamilyProfile(fName = fMoName, lName = lMoName, relation = FamilyType.Mother) if fMoName or lMoName else None
        userFamily.spouseProfile = FamilyProfile(fName = fHName, lName = lHName, relation = FamilyType.Spouse) if fHName or lHName else None
        childrenProfile: List[FamilyProfile] = []
        if childrenProfileStr:
            rawChildJson = [json.loads(x) for x in childrenProfileStr]
            if len(rawChildJson) > 0:
                for pf in rawChildJson:
                    if pf['fName'] or pf['lName']:
                        childPf: FamilyProfile = FamilyProfile(fName = pf['fName'], lName = pf['lName'], relation = FamilyType.Children)
                        childrenProfile.append(childPf)
        userFamily.childrenProfile = childrenProfile
        curUser:User = request.currentUser
        if curUser:
            uCreate = UserSnapshot().UserToSnapshot(curUser)
            if uCreate:
                userFamily.updateBy = uCreate
        userFamily.updateDate = timezone.now()
        userFamily.save()

        return JsonResponse({'success': True, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})
    
@requiredLogin
def deleteJson(request: HttpRequest, id: str):
    try:
        if not request.method == "GET":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        if not id:
            return JsonResponse({'success': False, 'message': 'Id not found.'})
        id = ObjectId(id)
        userFamily: UserFamily = UserFamily.objects.filter(id = id).first()
        if not userFamily:
            return JsonResponse({'success': False, 'message': 'Not found Data.'})
        userFamily.isActive = False
        curUser:User = request.currentUser
        if curUser:
            uDelete = UserSnapshot().UserToSnapshot(curUser)
            if uDelete:
                userFamily.updateBy = uDelete
        userFamily.updateDate = timezone.now()
        userFamily.save()

        return JsonResponse({'success': True, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})