import datetime
import json
import re
from typing import List
from bson import ObjectId
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
from django.utils import timezone
import pytz

from app_organization.models.level import Level
from app_organization.models.organization import Organization
from app_organization.models.position import Position
from app_safety_system.models.greenyellow_card import GreenYellowCard, GreenYellowType, IssueToType, Issuer, YellowCardType
from app_safety_system.utils import sendMailGreenYellowCard
from app_user.models.user import EmpNation, User, UserStatus
from app_user.utils import requiredLogin
from base_models.basemodel import UserSnapshot
from utilities.utility import DateStrToDate, findDeptUser, printLogData

MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB
uploadDir = 'greenyellowcard'

@requiredLogin
def index(request: HttpRequest):
    issueTypes = [
        item for item in IssueToType
    ]
    yellowCardTypes = [
        {"value": t.value, "label": f"{t.labels['th']} / {t.labels['en']}"} 
        for t in YellowCardType
    ]
    cur: User = request.currentUser
    
    # -- select dept org สำหรับ thai เมื่อกรณีอยู่หลาย org
    roles = []
    isEmpThai = False
    if cur.nation == EmpNation.Thai:
        isEmpThai = True
        roles = findDeptUser(cur)
    
    # print(roles)
    # print(cur.nation.name)

    # -- เมื่อ emp thai มีการย้าย org ให้เอาใบเขียวเหลืองของปีปัจจุบันติดตัวไป org ใหม่ ด้วย
    changeDept = False
    if cur.nation == EmpNation.Thai:
        year = timezone.now().year
        start_date = datetime.datetime(year, 1, 1, tzinfo=pytz.UTC)
        end_date = datetime.datetime(year + 1, 1, 1, tzinfo=pytz.UTC)
        listData: List[GreenYellowCard] = GreenYellowCard.objects.filter(
                isActive = True, 
                issueDate__gte=start_date,
                issueDate__lt=end_date,
                issuer__userId = cur.id
                )
        tempRoles = [item['id'] for item in roles]
        tempRolesName = [item['nameEN'] for item in roles]
        
        for card in listData:
            if card.deptId in tempRoles:
                # -- ถ้า org ตรงไม่ต้องทำไร
                print(card.deptNameEN)
            else:
                if len(tempRoles) > 1:
                    # -- ถ้ามีหลาย org ให้ส่ง fag ไปที่ html
                    # -- ให้ user เลือก dept ใน html
                    changeDept = True
                else:
                    # -- เปลี่ยน org ของใบเขียวเหลือง
                    card.deptId = tempRoles[0]
                    card.deptNameEN = tempRolesName[0]
                    card.updateDate = timezone.now()
                    card.save()
    
    context = {
        "issueTypes": issueTypes,
        "yellowCardTypes": yellowCardTypes,
        "selectRoles": roles,
        "isEmpThai": isEmpThai,
        "changeDept": changeDept
    }
    return render(request, 'greencard/index.html', context)

@requiredLogin
def search(request: HttpRequest):
    cardTypes = [
        item for item in GreenYellowType
    ]
    listUserData: List[User] = User.objects.filter(isActive = True, status = UserStatus.Hire.value).order_by('code')
    users = [ user.serialize() for user in listUserData]
    listOrgData: List[Organization] = Organization.objects.filter(isActive = True).order_by('level')
    orgs = [ org.serialize_organization() for org in listOrgData]
    yellowCardTypes = [
        {"value": t.value, "label": f"{t.labels['th']} / {t.labels['en']}"} 
        for t in YellowCardType
    ]

    context = {
        "cardTypes": cardTypes,
        "users": users,
        "orgs": orgs,
        "yellowCardTypes": yellowCardTypes
    }
    return render(request, 'greencard/search.html', context)

