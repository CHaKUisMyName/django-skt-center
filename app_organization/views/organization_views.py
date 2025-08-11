from typing import List
from bson import ObjectId
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone

from app_organization.models.level import Level
from app_organization.models.organization import Organization, OrganizationSnapShot
from app_user.models.user import User
from app_user.utils import requiredLogin
from base_models.basemodel import UserSnapshot

@requiredLogin
def index(request: HttpRequest):
    orgs = Organization.objects.filter(isDelete = False)
    context = {
        "orgs": orgs
    }
    return render(request, 'organization/index.html', context= context)

@requiredLogin
def addOrg(request: HttpRequest):
    if request.method == "POST":
        response = HttpResponseRedirect(reverse('indexOrg'))
        try:
            code = request.POST.get("code")
            if not code:
                messages.error(request, "Code is required")
                return response
            nameth = request.POST.get("nameth")
            nameen = request.POST.get("nameen")
            if not nameen:
                messages.error(request, "NameEN is required")
                return response
            shortname = request.POST.get("shortname")
            level = None if request.POST.get("level") == "none" else ObjectId(request.POST.get("level"))
            parent = None if request.POST.get("parent") == "none" else ObjectId(request.POST.get("parent"))
            note = request.POST.get("note")
            isactive = True if request.POST.get("isactive") == 'on' else False

            org = Organization()
            org.code = code
            org.nameTH = nameth
            org.nameEN = nameen
            org.shortName = shortname
            org.isActive = isactive
            org.isDelete = False
            org.note = note
            org.level = ObjectId(level) if level else None
            org.parent = ObjectId(parent) if parent else None
            currentUser: User = request.currentUser
            if currentUser:
                uCreate = UserSnapshot().UserToSnapshot(currentUser)
                if uCreate:
                    org.createBy = uCreate
            org.save()
            
            messages.success(request, 'Save Success')
        except Exception as e:
            print(e)
            messages.error(request, str(e))
        return response
    else:
        levels: List[Level] = Level.objects.filter(isActive = True, isDelete = False)
        orgs: List[Organization] = Organization.objects.filter(isActive = True, isDelete = False)
        context = {
            "levels": levels,
            "orgs": orgs,
        }
        return render(request, 'organization/add.html', context= context)

@requiredLogin 
def editOrg(request: HttpRequest, id: str):
    response = HttpResponseRedirect(reverse('indexOrg'))
    try:
        if request.method == "POST":
            orgId = request.POST.get("orgId")
            if not orgId:
                messages.error(request, "Not found id !")
                return response
            org: Organization = Organization.objects(id = ObjectId(orgId)).first()
            if not org:
                messages.error(request, "Organization not found")
                return response
            code = request.POST.get("code")
            if not code:
                messages.error(request, "Code is required")
                return response
            nameth = request.POST.get("nameth")
            nameen = request.POST.get("nameen")
            if not nameen:
                messages.error(request, "NameEN is required")
                return response
            shortname = request.POST.get("shortname")
            level = None if request.POST.get("level") == "none" else ObjectId(request.POST.get("level"))
            parent = None if request.POST.get("parent") == "none" else ObjectId(request.POST.get("parent"))
            note = request.POST.get("note")
            isactive = True if request.POST.get("isactive") == 'on' else False

            snapShot = OrganizationSnapShot()
            snapShot.code = org.code
            snapShot.nameTH = org.nameTH
            snapShot.nameEN = org.nameEN
            snapShot.shortName = org.shortName

            if org.parent:
                snapShot.parentCode = org.parent.code
                snapShot.parentNameTH = org.parent.nameTH
                snapShot.parentNameEN = org.parent.nameEN
            if org.level:
                snapShot.levelCode = org.level.code
                snapShot.LevelNameTH = org.level.nameTH
                snapShot.levelNameEN = org.level.nameEN

            org.code = code
            org.nameTH = nameth
            org.nameEN = nameen
            org.shortName = shortname
            org.isActive = isactive
            org.note = note

            currentUser: User = request.currentUser
            if currentUser:
                uUpdate = UserSnapshot().UserToSnapshot(currentUser)
                if uUpdate:
                    org.updateBy = uUpdate
                    snapShot.createBy = uUpdate
                org.updateDate = timezone.now()
            
            if not org.snapSots:
                org.snapSots = list()
            org.snapSots.append(snapShot)

            if parent:
                findParent = Organization.objects.get(id = ObjectId(parent))
                if not findParent:
                    messages.error(request, "Parent not found")
                    return response
            org.parent = ObjectId(parent) if parent else None
            if level:
                findLevel = Level.objects.get(id = ObjectId(level))
                if not findLevel:
                    messages.error(request, "Level not found")
                    return response
            org.level = level
            org.save()

            messages.success(request, 'Save Success')
            return response

        else:
            org = Organization.objects.get(id = ObjectId(id))
            if not org:
                messages.error(request= request, message= "Organization not found !")
                return response
            levels: List[Level] = Level.objects.filter(isActive = True, isDelete = False)
            orgs: List[Organization] = Organization.objects.filter(isActive = True, isDelete = False, id__ne= org.id)
            context = {
                "org": org,
                "levels": levels,
                "orgs": orgs,
            }
            return render(request, 'organization/edit.html', context= context)
    except Exception as e:
        print(e)
        messages.error(request, str(e))
    return response

@requiredLogin
def deleteOrg(request: HttpRequest, id: str):
    try:
        if not request.method == "GET":
            return JsonResponse({'deleted': False, 'message': 'Method not allowed'})
        if not id:
            return JsonResponse({'deleted': False, 'message': 'Not found id'})
        org: Organization = Organization.objects.get(id = ObjectId(id))
        if not org:
            return JsonResponse({'deleted': False, 'message': 'Organization not found'})
        currentUser: User = request.currentUser
        if currentUser:
            uDelete = UserSnapshot().UserToSnapshot(currentUser)
            if uDelete:
                org.updateBy = uDelete
            org.updateDate = timezone.now()
        org.isActive = False
        org.isDelete = True
        org.save()
        returnData = {
            'deleted': True,
            'message': 'Delete success'
        }
        return JsonResponse(returnData)
    except Exception as e:
        returnData = {
            'deleted': False,
            'message': str(e)
        }
        return JsonResponse(returnData)

@requiredLogin
def listOrg(request: HttpRequest):
    try:
        if not request.method == "GET":
            return JsonResponse({'success': False, 'data': [], 'message': 'Method not allowed'})
        
        # รับจาก query string: /list/?isActive=true&isDelete=false
        isActive_str = request.GET.get("isactive")
        isDelete_str = request.GET.get("isdelete")
        # แปลง string เป็น boolean
        def parse_bool(val):
            return val.lower() in ["true", "1", "yes"] if val else None
        
        isActive = parse_bool(isActive_str)
        isDelete = parse_bool(isDelete_str)
        query = {}
        if isActive is not None:
            query['isActive'] = isActive
        if isDelete is not None:
            query['isDelete'] = isDelete
        orgs: List[Organization] = Organization.objects.filter(**query).order_by('code')
        
        returnData = {
            "success": True,
            # "data": json.loads(pos.to_json()),
            "data": [ o.serialize_organization() for o in orgs],
            "message": "Success"
        }
        return JsonResponse(returnData)
    except Exception as e:
        returnData = {
            "success": False,
            "data": [],
            "message": str(e)
        }
        return JsonResponse(returnData)