from typing import List
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from app_car_schedule.models.car import Car
from app_car_schedule.models.driver import Driver
from app_car_schedule.utils import HasCshPermission
from app_user.models.user import User, UserStatus
from app_user.utils import requiredLogin
from base_models.basemodel import UserSnapshot


@requiredLogin
def index(request: HttpRequest):
    drivers = Driver.objects.filter(isActive = True)
    hasPermission = HasCshPermission(id = str(request.currentUser.id), menu = "Driver")
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    context = {
        "drivers": drivers,
    }
    return render(request,'driver/index.html', context)

@requiredLogin
def add(request: HttpRequest):
    hasPermission = HasCshPermission(id = str(request.currentUser.id), menu = "Driver")
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    if request.method == "POST":
        response = HttpResponseRedirect(reverse('indexDriver'))
        try:
            driver = request.POST.get('driver')
            if not driver:
                messages.error(request, "Driver is required")
                return response
            color = request.POST.get('color')
            car = request.POST.get('car')
            if car == "None":
                car = None
            else:
                car = Car.objects.filter(id = car).first()
            note = request.POST.get('note')
            dupDriver = Driver.objects.filter(id = driver, isActive = True).first()
            if dupDriver:
                messages.error(request, "Driver already exists")
                return response
            driver: User = User.objects.filter(id = driver).first()
            if not driver:
                messages.error(request, "User not found")
            data = Driver()
            data.user = driver
            data.color = color
            data.car = car
            data.note = note
            data.isActive = True
            currentUser: User = request.currentUser
            if currentUser:
                uCreate = UserSnapshot().UserToSnapshot(currentUser)
                if uCreate:
                    data.createBy = uCreate
            data.save()
            messages.success(request, 'Save Success')
        except Exception as e:
            print(e)
            messages.error(request, str(e))
        return response
    else:
        users: List[User] = User.objects.filter(isActive = True, status = UserStatus.Hire).order_by('code')
        cars: List[Car] = Car.objects.filter(isActive = True)
        # disable user ที่เป็น driver ไปแล้ว
        drivers = Driver.objects.filter(isActive = True)
        dropdown_users = []
        for u in users:
            dropdown_users.append({
                "id": str(u.id),
                "code": u.code,
                "fNameEN": u.fNameEN,
                "lNameEN": u.lNameEN,
                "disabled": str(u.id) in [str(uid.user.id) for uid in drivers]
            })
        # สร้าง set ของ car_id ที่ถูกใช้แล้ว
        used_car_ids = {str(d.car.id) for d in drivers if d.car}
        dropdown_cars = []
        for c in cars:
            dropdown_cars.append({
                "id": str(c.id),
                "licenseNo": c.licenseNo,
                "disabled": str(c.id) in used_car_ids
            })
        context = {
            "dropdown_users": dropdown_users,
            "dropdown_cars": dropdown_cars,
        }
        return render(request,'driver/add.html', context)

@requiredLogin
def edit(request: HttpRequest, id: str):
    hasPermission = HasCshPermission(id = str(request.currentUser.id), menu = "Driver")
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    response = HttpResponseRedirect(reverse('indexDriver'))
    if request.method == "POST":
        try:
            driverId = request.POST.get('dvid')
            if not driverId:
                messages.error(request, "Not found id")
                return response
            driver: Driver = Driver.objects.filter(id = driverId).first()
            if not driver:
                messages.error(request, "Driver not found")
                return response
            color = request.POST.get('color')
            car = request.POST.get('car')
            if car == "None":
                car = None
            else:
                car = Car.objects.filter(id = car).first()
            note = request.POST.get('note')
            driver.color = color
            driver.car = car
            driver.note = note
            driver.updateDate = timezone.now()
            currentUser: User = request.currentUser
            if currentUser:
                uUpdate = UserSnapshot().UserToSnapshot(currentUser)
                if uUpdate:
                    driver.updateBy = uUpdate
            driver.save()

            messages.success(request, 'Save Success')
        except Exception as e:
            print(e)
            messages.error(request, str(e))
        return response
    else:
        if not id:
            messages.error(request, "Not found id")
            return response
        driver = Driver.objects.filter(id = id).first()
        if not driver:
            messages.error(request, "Driver not found")
            return response
        drivers = Driver.objects.filter(isActive = True)
        print(driver.to_json())
        cars: List[Car] = Car.objects.filter(isActive = True)
        # สร้าง set ของ car_id ที่ถูกใช้แล้ว
        used_car_ids = {
            str(d.car.id)
            for d in drivers
            if d.car and (not driver.car or driver.car.id != d.car.id)
        }
        dropdown_cars = []
        for c in cars:
            dropdown_cars.append({
                "id": str(c.id),
                "licenseNo": c.licenseNo,
                "disabled": str(c.id) in used_car_ids
            })

        context = {
            "driver": driver,
            "dropdown_cars": dropdown_cars,
        }
        return render(request,'driver/edit.html', context)
    
@requiredLogin
def delete(request: HttpRequest, id: str):
    try:
        if not request.method == "GET":
            return JsonResponse({'deleted': False, 'message': 'Method not allowed'})
        hasPermission = HasCshPermission(id = str(request.currentUser.id), menu = "Driver")
        if not request.currentUser.isAdmin:
            if hasPermission == False:
                return JsonResponse({'deleted': False, 'message': 'Not Permission'})
        if not id:
            return JsonResponse({'deleted': False, 'message': 'Not found id'})
        driver: Driver = Driver.objects.filter(id = id).first()
        if not driver:
            return JsonResponse({'deleted': False, 'message': 'Driver not found'})
        
        driver.isActive = False
        driver.car = None
        driver.updateDate = timezone.now()
        currentUser: User = request.currentUser
        if currentUser:
            uDelete = UserSnapshot().UserToSnapshot(currentUser)
            if uDelete:
                driver.updateBy = uDelete
        driver.save()
        r = {
            'deleted': True,
            'message': 'Delete success'
        }
        return JsonResponse(r)
    except Exception as e:
        r = {
            'deleted': False,
            'message': str(e)
        }
        return JsonResponse(r)
    
def deleteDriverByUser(requester: User, user: User):
    driver: Driver = Driver.objects.filter(user = user.id).first()
    if driver:
        driver.isActive = False
        driver.updateDate = timezone.now()
        if requester:
            uUpdate = UserSnapshot().UserToSnapshot(requester)
            if uUpdate:
                driver.updateBy = uUpdate
        driver.save()