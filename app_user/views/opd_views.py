import datetime
import json
from typing import List
from bson import ObjectId
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
import pytz

from app_organization.models.organization import Organization
from app_user.models.family import FamilyProfile, FamilyType, UserFamily
from app_user.models.opd import BudgetEmpType, BudgetOpd, DisbursementOpd, OPDRecord, OpdType, OptionOpd
from app_user.models.user import EmpNation, User, UserStatus, UserType
from app_user.utils import HasUsPermission, requiredLogin
from base_models.basemodel import UserSnapshot
from utilities.utility import DateStrToDate

@requiredLogin
def index(request: HttpRequest):
    hasPermission = HasUsPermission(id = str(request.currentUser.id), menu = "Opd-Admin")
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    listUser: List[User] = User.objects.filter(isActive = True, status = UserStatus.Hire, userType = UserType.Employee)
    listBudget = BudgetOpd.objects.filter(isActive = True)
    budgTH = listBudget.filter(type = BudgetEmpType.Thai).first()
    budgFore = listBudget.filter(type = BudgetEmpType.Foreigner).first()
    users = []
    for us in listUser:
        listDept = findDeptUser(us)
        depts = []
        if len(listDept) > 0:
            for de in listDept:
                depts.append(de['nameEN'])
        budget = 0
        if us.nation == EmpNation.Thai:
            budget = budgTH.budget
        else:
            budget = budgFore.budget
        actual = 0
        year = timezone.now().year
        start_date = datetime.datetime(year, 1, 1, tzinfo=pytz.UTC)
        end_date = datetime.datetime(year + 1, 1, 1, tzinfo=pytz.UTC)
        findOpdRecord: List[OPDRecord] = OPDRecord.objects.filter(
            isActive = True,
            employee = us,
            inputDate__gte = start_date,
            inputDate__lt = end_date,
            ).order_by('-inputDate')
        if findOpdRecord and len(findOpdRecord) > 0:
            for opd in findOpdRecord:
                actual += opd.totalAmount if opd.totalAmount else 0
        balance = budget - actual
        userObj = {
            'id': str(us.id),
            'code': us.code if us.code else "-",
            'fNameEN': us.fNameEN if us.fNameEN else "-",
            'lNameEN': us.lNameEN if us.lNameEN else "-",
            'dept': depts if len(depts) > 0 else "-",
            'budget': f"{budget:,.2f}",
            'actual': f"{actual:,.2f}",
            'balance': balance,
            'balance_display': f"{balance:,.2f}" if balance is not None else "-"
        }
        users.append(userObj)
    context = {
        'users': users
    }

    return render(request, 'opd/index_opd.html', context)