@requiredLogin
def filterGreenYellowCardJson(request: HttpRequest):
    try:
        if not request.method == "POST":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        body = json.loads(request.body.decode('utf-8'))  # อ่าน JSON body
        sDate = body.get('sDate')
        eDate = body.get('eDate')
        cardType = body.get('cardType')
        user = body.get('user')
        org = body.get('org')
        yellowCardTypes = body.get('yellowCardTypes')

        if sDate or eDate or cardType or user != "None" or org != "None" or yellowCardTypes != "None":
            greenYellowCards: List[GreenYellowCard] = GreenYellowCard.objects.filter(isActive = True)
            if sDate:
                sDate = DateStrToDate(sDate)
                greenYellowCards = greenYellowCards.filter(issueDate__gte = sDate)
            if eDate:
                eDate = DateStrToDate(eDate)
                greenYellowCards = greenYellowCards.filter(issueDate__lte = eDate)
            if cardType:
                cardType = int(cardType)
                greenYellowCards = greenYellowCards.filter(type = cardType)
            if user and user != "None":
                greenYellowCards = greenYellowCards.filter(issuer__userId=ObjectId(user))
            if org and org != "None":
                org_id = ObjectId(org)
                orgList = []
                child: List[Organization] = Organization.objects.filter(parent=org_id).all()
                if child:
                    for c in child:
                        # org_id = c.id
                        orgList.append(c.id)
                orgList.append(org_id)
                # ✅ แปลงเป็น Organization objects
                org_objects = Organization.objects(id__in=orgList)
                greenYellowCards = greenYellowCards.filter(issuer__roles__orgId__in = org_objects)

                # greenYellowCards = greenYellowCards.filter(issuer__roles__orgId=org_id)
            if yellowCardTypes and yellowCardTypes != "None":
                yellowCardTypes = int(yellowCardTypes)
                greenYellowCards = greenYellowCards.filter(yellowCardType=yellowCardTypes)
            greenYellowCards = greenYellowCards.order_by('-issueDate')
            # ✅ สร้าง response list
            return JsonResponse({'success': True, 'data': [card.serialize() for card in greenYellowCards], 'message': 'Success'})
        return JsonResponse({'success': True, 'data': [], 'message': 'Success'})
        
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})

@requiredLogin
def getUserJson(request: HttpRequest):
    try:
        if not request.method == "GET":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        listData: List[User] = User.objects.filter(isActive = True, status = UserStatus.Hire.value).order_by('code')
        if not listData:
            return JsonResponse({'success': True, 'data': [], 'message': 'Success'})
        users = [ user.serialize() for user in listData]
        return JsonResponse({'success': True, 'data': users, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})
    
@requiredLogin
def getOrgJson(request: HttpRequest):
    try:
        if not request.method == "GET":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        
        listData = []
        level: Level = Level.objects.filter(isActive = True, nameEN = "Department").first()
        if level:
            listData: List[Organization] = Organization.objects.filter(isActive = True, level = level).order_by('level')
        else:
            listData: List[Organization] = Organization.objects.filter(isActive = True).order_by('level')
        if not listData:
            return JsonResponse({'success': True, 'data': [], 'message': 'Success'})
        orgs = [ org.serialize_organization() for org in listData]
        orgs.append({
            # -- สำหรับ option เลือกพวกต่างชาติ
            "id": "Foreigner",
            "nameEN": "Foreigner",
            "levelNameEN": "Foreigner"
        })
        
        return JsonResponse({'success': True, 'data': orgs, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})
    
