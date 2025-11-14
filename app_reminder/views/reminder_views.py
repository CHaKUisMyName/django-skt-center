from datetime import timezone as dt_timezone, timedelta
from zoneinfo import ZoneInfo
from django.utils import timezone
from typing import List
from bson import ObjectId
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from app_reminder.models.reminder import Reminder
from app_reminder.tasks import check_reminder
from app_reminder.utils import sendMailReminder
from app_user.models.user import User
from app_user.utils import requiredLogin
from base_models.basemodel import UserSnapshot
from utilities.utility import DateStrToDate


@requiredLogin
def index(request: HttpRequest):
    users = []
    listUser: List[User] = User.objects.filter(isActive = True).order_by('code')
    users = [user.serialize() for user in listUser]
    context = {
        'users': users,
    }
    return render(request, 'reminder/index.html', context)

@requiredLogin
def filter(request: HttpRequest):
    try:
        if not request.method == "GET":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        listReminder: List[Reminder] = Reminder.objects.filter(isActive = True).order_by('-createDate')
        
        data = [reminder.serailize_for_datatable() for reminder in listReminder]
        return JsonResponse({'success': True, 'data': data, 'message': 'Success'})

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})
    
@requiredLogin
def AddJson(request: HttpRequest):
    try:
        if not request.method == "POST":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        subject = request.POST.get('subject')
        detail = request.POST.get('detail')
        fReceiver = request.POST.get('fReceiver')
        sReceiver = request.POST.get('sReceiver')
        expiredDate = request.POST.get('expiredDate')
        alertBefore = request.POST.get('count')
        smsChecked = request.POST.get('smsChecked')

        if not subject:
            return JsonResponse({'success': False, 'message': 'Subject is required'})
        if not detail:
            return JsonResponse({'success': False, 'message': 'Detail is required'})
        if not fReceiver and fReceiver == "0":
            return JsonResponse({'success': False, 'message': 'First receiver is required'})
        if not expiredDate:
            return JsonResponse({'success': False, 'message': 'Expired date is required'})
        if not alertBefore:
            return JsonResponse({'success': False, 'message': 'Alert before is required'})
        
        if expiredDate:
            expiredDate = DateStrToDate(expiredDate)
            if not expiredDate:
                return JsonResponse({'success': False, 'message': 'Expired date is invalid'})
        if alertBefore:
            alertBefore = int(alertBefore)

        reminder: Reminder = Reminder()
        reminder.subject = subject
        reminder.detail = detail
        if sReceiver and sReceiver != "0":
            reminder.receiver = [fReceiver, sReceiver]
        else:
            reminder.receiver = [fReceiver]
        reminder.expiredDate = expiredDate
        reminder.alertBefore = alertBefore
        reminder.isSendMail = True
        reminder.isSendSMS = True if smsChecked == "true" else False

        fRecUser:User = User.objects.filter(id = ObjectId(fReceiver)).first()
        if not fRecUser:
            return JsonResponse({'success': False, 'message': 'First receiver is not found.'})

        if smsChecked == "true":
            if not fRecUser.phone and fRecUser.phone == "":
                return JsonResponse({'success': False, 'message': 'First receiver has no phone data.'})
            reminder.smsNumber = fRecUser.phone
        else:
            reminder.smsNumber = None
        reminder.status = False
        reminder.isActive = True
        curUser:User = request.currentUser
        if not curUser:
            return JsonResponse({'success': False, 'message': 'User not found'})
        uCreate = UserSnapshot().UserToSnapshot(curUser)
        if uCreate:
            reminder.createBy = uCreate
        reminder.createDate = timezone.now()
        reminder.save()

        print(subject, detail, fReceiver, sReceiver, expiredDate, alertBefore, smsChecked)

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
        reminder: Reminder = Reminder.objects.filter(id = id).first()
        if not reminder:
            return JsonResponse({'success': False, 'message': 'Reminder not found'})
        reminder.isActive = False
        reminder.updateDate = timezone.now()
        curUser:User = request.currentUser
        if curUser:
            uUpdate = UserSnapshot().UserToSnapshot(curUser)
            if uUpdate:
                reminder.updateBy = uUpdate
        reminder.save()
        return JsonResponse({'success': True, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})