@requiredLogin
def historyOpd(request: HttpRequest, id: str):
    employee: User = User.objects.filter(id = ObjectId(id)).first()
    budget = '-'
    if employee.nation == EmpNation.Thai:
        budget: BudgetOpd = BudgetOpd.objects.filter(isActive = True, type = BudgetEmpType.Thai).first()
    else:
        budget: BudgetOpd = BudgetOpd.objects.filter(isActive = True, type = BudgetEmpType.Foreigner).first()
    year = timezone.now().year
    start_date = datetime.datetime(year, 1, 1, tzinfo=pytz.UTC)
    end_date = datetime.datetime(year + 1, 1, 1, tzinfo=pytz.UTC)
    findOpdRecord: List[OPDRecord] = OPDRecord.objects.filter(
        isActive = True,
        employee = ObjectId(id),
        inputDate__gte = start_date,
        inputDate__lt = end_date,
        ).order_by('-inputDate')
    actual = 0
    histories = []
    totalFather = 0
    totalMother = 0
    totalSpouse = 0
    totalChildren = 0
    totalEmployee = 0
    if findOpdRecord and len(findOpdRecord) > 0:
        for opd in findOpdRecord:
            actual += opd.totalAmount if opd.totalAmount else 0
            for disb in opd.disbursements:
                if disb.type == OpdType.Family:
                    if disb.familyMember.relation == FamilyType.Father:
                        totalFather += disb.amount if disb.amount else 0
                    elif disb.familyMember.relation == FamilyType.Mother:
                        totalMother += disb.amount if disb.amount else 0
                    elif disb.familyMember.relation == FamilyType.Spouse:
                        totalSpouse += disb.amount if disb.amount else 0
                    elif disb.familyMember.relation == FamilyType.Children:
                        totalChildren += disb.amount if disb.amount else 0
                elif disb.type == OpdType.Employee:
                    totalEmployee += disb.amount if disb.amount else 0
                histories.append({
                    'inputDate': opd.inputDate.astimezone(pytz.timezone('Asia/Bangkok')).strftime('%Y-%m-%d'),
                    'type': disb.type.name,
                    'option': disb.refOption.name if disb.refOption else '-',
                    'amount': f"{disb.amount:,.2f}" if disb.amount else 0,
                    'person': f"{employee.fNameEN} {employee.lNameEN}" if disb.type == OpdType.Employee else f"{disb.familyMember.fName} {disb.familyMember.lName}" if disb.familyMember else '-',
                })

    # print([history for history in histories])
    
    summarize = [
        {'relation': f'({employee.code}) {employee.fNameEN} {employee.lNameEN}', 'amount': f"{totalEmployee:,.2f}"},
        {'relation': 'Father', 'amount': f"{totalFather:,.2f}"},
        {'relation': 'Mother', 'amount': f"{totalMother:,.2f}"},
        {'relation': 'Spouse', 'amount': f"{totalSpouse:,.2f}"},
        {'relation': 'Children', 'amount': f"{totalChildren:,.2f}"},
    ]

    balance_value = (budget.budget - actual) if budget else None
    context = {
        'year': year,
        'employee': employee,
        'budget': "{:,.2f}".format(budget.budget) if budget else '-',
        'actual': "{:,.2f}".format(actual),
        'balance': balance_value,
        'balance_display': f"{balance_value:,.2f}" if balance_value is not None else '-',
        'histories': histories,
        'summarize': summarize,
    }
    return render(request, 'opd/history_opd.html', context)

@requiredLogin
def listPageOpd(request: HttpRequest):
    hasPermission = HasUsPermission(id = str(request.currentUser.id), menu = "Opd-Admin")
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    listUserData: List[User] = User.objects.filter(isActive = True, status = UserStatus.Hire.value).order_by('code')
    users = [ user.serialize() for user in listUserData]
    context = {
        'users': users
    }
    return render(request, 'opd/list_opd.html', context)

@requiredLogin
def filterSearchOpd(request: HttpRequest):
    try:
        if not request.method == "POST":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        
        body = json.loads(request.body.decode('utf-8'))  # อ่าน JSON body
        sDate = body.get('sDate')
        eDate = body.get('eDate')
        user = body.get('user')
        if sDate or eDate or user != "None":
            if sDate:
                sDate = DateStrToDate(sDate)
            if eDate:
                eDate = DateStrToDate(eDate)
            filterParams = {'isActive': True}
            if user != "None":
                filterParams['employee'] = ObjectId(user)
            if sDate and eDate:
                filterParams['inputDate__gte'] = sDate
                filterParams['inputDate__lt'] = eDate + datetime.timedelta(days=1)
            elif sDate:
                filterParams['inputDate__gte'] = sDate
            elif eDate:
                filterParams['inputDate__lt'] = eDate + datetime.timedelta(days=1)
            opdRecords: List[OPDRecord] = OPDRecord.objects.filter(**filterParams).order_by('-inputDate')
            data = []
            if opdRecords and len(opdRecords) > 0:
                for opd in opdRecords:
                    empData: User = opd.employee
                    data.append({
                        'id': str(opd.id),
                        'empCode': empData.code if empData and empData.code else '-',
                        'empName': f"{empData.fNameEN} {empData.lNameEN}" if empData else '-',
                        'inputDate': opd.inputDate.astimezone(pytz.timezone('Asia/Bangkok')).strftime('%Y-%m-%d') if opd.inputDate else '-',
                        'totalAmount': f"{opd.totalAmount:,.2f}" if opd.totalAmount else '0.00',
                    })
            return JsonResponse({'success': True, 'data': data})

        return JsonResponse({'success': True, 'data': []})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})

