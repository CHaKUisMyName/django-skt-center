from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone


from app_car_schedule.models.car import Car
from app_car_schedule.models.driver import Driver
from app_user.models.user import User
from app_user.utils import requiredLogin
from base_models.basemodel import UserSnapshot

@requiredLogin
def index(request: HttpRequest):
    cars = Car.objects.filter(isActive = True)
    context = {
        "cars": cars,
    }
    return render(request,'car/index.html', context)

@requiredLogin
def add(request: HttpRequest):
    if request.method == "POST":
        response = HttpResponseRedirect(reverse('indexCar'))
        try:
            licenseNo = request.POST.get('licenseno')
            if not licenseNo:
                messages.error(request, "License No. is required")
                return response
            brand = request.POST.get('brand')
            model = request.POST.get('model')
            note = request.POST.get('note')

            car: Car = Car()
            car.licenseNo = licenseNo
            car.brand = brand
            car.model = model
            car.note = note
            car.isActive = True
            currentUser: User = request.currentUser
            if currentUser:
                uCreate = UserSnapshot().UserToSnapshot(currentUser)
                if uCreate:
                    car.createBy = uCreate
            car.save()
            messages.success(request, 'Save Success')
        except Exception as e:
            print(e)
            messages.error(request, str(e))
        return response
    else:
        return render(request,'car/add.html')
    
@requiredLogin
def edit(request: HttpRequest, id: str):
    response = HttpResponseRedirect(reverse('indexCar'))
    if request.method == "POST":
        carId = request.POST.get('carId')
        if not carId:
            messages.error(request, "Not found id")
            return response
        licenseNo = request.POST.get('licenseno')
        if not licenseNo:
            messages.error(request, "License No. is required")
            return response
        brand = request.POST.get('brand')
        model = request.POST.get('model')
        note = request.POST.get('note')
        try:
            car: Car = Car.objects.filter(id = carId).first()
            if not car:
                messages.error(request, "Car not found")
                return response
            car.brand = brand
            car.model = model
            car.licenseNo = licenseNo
            car.note = note
            car.updateDate = timezone.now()
            currentUser: User = request.currentUser
            if currentUser:
                uUpdate = UserSnapshot().UserToSnapshot(currentUser)
                if uUpdate:
                    car.updateBy = uUpdate
            car.save()
            messages.success(request, 'Save Success')
        except Exception as e:
            print(e)
            messages.error(request, str(e))
        
        return response

    else:
        if not id:
            messages.error(request, "Not found id")
            return response
        car: Car = Car.objects.filter(id = id).first()
        if not car:
            messages.error(request, "Car not found")
            return
        context = {
            "car": car,
        }
        return render(request,'car/edit.html', context)
    

@requiredLogin
def delete(request: HttpRequest, id: str):
    try:
        if not request.method == "GET":
            return JsonResponse({'deleted': False, 'message': 'Method not allowed'})
        if not id:
            return JsonResponse({'deleted': False, 'message': 'Not found id'})
        car: Car = Car.objects.filter(id = id).first()
        if not car:
            return JsonResponse({'deleted': False, 'message': 'Car not found'})
        driver = Driver.objects.filter(isActive = True, car = car)
        if driver:
            return JsonResponse({'deleted': False, 'message': 'Car is in use'})
        car.isActive = False
        car.updateDate = timezone.now()
        currentUser: User = request.currentUser
        if currentUser:
            uDelete = UserSnapshot().UserToSnapshot(currentUser)
            if uDelete:
                car.updateBy = uDelete
        car.save()
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