from typing import List
from bson import ObjectId
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.utils import timezone

from app_user.models.opd import BudgetEmpType, BudgetOpd, OpdType, OptionOpd
from app_user.models.user import User
from app_user.utils import requiredLogin
from base_models.basemodel import UserSnapshot

# ------------------------------------
# ----------- Budget OPD -------------
# ------------------------------------

@requiredLogin
def budgetOpd(request: HttpRequest):
    return render(request, "opd/budget_setting.html")

@requiredLogin
def filterBudgetOpd(request: HttpRequest, type: str):
    try:
        if not request.method == "GET":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        findData: List[BudgetOpd] = BudgetOpd.objects.filter(isActive = True, type = int(type))
        budgetOpds = []
        if findData:
            budgetOpds = [ bud.serialize() for bud in findData ]
        return JsonResponse({'success': True, 'data': budgetOpds, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})
    
@requiredLogin
def getBudgetOpd(request: HttpRequest, id: str):
    try:
        if not request.method == "GET":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        if not id:
            return JsonResponse({'success': False, 'message': 'Id is required'})
        id = ObjectId(id)
        budget: BudgetOpd = BudgetOpd.objects.filter(id=id).first()
        if not budget:
            return JsonResponse({'success': False, 'message': 'Budget not found'})
        return JsonResponse({'success': True, 'data': budget.serialize(), 'message': 'Success'})
        
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})

@requiredLogin
def addBudgetOpd(request: HttpRequest):
    try:
        if not request.method =="POST":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        year = request.POST.get('year')
        budget = request.POST.get('budget')
        status = request.POST.get('status')
        addtype = request.POST.get('addtype')

        if not year:
            return JsonResponse({'success': False, 'message': 'Year is required'})
        if not budget:
            return JsonResponse({'success': False, 'message': 'Budget is required'})
        
        dup = BudgetOpd.objects.filter(year=year, isActive = True, type = int(addtype))
        if dup:
            return JsonResponse({'success': False, 'message': 'Year already exists'})
        findActive  = BudgetOpd.objects.filter(status = True, type = int(addtype))
        if findActive:
            return JsonResponse({'success': False, 'message': 'Can not add, Other Budget has Active'})
        budgetOpd = BudgetOpd()
        budgetOpd.year = year
        budgetOpd.budget = float(budget)
        budgetOpd.status = True if status == "true" else False
        budgetOpd.isActive = True
        budgetOpd.type = BudgetEmpType(int(addtype))
        curUser:User = request.currentUser
        if curUser:
            uCreate = UserSnapshot().UserToSnapshot(curUser)
            if uCreate:
                budgetOpd.createBy = uCreate
        budgetOpd.createDate = timezone.now()
        budgetOpd.save()

        return JsonResponse({'success': True, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})
    
@requiredLogin
def editBudgetOpd(request: HttpRequest):
    try:
        if not request.method =="POST":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        id = request.POST.get('id')
        budget = request.POST.get('budget')
        status = request.POST.get('status')
        edittype = request.POST.get('edittype')
        if not id:
            return JsonResponse({'success': False, 'message': 'Id is required'} )
        if not budget:
            return JsonResponse({'success': False, 'message': 'Budget is required'})
        if status == "true":
            findActive  = BudgetOpd.objects.filter(status = True, type = int(edittype))
            if findActive:
                return JsonResponse({'success': False, 'message': 'Can not edit, Other Budget has Active'})
        
        id = ObjectId(id)
        budgetOpd: BudgetOpd = BudgetOpd.objects.filter(id=id).first()
        if not budgetOpd:
            return JsonResponse({'success': False, 'message': 'Budget not found'})
        
        budgetOpd.budget = float(budget)
        budgetOpd.status = True if status == "true" else False
        curUser:User = request.currentUser
        if curUser:
            uUpdate = UserSnapshot().UserToSnapshot(curUser)
            if uUpdate:
                budgetOpd.updateBy = uUpdate
        budgetOpd.updateDate = timezone.now()
        budgetOpd.save()

        return JsonResponse({'success': True, 'message': 'Success'})

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})
    

@requiredLogin
def deleteBudgetOpd(request: HttpRequest, id: str):
    try:
        if not request.method =="DELETE":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        if not id:
            return JsonResponse({'success': False, 'message': 'Id is required'})
        id = ObjectId(id)
        budgetOpd: BudgetOpd = BudgetOpd.objects.filter(id=id).first()
        if not budgetOpd:
            return JsonResponse({'success': False, 'message': 'Budget not found'})
        budgetOpd.isActive = False
        budgetOpd.status = False
        curUser:User = request.currentUser
        if curUser:
            uDelete = UserSnapshot().UserToSnapshot(curUser)
            if uDelete:
                budgetOpd.updateBy = uDelete
        budgetOpd.updateDate = timezone.now()
        budgetOpd.save()

        return JsonResponse({'success': True, 'message': 'Success'})

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})
    