@requiredLogin
def addGreenCardJson(request: HttpRequest):
    try:
        if not request.method == "POST":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        issueDate = request.POST.get('issueDate')
        detail = request.POST.get('detail')
        issueToType = request.POST.get('issueToType')
        employee = request.POST.get('user')
        org = request.POST.get('org')
        vendor = request.POST.get('vendor')
        img = request.FILES.get("image")
        dept = request.POST.get('dept')

        if issueDate:
            issueDate = DateStrToDate(issueDate)
        if issueToType:
            issueToType = int(issueToType)

        greenCard: GreenYellowCard = GreenYellowCard()
        greenCard.issueDate = issueDate
        greenCard.type = GreenYellowType.GreenCard.value
        greenCard.issueToType = IssueToType(issueToType)
        greenCard.detail = detail
        greenCard.isActive = True
        if IssueToType(issueToType).value == IssueToType.Employee.value:
            greenCard.issueTo = employee
            emp: User = User.objects(id = ObjectId(employee)).first()
            if not emp:
                return JsonResponse({'success': False, 'message': 'Employee not found'})
            emailIssueTo = []
            if not emp.email:
                # # -- ถ้า email ไม่มีให้หา email manager ของ dept นั้นๆ
                # empOrg = findDeptUser(emp)
                # if empOrg and len(empOrg) > 0:
                #     managerPos = Position.objects.filter(isActive = True, nameEN = "Manager").first()
                #     if managerPos:
                #         for o in empOrg:
                #             if o['id']:
                #                 us: User = User.objects.filter(
                #                     isActive = True,
                #                     roles__elemMatch = {
                #                         # -- $elemMatch จะเลือก เฉพาะ document ที่ roles มี element ใด element หนึ่งตรงกับเงื่อนไข
                #                         "isActive": True,
                #                         "orgId": ObjectId(o['id']),
                #                         "posId": ObjectId(managerPos.id)
                #                     },
                #                     email__nin= [None] # <-- filter email ที่ไม่ถูกต้อง
                #                 ).only("email")
                #                 for u in us:
                #                     emailIssueTo.append(u.email)
                #     greenCard.emailIssueTo = emailIssueTo
                #     print(f"------------------ emp mail: {emailIssueTo}")
                greenCard.emailIssueTo = emailIssueTo
                print(f"------------------ emp has mail: {emailIssueTo}")
            else:
                emailIssueTo.append(emp.email)
                greenCard.emailIssueTo = emailIssueTo
                print(f"------------------ emp has mail: {emailIssueTo}")
        elif IssueToType(issueToType).value == IssueToType.Organization.value:
            greenCard.issueTo = org
            emailIssueToOrg = []
            if org:
                if org != "Foreigner":
                    # managerPos = Position.objects.filter(isActive = True, nameEN = "Manager").first()
                    # if managerPos:
                    #     us: User = User.objects.filter(
                    #         isActive = True,
                    #         roles__elemMatch = {
                    #             "isActive": True,
                    #             "orgId": ObjectId(org),
                    #             "posId": ObjectId(managerPos.id)
                    #         },
                    #         email__nin= [None] # <-- filter email ที่ไม่ถูกต้อง
                    #     ).only("email")
                    #     for u in us:
                    #         emailIssueToOrg.append(u.email)
                    # greenCard.emailIssueTo = emailIssueToOrg
                    # print(f"------------------ org mail: {emailIssueToOrg}")
                    greenCard.emailIssueTo = emailIssueToOrg
                    print(f"------------------ org has mail: {emailIssueToOrg}")
                else:
                    print(f"------------------ foreigner")
        elif IssueToType(issueToType).value == IssueToType.Vendor.value:
            greenCard.issueTo = vendor
        currentUser: User = request.currentUser
        if not currentUser:
            return JsonResponse({'success': False, 'message': 'Issuer not found'})
        
        greenCard.issuer = Issuer()
        greenCard.issuer.userId = currentUser.id
        greenCard.issuer.code = currentUser.code
        greenCard.issuer.fNameEN = currentUser.fNameEN
        greenCard.issuer.lNameEN = currentUser.lNameEN
        greenCard.issuer.email = currentUser.email if currentUser.email else None
        
        if currentUser.nation == EmpNation.Thai:
            if not dept:
                return JsonResponse({'success': False, 'message': 'Department is required'})
            deptId = ObjectId(dept)
            findIssuserDept: Organization = Organization.objects.filter(id = deptId).first()
            if not findIssuserDept:
                return JsonResponse({'success': False, 'message': 'Department Issuser not found'})
            greenCard.deptId = str(deptId)
            greenCard.deptNameEN = findIssuserDept.nameEN
            
        uCreate = UserSnapshot().UserToSnapshot(currentUser)
        if uCreate:
            greenCard.createBy = uCreate
        greenCard.save()

        # -- upload image ทีหลัง กันเวลาบันทึกพลาดแล้ว upload file ไปเลย
        if img:
            if img.size > MAX_UPLOAD_SIZE:
                return JsonResponse({'success': False, 'message': 'Image size is too large exceeds 50 MB'})
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, uploadDir))
            safeName = sanitize_filename(img.name)
            filename = fs.save(safeName, img)  # จะเก็บไฟล์และ return filename
            file_path = os.path.join(uploadDir, filename)  # เช่น greenyellowcard/xxx.jpg
            if not file_path:
                return JsonResponse({'success': False, 'message': 'Upload failed'})
            greenCard.imagePath = file_path
        greenCard.save()

        hasSendMail = sendMailGreenYellowCard(greenCard)
        if hasSendMail == True:
            greenCard.hasSendMail = True
            greenCard.save()

        return JsonResponse({'success': True, 'message': 'Success'})
        
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})
    
