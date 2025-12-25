import json
from typing import List
from bson import ObjectId
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
import pytz
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from mongoengine.queryset.visitor import Q

from app_car_schedule.models.car_schedule import CarSchedule, ViewPersonCarSchedule
from app_car_schedule.models.car_schedule_setting import CarScheduleSetting
from app_car_schedule.models.driver import Driver
from app_user.models.user import User, UserStatus
from app_user.utils import requiredLogin
from base_models.basemodel import UserSnapshot
from utilities.utility import DateStrToDate, dateStrAndTimeToDatetime

tz = pytz.timezone("Asia/Bangkok")

@requiredLogin
def index(request: HttpRequest):
    checCurUserSettingAdmin = CarScheduleSetting.objects.filter(user = request.currentUser.id, isAdmin = True, isActive = True).first()
    isSettingAdmin = False
    if checCurUserSettingAdmin:
        isSettingAdmin = True
    context = {
        "isSettingAdmin": isSettingAdmin,
    }
    return render(request,'schedule/index.html', context)

def listCarScheduleJson(request: HttpRequest):
    try:
        if not request.method == "GET":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        sdate = request.GET.get('sdate')
        edate = request.GET.get('edate')
        if not sdate or not edate:
            return JsonResponse({'success': False, 'message': 'Date is required'})
        listData: List[CarSchedule] = CarSchedule.objects.filter(
            sDate__gte=sdate,
            eDate__lte=edate,
            isActive=True
        ).order_by('sDate')
        if not listData:
            return JsonResponse({'success': True, 'data': [], 'message': 'Success'})
        schedules = [ csh.serialize() for csh in listData]
        
        return JsonResponse({'success': True, 'data': schedules, 'message': 'Success'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@requiredLogin
def add(request: HttpRequest):
    response = HttpResponseRedirect(reverse('indexCarSchedule'))
    if request.method == "POST":
        try:
            title = request.POST.get('title')
            if not title:
                messages.error(request, "Title is required")
                return response
            dpDate = request.POST.get('dpStart')
            if not dpDate:
                messages.error(request, "Date is required")
                return response
            sTime = request.POST.get('stime')
            if not sTime:
                messages.error(request, "Start Time is required")
                return response
            eTime = request.POST.get('etime')
            if not eTime:
                messages.error(request, "End Time is required")
                return response
            # แปลงเวลา
            sDate = dateStrAndTimeToDatetime(dpDate, sTime)
            eDate = dateStrAndTimeToDatetime(dpDate, eTime)
            if sDate >= eDate:
                messages.error(request, 'Start date must be before end date.')
                return response

            driver = request.POST.get('driver')
            if not driver:
                messages.error(request, "Driver is required")
                return response
            driverData = Driver.objects.filter(id = driver).first()
            if not driverData:
                messages.error(request, "Driver not found")
                return response
            purpose = request.POST.get('purpose')
            destination = request.POST.get('destination')
            listPsg = request.POST.getlist('psgs[]')

            # --- เช็คว่ามี schedule ที่เวลาทับกันไหม
            conflict = CarSchedule.objects(
                isActive=True,
                driver__id=str(driverData.id)   # ถ้า driver เก็บ id ไว้ใน embedded doc
            ).filter(
                Q(sDate__lt=eDate) & Q(eDate__gt=sDate)
            ).first()

            if conflict:
                messages.error(request, "Driver already has a booking in this time slot.")
                return response

            schedule = CarSchedule()

            driverObj = ViewPersonCarSchedule()
            driverObj.id = str(driverData.id)
            if driverData.user:
                schedule.color = driverData.color
                if driverData.user.code : driverObj.code = driverData.user.code
                if driverData.user.fNameEN :driverObj.fNameEN = driverData.user.fNameEN
                if driverData.user.lNameEN : driverObj.lNameEN = driverData.user.lNameEN
                if driverData.user.phone : driverObj.phone = driverData.user.phone
                if driverData.user.email : driverObj.email = driverData.user.email
            driverObj.carLicenseNo = driverData.car.licenseNo if driverData.car else None

            passengers = []
            if listPsg and len(listPsg) > 0:
                for psg in listPsg:
                    if psg == "0":
                        other = ViewPersonCarSchedule()
                        other.id = "0"
                        passengers.append(other)
                    else:
                        person = ViewPersonCarSchedule()
                        userData = User.objects.filter(id = psg).first()
                        if userData:
                            person.id = str(userData.id)
                            if userData.code :person.code = userData.code
                            if userData.fNameEN : person.fNameEN = userData.fNameEN
                            if userData.lNameEN : person.lNameEN = userData.lNameEN
                            if userData.phone : person.phone = userData.phone
                            if userData.email : person.email = userData.email
                        
                        passengers.append(person)

            
            schedule.sDate = sDate
            schedule.eDate = eDate
            schedule.title = title
            schedule.purpose = purpose
            schedule.destination = destination
            schedule.isActive = True
            schedule.driver = driverObj
            schedule.passengers = passengers
            currentUser: User = request.currentUser
            if currentUser:
                uCreate = UserSnapshot().UserToSnapshot(currentUser)
                if uCreate:
                    schedule.createBy = uCreate
            schedule.save()
            messages.success(request, 'Save Success')
        except Exception as e:
            print(e)
            messages.error(request, str(e))
        return response
    else:
        drivers = Driver.objects.filter(isActive = True)
        passengers = User.objects.filter(isActive = True, status = UserStatus.Hire.value).order_by('code')
        qDate = request.GET.get('d') # -- query string date
        if not qDate:
            qDate = ""
        context = {
            "drivers": drivers,
            "passengers": passengers,
            "qDate": qDate,
        }
        return render(request,'schedule/add.html', context)

@requiredLogin
def edit(request: HttpRequest, id: str):
    if request.method == "POST":
        response = HttpResponseRedirect(reverse('indexCarSchedule'))
        try:
            scheduleId = request.POST.get('cshid')
            if not scheduleId:
                messages.error(request, "Not found id")
                return response
            schedule: CarSchedule = CarSchedule.objects.filter(id = scheduleId).first()
            if not schedule:
                messages.error(request, "Schedule not found")
                return response
            title = request.POST.get('title')
            if not title:
                messages.error(request, "Title is required")
                return response
            dpDate = request.POST.get('dpStart')
            if not dpDate:
                messages.error(request, "Date is required")
                return response
            sTime = request.POST.get('stime')
            if not sTime:
                messages.error(request, "Start Time is required")
                return response
            eTime = request.POST.get('etime')
            if not eTime:
                messages.error(request, "End Time is required")
                return response
            # แปลงเวลา
            sDate = dateStrAndTimeToDatetime(dpDate, sTime)
            eDate = dateStrAndTimeToDatetime(dpDate, eTime)
            if sDate >= eDate:
                messages.error(request, 'Start date must be before end date.')
                return response
            driver = request.POST.get('driver')
            if not driver:
                messages.error(request, "Driver is required")
                return response
            driverData: Driver = Driver.objects.filter(id = driver).first()
            if not driverData:
                messages.error(request, "Driver not found")
                return response
            purpose = request.POST.get('purpose')
            destination = request.POST.get('destination')
            listPsg = request.POST.getlist('psgs[]')
            # --- เช็คว่ามี schedule ที่เวลาทับกันไหม
            conflict = CarSchedule.objects(
                isActive=True,
                driver__id=str(driverData.id)   # ถ้า driver เก็บ id ไว้ใน embedded doc
            ).filter(
                Q(sDate__lt=eDate) & Q(eDate__gt=sDate) & Q(id__ne=schedule.id)
            ).first()

            if conflict:
                messages.error(request, "Driver already has a booking in this time slot.")
                return response

            driverObj = ViewPersonCarSchedule()
            driverObj.id = str(driverData.id)
            if driverData.user:
                schedule.color = driverData.color
                if driverData.user.code : driverObj.code = driverData.user.code
                if driverData.user.fNameEN :driverObj.fNameEN = driverData.user.fNameEN
                if driverData.user.lNameEN : driverObj.lNameEN = driverData.user.lNameEN
                if driverData.user.phone : driverObj.phone = driverData.user.phone
                if driverData.user.email : driverObj.email = driverData.user.email
            driverObj.carLicenseNo = driverData.car.licenseNo if driverData.car else None

            passengers = []
            if listPsg and len(listPsg) > 0:
                for psg in listPsg:
                    if psg == "0":
                        other = ViewPersonCarSchedule()
                        other.id = "0"
                        passengers.append(other)
                    else:
                        person = ViewPersonCarSchedule()
                        userData = User.objects.filter(id = psg).first()
                        if userData:
                            person.id = str(userData.id)
                            if userData.code :person.code = userData.code
                            if userData.fNameEN : person.fNameEN = userData.fNameEN
                            if userData.lNameEN : person.lNameEN = userData.lNameEN
                            if userData.phone : person.phone = userData.phone
                            if userData.email : person.email = userData.email
                        
                        passengers.append(person)

            schedule.sDate = sDate
            schedule.eDate = eDate
            schedule.title = title
            schedule.purpose = purpose
            schedule.destination = destination
            schedule.isActive = True
            schedule.driver = driverObj
            schedule.passengers = passengers
            schedule.updateDate = timezone.now()
            currentUser: User = request.currentUser
            if currentUser:
                uUpdate = UserSnapshot().UserToSnapshot(currentUser)
                if uUpdate:
                    schedule.updateBy = uUpdate
            schedule.save()

            messages.success(request, 'Save Success')
        except Exception as e:
            print(e)
            messages.error(request, str(e))
        return response
    else:
        if not id:
            messages.error(request, "Not found id")
            return HttpResponseRedirect(reverse('indexCarSchedule'))
        schedule: CarSchedule = CarSchedule.objects.filter(id = id).first()
        if not schedule:
            messages.error(request, "Schedule not found")
            return HttpResponseRedirect(reverse('indexCarSchedule'))
        drivers = Driver.objects.filter(isActive = True)
        passengers = User.objects.filter(isActive = True).order_by('code')
        listPsg = []
        for psg in schedule.passengers:
            listPsg.append(psg.id)

        context = {
            "drivers": drivers,
            "passengers": passengers,
            "schedule": schedule,
            "listPsg": listPsg,
        }
        return render(request,'schedule/edit.html', context)

@requiredLogin
def delete(request: HttpRequest, id: str):
    try:
        if not request.method == "GET":
            return JsonResponse({'deleted': False, 'message': 'Method not allowed'})
        if not id:
            return JsonResponse({'deleted': False, 'message': 'Not found id'})
        schedule: CarSchedule = CarSchedule.objects.filter(id = id).first()
        if not schedule:
            return JsonResponse({'deleted': False, 'message': 'Schedule not found'})
        schedule.isActive = False
        schedule.updateDate = timezone.now()
        currentUser: User = request.currentUser
        if currentUser:
            uDelete = UserSnapshot().UserToSnapshot(currentUser)
            if uDelete:
                schedule.updateBy = uDelete
        schedule.save()
        return JsonResponse({'deleted': True, 'message': 'Delete success'})

    except Exception as e:
        print(e)
        return JsonResponse({'deleted': False, 'message': str(e)})
    
@requiredLogin
def listPage(request: HttpRequest):
    if request.method == 'POST':
        pass
    else:
        drivers = Driver.objects.filter(isActive = True)
        users = User.objects.filter(isActive = True).order_by('code')
        print(f"year : {timezone.now().year}")
        defaultYear =int(2020)
        nowYear = int(timezone.now().year)
        years = list(range(nowYear, defaultYear - 1, -1))
        currentUser: User = request.currentUser
        checkCurUserSettingAdmin = CarScheduleSetting.objects.filter(user = currentUser.id, isAdmin = True, isActive = True).first()
        isSettingAdmin = False
        if checkCurUserSettingAdmin:
            isSettingAdmin = True
        context = {
            "drivers": drivers,
            "users": users,
            "years": years,
            "selectUser": currentUser.id if currentUser else "",
            "isSettingAdmin": isSettingAdmin,
        }
        return render(request,'schedule/list.html', context)


    
def filterCarScheduleJson(request: HttpRequest):
    try:
        if request.method != "POST":
            return JsonResponse({'success': False, 'message': "Method not allowed"})
        body = json.loads(request.body.decode('utf-8'))  # อ่าน JSON body
        year = body.get('year')
        passenger = body.get('passenger')
        driver = body.get('driver')
        bookby = body.get('bookby')
        currentUser: User = request.currentUser
        checkCurUserSettingAdmin = CarScheduleSetting.objects.filter(user = currentUser.id, isAdmin = True, isActive = True).first()
        isSettingAdmin = False
        if checkCurUserSettingAdmin:
            isSettingAdmin = True

        schedules: List[CarSchedule] = CarSchedule.objects.filter(isActive = True)
        if year:
            # schedules = schedules.filter(sDate__year = year)
            start = datetime(int(year), 1, 1, tzinfo=tz)
            end = datetime(int(year) + 1, 1, 1, tzinfo=tz)
            schedules = schedules.filter(sDate__gte=start, sDate__lt=end)
        if passenger and passenger != "None":
            schedules = schedules.filter(passengers__id = passenger)
        if driver and driver != "0":
            schedules = schedules.filter(driver__id = driver)
        if bookby and bookby != "0":
            schedules = schedules.filter(Q(createBy__userId = ObjectId(bookby)) | Q(updateBy__userId = ObjectId(bookby)))
        schedules = schedules.order_by('-sDate')
        return JsonResponse({'success': True, 'data': [sch.serialize(current_user=currentUser, is_setting_admin=isSettingAdmin) for sch in schedules], 'message': 'Success'})

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})
    