# ------------------------------------
# ----------- Option OPD -------------
# ------------------------------------
@requiredLogin
def optionOpd(request: HttpRequest):
    opdTypes = []
    for ut in OpdType:
        opdTypes.append({
            "name": ut.name,
            "value": ut.value
        })
    context = {
        "opdTypes": opdTypes
    }
    return render(request, "opd/option_setting.html", context)

@requiredLogin
def filterOptionOpd(request: HttpRequest):
    try:
        if not request.method == "GET":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        options = []
        findData: List[OptionOpd] = OptionOpd.objects.filter(isActive = True)
        if findData:
            options = [ opt.serialize() for opt in findData ]
        return JsonResponse({'success': True, 'data': options, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})
    
@requiredLogin
def getOptionOpd(request: HttpRequest, id: str):
    try:
        if not request.method == "GET":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        if not id:
            return JsonResponse({'success': False, 'message': 'Id is required'})
        id = ObjectId(id)
        option: OptionOpd = OptionOpd.objects.filter(id = id).first()
        if not option:
            return JsonResponse({'success': False, 'message': 'Option not fonud'})
        return JsonResponse({'success': True, 'data': option.serialize(), 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})

@requiredLogin
def addOptionOpd(request: HttpRequest):
    try:
        if not request.method == "POST":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        name = request.POST.get('name')
        usefor = request.POST.getlist('usefor')
        desc = request.POST.get('desc')
        status = request.POST.get('status')
        if not name:
            return JsonResponse({'success': False, 'message': 'Name is required'})
        if not usefor and len(usefor) == 0:
            return JsonResponse({'success': False, 'message': 'Use For is required'})
        dup = OptionOpd.objects.filter(name = name, isActive = True)
        if dup:
            return JsonResponse({'success': False, 'message': 'Option is already exists.'})
        
        option: OptionOpd = OptionOpd()
        option.name = name
        useTypes = []
        for us in usefor:
            useTypes.append(OpdType(int(us)).value)
        
        option.useTypes = useTypes
        option.description = desc
        option.status = True if status == "true" else False
        option.isActive = True
        curUser:User = request.currentUser
        if curUser:
            uCreate = UserSnapshot().UserToSnapshot(curUser)
            if uCreate:
                option.createBy = uCreate
        option.createDate = timezone.now()
        option.save()

        return JsonResponse({'success': True, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})
    
@requiredLogin
def editOptionOpd(request: HttpRequest):
    try:
        if not request.method =="POST":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        id = request.POST.get('id')
        name = request.POST.get('name')
        usefor = request.POST.getlist('usefor')
        desc = request.POST.get('desc')
        status = request.POST.get('status')
        if not id:
            return JsonResponse({'success': False, 'message': 'Id is required'} )
        if not name:
            return JsonResponse({'success': False, 'message': 'Name is required'})
        if not usefor and len(usefor) == 0:
            return JsonResponse({'success': False, 'message': 'Use For is required'})
        id = ObjectId(id)
        dup = OptionOpd.objects.filter(id__ne = id,name = name, isActive = True)
        if dup:
            return JsonResponse({'success': False, 'message': 'Option is already exists.'})
        option: OptionOpd = OptionOpd.objects.filter(id = id).first()
        if not option:
            return JsonResponse({'success': False, 'message': 'Option not found'})
        option.name = name
        useTypes = []
        for us in usefor:
            useTypes.append(OpdType(int(us)).value)
        
        option.useTypes = useTypes
        option.description = desc
        option.status = True if status == "true" else False
        curUser:User = request.currentUser
        if curUser:
            uUdate = UserSnapshot().UserToSnapshot(curUser)
            if uUdate:
                option.updateBy = uUdate
        option.updateDate = timezone.now()
        option.save()
        return JsonResponse({'success': True, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})
    
@requiredLogin
def deleteOptionOpd(request: HttpRequest, id: str):
    try:
        if not request.method =="DELETE":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        if not id:
            return JsonResponse({'success': False, 'message': 'Id is required'})
        id = ObjectId(id)
        option: OptionOpd = OptionOpd.objects.filter(id = id).first()
        if not option:
            return JsonResponse({'success': False, 'message': 'Option not found'})
        option.isActive = False
        option.status = False
        curUser:User = request.currentUser
        if curUser:
            uUdate = UserSnapshot().UserToSnapshot(curUser)
            if uUdate:
                option.updateBy = uUdate
        option.updateDate = timezone.now()
        option.save()
        return JsonResponse({'success': True, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})