@requiredLogin
def addOpd(request: HttpRequest, id: str):
    hasPermission = HasUsPermission(id = str(request.currentUser.id), menu = "Opd-Admin")
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    if not id:
        messages.error(request, "Id not found.")
        return HttpResponseRedirect(reverse('indexOpd'))
    employee: User = User.objects.filter(id = ObjectId(id)).first()
    if not employee:
        messages.error(request, "Employee not found.")
        return HttpResponseRedirect(reverse('indexOpd'))
    famData: UserFamily = UserFamily.objects.filter(employee = ObjectId(id)).first()
    usFamily = '-'
    if famData:
        usFamily = famData.serialize_datatable()
    allOption: List[OptionOpd] = OptionOpd.objects.filter(isActive = True, status = True)
    empOptions = []
    familyOptions = []
    for emp in allOption:
        if OpdType.Employee in emp.useTypes:
            empOptions.append(emp.serialize())
        if OpdType.Family in emp.useTypes:
            familyOptions.append(emp.serialize())

    listDept = findDeptUser(employee)
    depts = []
    if len(listDept) > 0:
        for de in listDept:
            depts.append(de['nameEN'])

    budget = '-'
    if employee.nation == EmpNation.Thai:
        budget: BudgetOpd = BudgetOpd.objects.filter(isActive = True, type = BudgetEmpType.Thai).first()
    else:
        budget: BudgetOpd = BudgetOpd.objects.filter(isActive = True, type = BudgetEmpType.Foreigner).first()

    year = timezone.now().year
    start_date = datetime.datetime(year, 1, 1, tzinfo=pytz.UTC)
    end_date = datetime.datetime(year + 1, 1, 1, tzinfo=pytz.UTC)
    findOpdRecord: List[OPDRecord] = OPDRecord.objects.filter(
        isActive = True,
        employee = ObjectId(id),
        inputDate__gte = start_date,
        inputDate__lt = end_date,
        ).order_by('-inputDate')
    print(findOpdRecord)
    actual = 0
    histories = []
    if findOpdRecord and len(findOpdRecord) > 0:
        for opd in findOpdRecord:
            actual += opd.totalAmount if opd.totalAmount else 0
            for disb in opd.disbursements:
                histories.append({
                    'inputDate': opd.inputDate.astimezone(pytz.timezone('Asia/Bangkok')).strftime('%Y-%m-%d'),
                    'type': disb.type.name,
                    'option': disb.refOption.name if disb.refOption else '-',
                    'amount': f"{disb.amount:,.2f}" if disb.amount else 0,
                    'person': f"{employee.fNameEN} {employee.lNameEN}" if disb.type == OpdType.Employee else f"{disb.familyMember.fName} {disb.familyMember.lName}" if disb.familyMember else '-',
                })

    balance_value = (budget.budget - actual) if budget else None
    context = {
        'year': year,
        'employee': employee,
        'usFamily': usFamily,
        'empOptions': empOptions,
        'empOptionLength': len(empOptions),
        'familyOptions': familyOptions,
        'famOptionLength': len(familyOptions) + 1,
        'depts': depts,
        'budget': "{:,.2f}".format(budget.budget) if budget else '-',
        'actual': "{:,.2f}".format(actual),
        'balance': balance_value,
        'balance_display': f"{balance_value:,.2f}" if balance_value is not None else '-',
        'histories': histories,
    }
    return render(request, 'opd/add_opd.html', context)

