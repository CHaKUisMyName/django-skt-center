import json
from typing import List
from bson import ObjectId
from django.conf import settings
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
import pytz
from django.utils import timezone
import datetime

from app_user.models.immigration import ExpiredImmigration, Immigration
from app_user.models.user import EmpNation, User, UserStatus
from app_user.tasks import check_immigration_expired
from app_user.utils import HasUsPermission, requiredLogin
from base_models.basemodel import UserSnapshot
from utilities.utility import DateStrToDate, printLogData
from django.contrib import messages

tz = pytz.timezone("Asia/Bangkok")

@requiredLogin
def index(request: HttpRequest):
    hasPermission = HasUsPermission(id = str(request.currentUser.id), menu = "Immigration")
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    users: User = User.objects.filter(isActive = True, nation__ne = EmpNation.Thai.value, status = UserStatus.Hire.value).order_by('code')
    check_immigration_expired()
    context = {
        "users": users
    }
    return render(request, 'immigration/index.html', context)

@requiredLogin
def listImmigrationJson(request: HttpRequest):
    try:
        if not request.method == "GET":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        listData: List[Immigration] = Immigration.objects.filter(isActive = True)
        if not listData:
            return JsonResponse({'success': True, 'data': [], 'message': 'Success'})
        immigrations = [ im.serialize() for im in listData]
        
        return JsonResponse({'success': True, 'data': immigrations, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})
    
@requiredLogin
def getImmigrationJson(request: HttpRequest, id: str):
    try:
        if not request.method == "GET":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        if not id:
            return JsonResponse({'success': False, 'message': 'Id is required'})
        data: Immigration = Immigration.objects.filter(id = id).first()
        if not data:
            return JsonResponse({'success': False, 'message': 'Data not found'})
        return JsonResponse({'success': True, 'data': data.serialize(), 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})

@requiredLogin
def addJson(request: HttpRequest):
    try:
        if request.method != "POST":
           return JsonResponse({'success': False, 'message': 'Method not allowed'})
         
        body = json.loads(request.body.decode('utf-8'))  # อ่าน JSON body
        refUser = body.get('user')
        if not refUser:
           return JsonResponse({'success': False, 'message': 'User is required'})
        inputDate = body.get('inputDate')
        if not inputDate:
           return JsonResponse({'success': False, 'message': 'input date is required'})
        dupData: Immigration = Immigration.objects.filter(refUser = refUser, isActive = True).first()
        if dupData:
           return JsonResponse({'success': False, 'message': 'Duplicate data'})
        
        immigration: Immigration = Immigration()
        immigration.refUser = ObjectId(refUser)
        immigration.inputDate = DateStrToDate(inputDate)
        #  immigration.dueDate = DateStrToDate(duedate)
        # ✅ ตั้งค่า duedate = 90 วันนับ inputDate ด้วย
        if immigration.inputDate:
            immigration.dueDate = immigration.inputDate + datetime.timedelta(days=89)
        immigration.status = ExpiredImmigration.Normal
        immigration.isActive = True
        immigration.hasNoti15 = False
        immigration.hasNoti7 = False
        immigration.hasNotiExpired = False
        currentUser: User = request.currentUser
        if currentUser:
            uCreate = UserSnapshot().UserToSnapshot(currentUser)
            if uCreate:
               immigration.createBy = uCreate
        immigration.save()
        check_immigration_expired()
        return JsonResponse({'success': True, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})
    
@requiredLogin
def editJson(request: HttpRequest):
    try:
        if request.method != "POST":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        body = json.loads(request.body.decode('utf-8'))  # อ่าน JSON body
        immId = body.get('immId')
        if not immId:
            return JsonResponse({'success': False, 'message': 'Id is required'})
        inputDate = body.get('inputDate')
        if not inputDate:
            return JsonResponse({'success': False, 'message': 'inout date is required'})
        # dueDate = DateStrToDate(dueDate)
        
        oldImmigration: Immigration = Immigration.objects.filter(id = immId).first()
        if not oldImmigration:
            return JsonResponse({'success': False, 'message': 'Immigration not found'})
        oldImmigration.isActive = False
        currentUser: User = request.currentUser
        if currentUser:
            uUpdate = UserSnapshot().UserToSnapshot(currentUser)
            if uUpdate:
                oldImmigration.updateBy = uUpdate
        oldImmigration.updateDate = timezone.now()
        oldImmigration.save()
        
        immigration: Immigration = Immigration()
        immigration.refUser = oldImmigration.refUser
        immigration.inputDate = DateStrToDate(inputDate)
        # ✅ ตั้งค่า duedate = 90 วันนับ inputDate ด้วย
        if immigration.inputDate:
            immigration.dueDate = immigration.inputDate + datetime.timedelta(days=89)
        # immigration.updateDate = timezone.now()
        immigration.status = ExpiredImmigration.Normal
        immigration.hasNoti15 = False
        immigration.hasNoti7 = False
        immigration.hasNotiExpired = False
        immigration.isActive = True
        if currentUser:
            uCreate = UserSnapshot().UserToSnapshot(currentUser)
            if uCreate:
                immigration.createBy = uCreate
        immigration.createDate = timezone.now()
        immigration.save()
        check_immigration_expired()        
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
            return JsonResponse({'success': False, 'message': 'Id is required'})
        immigration: Immigration = Immigration.objects.filter(id = id).first()
        if not immigration:
            return JsonResponse({'success': False, 'message': 'Immigration not found'})
        immigration.isActive = False
        immigration.updateDate = timezone.now()
        currentUser: User = request.currentUser
        if currentUser:
            uDelete = UserSnapshot().UserToSnapshot(currentUser)
            if uDelete:
                immigration.updateBy = uDelete
        immigration.save()
        check_immigration_expired()
        return JsonResponse({'success': True, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})
    
def deleteImmigrationByUser(requester: User, user: User):
    immigration: Immigration = Immigration.objects.filter(refUser = user.id, isActive = True).first()
    if immigration:
        immigration.isActive = False
        immigration.updateDate = timezone.now()
        if requester:
            uUpdate = UserSnapshot().UserToSnapshot(requester)
            if uUpdate:
                immigration.updateBy = uUpdate
        immigration.save()
        check_immigration_expired()





    