@requiredLogin
def addYellowCardJson(request: HttpRequest):
    try:
        if not request.method == "POST":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        yellowIssueDate = request.POST.get('yellowIssueDate')
        providerToType = request.POST.get('providerToType')
        employee = request.POST.get('user')
        org = request.POST.get('org')
        vendor = request.POST.get('vendor')
        yellowType = request.POST.get('yellowType')
        detail = request.POST.get('detail')
        img = request.FILES.get("image")
        ydept = request.POST.get('ydept')

        if yellowIssueDate:
            yellowIssueDate = DateStrToDate(yellowIssueDate)
        if providerToType:
            providerToType = int(providerToType)
        if yellowType:
            yellowType = int(yellowType)
            
        printLogData(YellowCardType(yellowType))
        yellowCard: GreenYellowCard = GreenYellowCard()
        yellowCard.issueDate = yellowIssueDate
        yellowCard.type = GreenYellowType.YellowCard.value
        yellowCard.issueToType = IssueToType(providerToType)
        yellowCard.detail = detail
        yellowCard.isActive = True
        if IssueToType(providerToType).value == IssueToType.Employee.value:
            yellowCard.issueTo = employee
            emp: User = User.objects(id = ObjectId(employee)).first()
            if not emp:
                return JsonResponse({'success': False, 'message': 'Employee not found'})
            emailIssueTo = []
            if not emp.email:
                # # -- ถ้า email ไม่มีให้หา email manager ของ dept นั้นๆ
                # empOrg = findDeptUser(emp)
                # if empOrg and len(empOrg) > 0:
                #     managerPos = Position.objects.filter(isActive = True, nameEN = "Manager").first()
                #     if managerPos:
                #         for o in empOrg:
                #             if o['id']:
                #                 us: User = User.objects.filter(
                #                     isActive = True,
                #                     roles__elemMatch = {
                #                         # -- $elemMatch จะเลือก เฉพาะ document ที่ roles มี element ใด element หนึ่งตรงกับเงื่อนไข
                #                         "isActive": True,
                #                         "orgId": ObjectId(o['id']),
                #                         "posId": ObjectId(managerPos.id)
                #                     },
                #                     email__nin= [None] # <-- filter email ที่ไม่ถูกต้อง
                #                 ).only("email")
                #                 for u in us:
                #                     emailIssueTo.append(u.email)
                #     yellowCard.emailIssueTo = emailIssueTo
                #     print(f"------------------ emp mail: {emailIssueTo}")
                yellowCard.emailIssueTo = emailIssueTo
                print(f"------------------ emp has mail: {emailIssueTo}")
            else:
                emailIssueTo.append(emp.email)
                yellowCard.emailIssueTo = emailIssueTo
                print(f"------------------ emp has mail: {emailIssueTo}")

        elif IssueToType(providerToType).value == IssueToType.Organization.value:
            yellowCard.issueTo = org
            emailIssueToOrg = []
            if org:
                if org != "Foreigner":
                    # managerPos = Position.objects.filter(isActive = True, nameEN = "Manager").first()
                    # if managerPos:
                    #     us: User = User.objects.filter(
                    #         isActive = True,
                    #         roles__elemMatch = {
                    #             "isActive": True,
                    #             "orgId": ObjectId(org),
                    #             "posId": ObjectId(managerPos.id)
                    #         },
                    #         email__nin= [None] # <-- filter email ที่ไม่ถูกต้อง
                    #     ).only("email")
                    #     for u in us:
                    #         emailIssueToOrg.append(u.email)
                    # yellowCard.emailIssueTo = emailIssueToOrg
                    # print(f"------------------ org mail: {emailIssueToOrg}")
                    yellowCard.emailIssueTo = emailIssueToOrg
                    print(f"------------------ org has mail: {emailIssueToOrg}")
                else:
                    print(f"------------------ foreigner")
        elif IssueToType(providerToType).value == IssueToType.Vendor.value:
            yellowCard.issueTo = vendor
        yellowCard.yellowCardType = YellowCardType(yellowType)
        currentUser: User = request.currentUser
        if not currentUser:
            return JsonResponse({'success': False, 'message': 'Issuer not found'})
        yellowCard.issuer = Issuer()
        yellowCard.issuer.userId = currentUser.id
        yellowCard.issuer.code = currentUser.code
        yellowCard.issuer.fNameEN = currentUser.fNameEN
        yellowCard.issuer.lNameEN = currentUser.lNameEN
        yellowCard.issuer.email = currentUser.email if currentUser.email else None
        
        uUpdate = UserSnapshot().UserToSnapshot(currentUser)
        if uUpdate:
            yellowCard.updateBy = uUpdate
        yellowCard.updateDate = timezone.now()
        if currentUser.nation == EmpNation.Thai:
            if not ydept:
                return JsonResponse({'success': False, 'message': 'Department is required'})
            ydeptId = ObjectId(ydept)
            findIssuserDept: Organization = Organization.objects.filter(id = ydeptId).first()
            if not findIssuserDept:
                return JsonResponse({'success': False, 'message': 'Department Issuser not found'})
            yellowCard.deptId = str(ydeptId)
            yellowCard.deptNameEN = findIssuserDept.nameEN
        yellowCard.save()

        # -- upload image ทีหลัง กันเวลาบันทึกพลาดแล้ว upload file ไปเลย
        if img:
            if img.size > MAX_UPLOAD_SIZE:
                return JsonResponse({'success': False, 'message': 'Image size is too large exceeds 50 MB'})
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, uploadDir))
            safeName = sanitize_filename(img.name)
            filename = fs.save(safeName, img)  # จะเก็บไฟล์และ return filename
            file_path = os.path.join(uploadDir, filename)  # เช่น greenyellowcard/xxx.jpg
            if not file_path:
                return JsonResponse({'success': False, 'message': 'Upload failed'})
            yellowCard.imagePath = file_path
        yellowCard.save()

        hasSendmail = sendMailGreenYellowCard(yellowCard)
        if hasSendmail == True:
            yellowCard.hasSendMail = True
            yellowCard.save()
        
        return JsonResponse({'success': True, 'message': 'Success'})

    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})
    