@requiredLogin
def addOpdJson(request: HttpRequest):
    try:
        if not request.method == "POST":
            return JsonResponse({
                'success': False,
                "message": "Method not allowed"
            }, status=405)
        
        body = json.loads(request.body.decode('utf-8'))  # อ่าน JSON body
        empid = body.get('empid')
        inputdate = body.get('inputdate')
        hospital = body.get('hospital')
        employee = body.get('employee')
        father = body.get('father')
        mother = body.get('mother')
        spouse = body.get('spouse')
        children = body.get('children')

        if not empid:
            return JsonResponse({'success': False, "message": "Employee Id not found"})
        empData = User.objects.filter(id = ObjectId(empid)).first()
        if not empData:
            return JsonResponse({'success': False, "message": "Employee not found"})
        if not inputdate:
            return JsonResponse({'success': False, "message": "Input date not found"})
        if not hospital:
            return JsonResponse({'success': False, "message": "Hospital not found"})
        
        inputdate = DateStrToDate(inputdate)
        if not inputdate:
            return JsonResponse({'success': False, "message": "Invalid input date format"})

        if (not employee or len(employee) == 0) and (not father or len(father) == 0) and (not mother or len(mother) == 0) and (not spouse or len(spouse) == 0) and (not children or len(children) == 0):
            return JsonResponse({'success': False, "message": "No data to submit"})

        sumAmountEmployee = sumAmountDisburse(employee)
        sumAmountFather = sumAmountDisburse(father)
        sumAmountMother = sumAmountDisburse(mother)
        sumAmountSpouse = sumAmountDisburse(spouse)
        sumAmountChild = sumAmountDisburse(children)
        print(sumAmountChild)

        opdRecord = OPDRecord()
        opdRecord.employee = empData
        opdRecord.inputDate = inputdate
        opdRecord.totalAmount = sumAmountEmployee + sumAmountFather + sumAmountMother + sumAmountSpouse + sumAmountChild
        opdRecord.hospital = hospital
        opdRecord.isActive = True
        disbursements = []
        if employee and len(employee) > 0:
            disbursements.extend(toDisbursementOpd(employee, OpdType.Employee, None))
        if father and len(father) > 0:
            disbursements.extend(toDisbursementOpd(father, OpdType.Family, FamilyType.Father))
        if mother and len(mother) > 0:
            disbursements.extend(toDisbursementOpd(mother, OpdType.Family, FamilyType.Mother))
        if spouse and len(spouse) > 0:
            disbursements.extend(toDisbursementOpd(spouse, OpdType.Family, FamilyType.Spouse))
        if children and len(children) > 0:
            disbursements.extend(toDisbursementOpd(children, OpdType.Family, FamilyType.Children))
        opdRecord.disbursements = disbursements
        curUser:User = request.currentUser
        if curUser:
            uCreate = UserSnapshot().UserToSnapshot(curUser)
            if uCreate:
                opdRecord.createBy = uCreate
        opdRecord.createDate = timezone.now()
        opdRecord.save()
        
        return JsonResponse({
            'success': True,
            "message": "Success"
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            "message": str(e)
        }, status=500)
    
@requiredLogin
def editOpd(request: HttpRequest, id: str):
    hasPermission = HasUsPermission(id = str(request.currentUser.id), menu = "Opd-Admin")
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
    if not id:
        messages.error(request, "Id not found.")
        return HttpResponseRedirect(reverse('listOpd'))
    opdRecord: OPDRecord = OPDRecord.objects.filter(id = ObjectId(id)).first()
    if not opdRecord:
        messages.error(request, "OPD Record not found.")
        return HttpResponseRedirect(reverse('listOpd'))
    employee: User = User.objects.filter(id = opdRecord.employee.id).first()
    if not employee:
        messages.error(request, "Employee not found.")
        return HttpResponseRedirect(reverse('listOpd'))
    allOption: List[OptionOpd] = OptionOpd.objects.filter(isActive = True, status = True)
    empOptions = []
    familyOptions = []
    for emp in allOption:
        if OpdType.Employee in emp.useTypes:
            amountEmpOption = ""
            for opd in opdRecord.disbursements:
                if opd.type == OpdType.Employee and opd.refOption.id == emp.id:
                    amountEmpOption = opd.amount
            empOptions.append({
                'id': str(emp.id),
                'name': emp.name,
                'amount': amountEmpOption
            })
        if OpdType.Family in emp.useTypes:
            amountFamilyOption = ""
            famRelation = ""
            famProf = ""
            for opd in opdRecord.disbursements:
                if opd.type == OpdType.Family and opd.refOption.id == emp.id:
                    amountFamilyOption = opd.amount
                    famRelation = opd.familyMember.relation.name
                    famProf = f"{opd.familyMember.fName} {opd.familyMember.lName}"
            familyOptions.append({
                'id': str(emp.id),
                'name': emp.name,
                'amount': amountFamilyOption,
                'relation': famRelation,
                'famProf': famProf
            })
    listDept = findDeptUser(employee)
    depts = []
    if len(listDept) > 0:
        for de in listDept:
            depts.append(de['nameEN'])
    famData: UserFamily = UserFamily.objects.filter(employee = employee.id).first()
    usFamily = '-'
    if famData:
        usFamily = famData.serialize_datatable()

    budget = '-'
    if employee.nation == EmpNation.Thai:
        budget: BudgetOpd = BudgetOpd.objects.filter(isActive = True, type = BudgetEmpType.Thai).first()
    else:
        budget: BudgetOpd = BudgetOpd.objects.filter(isActive = True, type = BudgetEmpType.Foreigner).first()

    year = timezone.now().year
    start_date = datetime.datetime(year, 1, 1, tzinfo=pytz.UTC)
    end_date = datetime.datetime(year + 1, 1, 1, tzinfo=pytz.UTC)
    findOpdRecord: List[OPDRecord] = OPDRecord.objects.filter(
        isActive = True,
        employee = employee.id,
        inputDate__gte = start_date,
        inputDate__lt = end_date,
        ).order_by('-inputDate')
    actual = 0
    histories = []
    if findOpdRecord and len(findOpdRecord) > 0:
        for opd in findOpdRecord:
            actual += opd.totalAmount if opd.totalAmount else 0
            for disb in opd.disbursements:
                histories.append({
                    'inputDate': opd.inputDate.astimezone(pytz.timezone('Asia/Bangkok')).strftime('%Y-%m-%d'),
                    'type': disb.type.name,
                    'option': disb.refOption.name if disb.refOption else '-',
                    'amount': f"{disb.amount:,.2f}" if disb.amount else 0,
                    'person': f"{employee.fNameEN} {employee.lNameEN}" if disb.type == OpdType.Employee else f"{disb.familyMember.fName} {disb.familyMember.lName}" if disb.familyMember else '-',
                })

    balance_value = (budget.budget - actual) if budget else None
    context = {
        'employee': employee,
        'empOptions': empOptions,
        'familyOptions': familyOptions,
        'empOptionLength': len(empOptions),
        'famOptionLength': len(familyOptions) + 1,
        'usFamily': usFamily,
        'depts': depts,
        'opdRecord': opdRecord.serialize(),
        'budget': "{:,.2f}".format(budget.budget) if budget else '-',
        'actual': "{:,.2f}".format(actual),
        'balance': balance_value,
        'balance_display': f"{balance_value:,.2f}" if balance_value is not None else '-',
        'histories': histories,
        'year': year,
    }
    return render(request, 'opd/edit_opd.html', context)