def exportByDateRange(request: HttpRequest):
    try:
        if not request.method == "POST":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        body = json.loads(request.body.decode('utf-8'))  # อ่าน JSON body
        year = body.get('year')
        sdate_str = body.get('sdate')
        edate_str = body.get('edate')

        print(sdate_str, edate_str)
        if not sdate_str:
            return JsonResponse({'success': False, 'message': 'Date is required'})
        if not edate_str:
            return JsonResponse({'success': False, 'message': 'Date is required'})
        # --- แปลงจาก string → datetime (naive)
        sdate_dt = datetime.strptime(sdate_str, "%d/%m/%Y")
        edate_dt = datetime.strptime(edate_str, "%d/%m/%Y")

        sdate_dt = tz.localize(sdate_dt).astimezone(pytz.utc)
        edate_dt = tz.localize(edate_dt + timedelta(days=1)).astimezone(pytz.utc)
        print(sdate_dt, edate_dt)
        if sdate_dt > edate_dt:
            return JsonResponse({'success': False, 'message': 'Start date must be before end date.'})

        drivers: List[Driver] = Driver.objects.filter(isActive=True)
        schedules: List[CarSchedule] = CarSchedule.objects.filter(
            isActive=True,
            sDate__gte=sdate_dt,
            sDate__lt=edate_dt
        ).order_by('sDate')
        context = {
            "year": year,
            "sdate": sdate_str,   # ✅ สำคัญ
            "edate": edate_str,   # ✅ สำคัญ
            "drivers": [driver.serialize() for driver in drivers],
            "schedules": [schedule.serialize() for schedule in schedules],
        }

        return JsonResponse({'success': True, 'data': context, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})


def excelYear(request: HttpRequest, year: str):
    try:
        if request.method != "GET":
            return JsonResponse({'success': False, 'message': "Method not allowed"})
        if not year:
            return JsonResponse({'success': False, 'message': "Year is required"})
        year = int(year)
        start_date = tz.localize(datetime(year, 1, 1, 0, 0, 0))
        end_date   = tz.localize(datetime(year + 1, 1, 1, 0, 0, 0))

        drivers: List[Driver] = Driver.objects.filter(isActive=True)
        schedules: List[CarSchedule] = CarSchedule.objects.filter(
            isActive=True,
            sDate__gte=start_date,
            sDate__lt=end_date
        ).order_by('sDate')
        context = {
            "year": year,
            "drivers": [driver.serialize() for driver in drivers],
            "schedules": [schedule.serialize() for schedule in schedules],
        }
        return JsonResponse({'success': True, 'data': context, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})