@requiredLogin
def deleteGreenYellowCardJson(request: HttpRequest, id: str):
    try:
        if not request.method == "DELETE":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        gyData: GreenYellowCard = GreenYellowCard.objects.filter(id = ObjectId(id)).first()
        if not gyData:
            return JsonResponse({'success': False, 'message': 'Data not found'})
        gyData.isActive = False
        gyData.updateDate = timezone.now()
        cur: User = request.currentUser
        if cur:
            uUpdate = UserSnapshot().UserToSnapshot(cur)
            if uUpdate:
                gyData.updateBy = uUpdate
        gyData.save()
        return JsonResponse({'success': True, 'message': 'Success'})
    except Exception as e:
        print(str(e))
        return JsonResponse({'success': False, 'message': str(e)})
    
def sanitize_filename(filename: str) -> str:
    filename = filename.replace(" ", "_")
    filename = re.sub(r"[^A-Za-z0-9\.\-_]", "", filename)
    return filename

@requiredLogin
def conutGreenYellowCurMonth(request: HttpRequest):
    try:
        if not request.method == "GET":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        res = {}
        curUser = request.currentUser
        if not curUser:
            return JsonResponse({'success': False, 'message': 'User not found'})
        listData: List[GreenYellowCard] = GreenYellowCard.objects.filter(isActive = True, issuer__userId = curUser.id)
        if not listData:
            return JsonResponse({'success': True, 'data': res, 'message': 'Success'})
        res['month'] = timezone.now().month
        res['year'] = timezone.now().year
        for card in listData:
            if card.issueDate.month == timezone.now().month and card.issueDate.year == timezone.now().year:
                
                if card.type.value == GreenYellowType.GreenCard.value:
                    res['cGreen'] = res.get('cGreen', 0) + 1
                elif card.type.value == GreenYellowType.YellowCard.value:
                    res['cYellow'] = res.get('cYellow', 0) + 1
        return JsonResponse({'success': True, 'data': res, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})
    