@requiredLogin
def editOpdJson(request: HttpRequest):
    try:
        if not request.method == "POST":
            return JsonResponse({ 'success': False, "message": "Method not allowed"})
        body = json.loads(request.body.decode('utf-8'))  # อ่าน JSON body
        opdId = body.get('opdId')
        if not opdId:
            return JsonResponse({ 'success': False, "message": "OPD Id not found"})
        opdRecord: OPDRecord = OPDRecord.objects.filter(id = ObjectId(opdId)).first()
        if not opdRecord:
            return JsonResponse({ 'success': False, "message": "OPD Record not found"})
        inputdate = body.get('inputdate')
        hospital = body.get('hospital')
        employee = body.get('employee')
        father = body.get('father')
        mother = body.get('mother')
        spouse = body.get('spouse')
        children = body.get('children')
        if not inputdate:
            return JsonResponse({ 'success': False, "message": "Input date not found"})
        if not hospital:
            return JsonResponse({ 'success': False, "message": "Hospital not found"})
        inputdate = DateStrToDate(inputdate)
        if not inputdate:
            return JsonResponse({ 'success': False, "message": "Invalid input date format"})
        if (not employee or len(employee) == 0) and (not father or len(father) == 0) and (not mother or len(mother) == 0) and (not spouse or len(spouse) == 0) and (not children or len(children) == 0):
            return JsonResponse({ 'success': False, "message": "No data to submit"})
        sumAmountEmployee = sumAmountDisburse(employee)
        sumAmountFather = sumAmountDisburse(father)
        sumAmountMother = sumAmountDisburse(mother)
        sumAmountSpouse = sumAmountDisburse(spouse)
        sumAmountChild = sumAmountDisburse(children)
        opdRecord.inputDate = inputdate
        opdRecord.totalAmount = sumAmountEmployee + sumAmountFather + sumAmountMother + sumAmountSpouse + sumAmountChild
        opdRecord.hospital = hospital
        disbursements = []
        if employee and len(employee) > 0:
            disbursements.extend(toDisbursementOpd(employee, OpdType.Employee, None))
        if father and len(father) > 0:
            disbursements.extend(toDisbursementOpd(father, OpdType.Family, FamilyType.Father))
        if mother and len(mother) > 0:
            disbursements.extend(toDisbursementOpd(mother, OpdType.Family, FamilyType.Mother))
        if spouse and len(spouse) > 0:
            disbursements.extend(toDisbursementOpd(spouse, OpdType.Family, FamilyType.Spouse))
        if children and len(children) > 0:
            disbursements.extend(toDisbursementOpd(children, OpdType.Family, FamilyType.Children))
        opdRecord.disbursements = disbursements
        curUser:User = request.currentUser
        if curUser:
            uModify = UserSnapshot().UserToSnapshot(curUser)
            if uModify:
                opdRecord.updateBy = uModify
        opdRecord.updateDate = timezone.now()
        opdRecord.save()
        return JsonResponse({ 'success': True, "message": "Success"})
    except Exception as e:
        return JsonResponse({ 'success': False, "message": str(e)})
    
