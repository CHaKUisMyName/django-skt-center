from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone

from app_user.models.user import User
from app_user.utils import requiredLogin
from app_visitor.models.option import Option
from app_visitor.utils import HasVstPermission
from base_models.basemodel import UserSnapshot

@requiredLogin
def index(request: HttpRequest):
    options = Option.objects.filter(isActive = True)
    hasPermission = HasVstPermission(id = str(request.currentUser.id), menu = "Option")
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    context = {
        "options": options,
    }
    return render(request,'option/index.html', context)

@requiredLogin
def add(request: HttpRequest):
    hasPermission = HasVstPermission(id = str(request.currentUser.id), menu = "Option")
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    if request.method == "POST":
        response = HttpResponseRedirect(reverse('indexOption'))
        try:
            op = request.POST.get('option')
            if not op:
                messages.error(request, "Option name is required")
                return response
            note = request.POST.get('note')

            option: Option = Option()
            option.name = op
            option.note = note
            option.isActive = True
            currentUser: User = request.currentUser
            if currentUser:
                uCreate = UserSnapshot().UserToSnapshot(currentUser)
                if uCreate:
                    option.createBy = uCreate
            option.save()
            messages.success(request, 'Save Success')

        except Exception as e:
            print(e)
            messages.error(request, str(e))
        return response
    else:
        return render(request,'option/add.html')
    
@requiredLogin
def edit(request: HttpRequest, id: str):
    hasPermission = HasVstPermission(id = str(request.currentUser.id), menu = "Option")
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    response = HttpResponseRedirect(reverse('indexOption'))
    if request.method == "POST":
        try:
            opId = request.POST.get('optionId')
            if not opId:
                messages.error(request, "Not found id")
                return response
            op = request.POST.get('option')
            if not op:
                messages.error(request, "Option name is required")
                return response
            note = request.POST.get('note')

            option: Option = Option.objects.filter(id = opId).first()
            if not option:
                messages.error(request, "Option not found")
                return response
            option.name = op
            option.note = note
            option.updateDate = timezone.now()
            currentUser: User = request.currentUser
            if currentUser:
                uUpdate = UserSnapshot().UserToSnapshot(currentUser)
                if uUpdate:
                    option.updateBy = uUpdate
            option.save()
            messages.success(request, 'Save Success')
        except Exception as e:
            print(e)
            messages.error(request, str(e))
        return response
    else:
        if not id:
            messages.error(request, "Not found id")
            return response
        option: Option = Option.objects.filter(id = id).first()
        if not option:
            messages.error(request, "Option not found")
            return response
        context = {
            "option": option,
        }
        return render(request,'option/edit.html', context)
    
@requiredLogin
def delete(request: HttpRequest, id: str):
    try:
        if not request.method == "GET":
            return JsonResponse({'deleted': False, 'message': 'Method not allowed'})
        hasPermission = HasVstPermission(id = str(request.currentUser.id), menu = "Option")
        if not request.currentUser.isAdmin:
            if hasPermission == False:
                messages.error(request, "Not Permission")
                return JsonResponse({'deleted': False, 'message': 'Not Permission'})
        if not id:
            return JsonResponse({'deleted': False, 'message': 'Not found id'})
        option: Option = Option.objects.filter(id = id).first()
        if not option:
            return JsonResponse({'deleted': False, 'message': 'Option not found'})
        option.isActive = False
        option.updateDate = timezone.now()
        currentUser: User = request.currentUser
        if currentUser:
            uDelete = UserSnapshot().UserToSnapshot(currentUser)
            if uDelete:
                option.updateBy = uDelete
        option.save()
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