@requiredLogin
def countALLOrgByMonAndYear(request: HttpRequest):
    try:
        if not request.method == "POST":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        body = json.loads(request.body.decode('utf-8'))  # อ่าน JSON body
        month = body.get('month')
        if not month:
            return JsonResponse({'success': False, 'message': 'Month is required'})
        
        res = {}
        year = timezone.now().year
        if month == "All":
            start_date = datetime.datetime(year, 1, 1, tzinfo=pytz.UTC)
            end_date = datetime.datetime(year + 1, 1, 1, tzinfo=pytz.UTC)
        else:
            # ✅ คำนวณช่วงเวลาเริ่มต้นและสิ้นสุดของเดือนนั้น
            start_date = datetime.datetime(year, int(month), 1, tzinfo=pytz.UTC)
            if int(month) == 12:
                end_date = datetime.datetime(year + 1, 1, 1, tzinfo=pytz.UTC)
            else:
                end_date = datetime.datetime(year, int(month) + 1, 1, tzinfo=pytz.UTC)
        listData: List[GreenYellowCard] = GreenYellowCard.objects.filter(
            isActive = True, 
            issueDate__gte=start_date,
            issueDate__lt=end_date
            )
        print(f"------------------ start_date: {start_date}, end_date: {end_date}")
        print(f"------------------ countALLOrgByMonAndYear: {listData.count()}")
        # if not listData:
        #     return JsonResponse({'success': True, 'data': res, 'message': 'Success'})
        # -- หา department level
        level: Level = Level.objects.filter(isActive = True, nameEN = "Department").first()
        if not level:
            return JsonResponse({'success': False, 'message': 'Level not found'})
        
        orgNameList = []
        countGreen = []
        countYellow = []
        orgs: List[Organization] = Organization.objects.filter(isActive = True)
        
        if not orgs:
            return JsonResponse({'success': False, 'message': 'Organization not found'})
        for org in orgs:
            strJson = org.serialize_organization()
            if strJson['levelNameEN'] == level.nameEN:
                orgNameList.append(strJson['nameEN'])
                findG = listData.filter(type = GreenYellowType.GreenCard.value, deptId = str(org.id)).count() if listData else 0
                findY = listData.filter(type = GreenYellowType.YellowCard.value, deptId = str(org.id)).count() if listData else 0
                countYellow.append(findY)
                countGreen.append(findG)
                # print(f"{strJson['nameEN']} => {findG}")
        findForeignerG = listData.filter(type = GreenYellowType.GreenCard.value, deptId = None).count() if listData else 0
        findForeignerY = listData.filter(type = GreenYellowType.YellowCard.value, deptId = None).count() if listData else 0
        countGreen.append(findForeignerG)
        countYellow.append(findForeignerY)
        orgNameList.append("Foreigner")
        res['orgs'] = orgNameList
        res['countGreen'] = countGreen
        res['countYellow'] = countYellow

        # printLogData(orgListStr)
        
        return JsonResponse({'success': True, 'data': res, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})

# -- เมื่อ user เปลี่ยน ตำแหน่ง ต้องเอาใบเขียวเหลืองของปีนั้นเป็น org ใหม่ด้วย
@requiredLogin
def userChangeDept(request: HttpRequest):
    try:
        # employee = request.POST.get('user')
        orgid = request.POST.get('orgid')
        userid = request.POST.get('userid')
        if not request.method == "POST":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        if not orgid:
            return JsonResponse({'success': False, 'message': 'Org id is required'})
        if not userid:
            return JsonResponse({'success': False, 'message': 'User id is required'})
        org: Organization = Organization.objects.filter(id = ObjectId(orgid)).first()
        if not org:
            return JsonResponse({'success': False, 'message': 'Org not found'})
        user: User = User.objects.filter(id = ObjectId(userid)).first()
        if not user:
            return JsonResponse({'success': False, 'message': 'User not found'})
        gyList: List[GreenYellowCard] = GreenYellowCard.objects.filter(isActive = True, issuer__userId = user.id)
        if not gyList:
            return JsonResponse({'success': True, 'message': 'Success'})
        for gy in gyList:
            gy.deptId = str(org.id)
            gy.deptNameEN = org.nameEN
            gy.updateDate = timezone.now()
            gy.save()

        return JsonResponse({'success': True, 'message': 'Success'})
    except Exception as e:
        print(e)
        return JsonResponse({'success': False, 'message': str(e)})