@requiredLogin
def deleteOpdJson(request: HttpRequest, id:str):
    try:
        if not request.method == "GET":
            return JsonResponse({ 'success': False, "message": "Method not allowed"})
        if not id:
            return JsonResponse({ 'success': False, "message": "Id not found"})
        opdRecord: OPDRecord = OPDRecord.objects.filter(id = ObjectId(id)).first()
        if not opdRecord:
            return JsonResponse({ 'success': False, "message": "OPD Record not found"})
        opdRecord.isActive = False
        curUser:User = request.currentUser
        if curUser:
            uModify = UserSnapshot().UserToSnapshot(curUser)
            if uModify:
                opdRecord.updateBy = uModify
        opdRecord.updateDate = timezone.now()
        opdRecord.save()
        return JsonResponse({ 'success': True, "message": "Success"})
    except Exception as e:
        return JsonResponse({ 'success': False, "message": str(e)})


def sumAmountDisburse(disburseTypeArr: List[dict]):
    totalAmount = 0
    for dt in disburseTypeArr:
        totalAmount += float(dt['amount'])
    return totalAmount

def toDisbursementOpd(dataArr: List[dict], opdType: OpdType, FamilyType: FamilyType):
    disbursements = []
    for dt in dataArr:
        option = OptionOpd.objects.filter(id = ObjectId(dt['opId'].split("-")[1])).first()
        if option:
            disbursement = DisbursementOpd()
            disbursement.type = opdType
            disbursement.refOption = option
            if opdType == OpdType.Family:
                disbursement.familyMember = FamilyProfile(fName = dt['fName'], lName = dt['lName'], relation = FamilyType)
            disbursement.amount = float(dt['amount'])
            disbursements.append(disbursement)
    return disbursements

def getChildLevel(org: Organization, targetLevel: str):
    results = []
    # หา child ทั้งหมดที่ parent = org
    children = Organization.objects.filter(isActive = True,parent=org)
    for child in children:
        if child.level and child.level.nameEN == targetLevel:
            # print(child.serialize_organization()['levelNameEN'])
            results.append(child.serialize_organization())
        # หาในระดับลึกต่อ (เช่น Factory → Department → Section)
        results.extend(getChildLevel(child, targetLevel))
    return results

def  getParentLevel(org: Organization, targetLevel: str):
    parent: Organization = org.parent
    while parent:
        # ตรวจสอบว่าระดับของ parent คือ Department หรือไม่
        if parent.level and parent.level.nameEN == targetLevel:
            return parent.serialize_organization()  # หรือ return parent.serialize_organization() ถ้าอยากได้ข้อมูลครบ
        parent = parent.parent
    return None  # ถ้าไม่มี parent ที่เป็น Department

def findDeptUser(cur: User):
    roles = []
    roleOthers = []
    roleDepts = []
    if not cur.roles:
        return roles
    
    for r in cur.roles:
        if r.isActive == True:
            if r.orgId.level.nameEN == "Department":
                roleDepts.append(r.orgId.serialize_organization())
            elif r.orgId.level.nameEN == "Managing Director":
                roleOthers.extend(getChildLevel(r.orgId, "Department"))
            elif r.orgId.level.nameEN == "Division":
                roleOthers.extend(getChildLevel(r.orgId, "Department"))
            else:
                roleOthers.append(getParentLevel(r.orgId, "Department"))

    if roleDepts:
        for d in roleDepts:
            if d not in roles:
                roles.append(d)

    if roleOthers:
        for r in roleOthers:
            if r not in roles:
                roles.append(r)
    return roles