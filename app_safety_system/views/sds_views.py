import datetime
import json
import os
import re
from bson import ObjectId
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.utils import timezone

from app_safety_system.models.sds import SdsDocument, SdsType, SdsVersion
from app_safety_system.utils import HasSftPermission
from app_user.models.user import User
from app_user.utils import requiredLogin
from base_models.basemodel import UserSnapshot
from skt_center import settings

MAX_UPLOAD_SIZE = getattr(
    settings,
    "FILE_UPLOAD_MAX_MEMORY_SIZE",
    50 * 1024 * 1024  # fallback
)
uploadDir = 'sds_documents/'


@requiredLogin
def index(request: HttpRequest):
    sdsTypes = [sds_type.serialize() for sds_type in SdsType]
    lang = [sds_lang.serialize() for sds_lang in SdsVersion]
    
    context = {
        "sdsTypes": sdsTypes,
        "lang": lang,
        'mediaRoot': settings.MEDIA_URL,
    }
    return render(request, 'sds/index.html', context)

@requiredLogin
def filterSDSJson(request: HttpRequest):
    try:
        if request.method != "POST":
            return JsonResponse({"success": False, "message": "Method not allowed."})
        
        canModify = True  # Placeholder for permission check
        hasPermission = HasSftPermission(id = str(request.currentUser.id), menu= "SDS", checkAdmin = False)
        if not request.currentUser.isAdmin:
            if hasPermission == False:
                canModify = False
        
        sdsDocuments = []
        body = json.loads(request.body.decode('utf-8'))
        searchInput = body.get("searchInput", "").strip()
        sdsTypes = body.get("sdsTypes", [])
        docVersion = body.get("docVersion", "")
        dataQuery = SdsDocument.objects()
        filterParams = {}
        if sdsTypes and isinstance(sdsTypes, list):
            filterParams['type__in'] = [SdsType(int(t)) for t in sdsTypes]
        if docVersion:
            filterParams['docVersion'] = SdsVersion(int(docVersion))
        if filterParams:
            dataQuery = dataQuery.filter(**filterParams)
        if searchInput:
            dataQuery = dataQuery.filter(
                __raw__={
                    '$or': [
                        {'name': {'$regex': re.escape(searchInput), '$options': 'i'}},
                        {'chemicalName': {'$regex': re.escape(searchInput), '$options': 'i'}},
                        {'casNo': {'$regex': re.escape(searchInput), '$options': 'i'}}
                    ]
                }
            )
        listData = dataQuery.order_by('-createDate')
        for doc in listData:
            sdsDocuments.append({
                "canModify": canModify,
                "data":doc.serialize()
            })
        return JsonResponse({"success": True, "data": sdsDocuments, 'message': 'Success'})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})
    
@requiredLogin
def getSDSByIdJson(request: HttpRequest, id: str):
    try:
        if not request.method == "GET":
            return JsonResponse({"success": False, "message": "Method not allowed."})
        if not id or not ObjectId.is_valid(id):
            return JsonResponse({"success": False, "message": "Invalid SDS ID."})
        sdsDocument: SdsDocument = SdsDocument.objects(id=ObjectId(id)).first()
        if not sdsDocument:
            return JsonResponse({"success": False, "message": "SDS not found."})
        return JsonResponse({"success": True, "data": sdsDocument.serialize(), "message": "Success"})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})
    
@requiredLogin
def addSDSJson(request: HttpRequest):
    file_path = None
    try:
        if not request.method == "POST":
            return JsonResponse({"success": False, "message": "Method not allowed."})
        hasPermission = HasSftPermission(id = str(request.currentUser.id), menu= "SDS", checkAdmin = False)
        if not request.currentUser.isAdmin:
            if hasPermission == False:
                return JsonResponse({'success': False, 'message': 'Not Permission'})
        name = request.POST.get("name") # -- skt name
        chemicalName = request.POST.get("chemicalName") # -- chemical name
        doc = request.FILES.get("doc")
        doctype = request.POST.get("doctype")
        casNo = request.POST.get("casno")
        docversion = request.POST.get("docversion")
        if not name or not chemicalName or not doc or not doctype or not docversion:
            return JsonResponse({"success": False, "message": "Missing required fields."})
        
        if doc.content_type != "application/pdf":
            return JsonResponse({"success": False, "message": "Document must be a PDF file."})
        if doc.size > MAX_UPLOAD_SIZE:
            return JsonResponse({"success": False, "message": "Document size exceeds the maximum limit of 50MB."})
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, uploadDir))
        safeName = sanitize_filename(doc.name)
        filename = fs.save(safeName, doc)
        file_path = os.path.join(uploadDir, filename)
        if not file_path:
            return JsonResponse({"success": False, "message": "Failed to upload document."})
        
        sdsDocument = SdsDocument()
        sdsDocument.name = name # -- skt name --
        sdsDocument.chemicalName = chemicalName # -- chemical name --
        sdsDocument.casNo = casNo
        sdsDocument.docPath = file_path
        sdsDocument.isActive = True
        sdsDocument.createDate = timezone.now()
        sdsDocument.type = SdsType(int(doctype))
        sdsDocument.docVersion = SdsVersion(int(docversion))
        currentUser: User = request.currentUser
        if currentUser:
            uCreate = UserSnapshot().UserToSnapshot(currentUser)
            if uCreate:
                sdsDocument.createBy = uCreate
        sdsDocument.save()
        
        return JsonResponse({"success": True, "message": "SDS added successfully."})
    except Exception as e:
        if file_path and os.path.join(settings.MEDIA_ROOT, file_path):
            os.remove(os.path.join(settings.MEDIA_ROOT, file_path))
        return JsonResponse({"success": False, "message": str(e)})
    
@requiredLogin
def editSDSJson(request: HttpRequest):
    if not request.method == "POST":
        return JsonResponse({"success": False, "message": "Method not allowed."})
    hasPermission = HasSftPermission(id = str(request.currentUser.id), menu= "SDS", checkAdmin = False)
    if not request.currentUser.isAdmin:
        if hasPermission == False:
            return JsonResponse({'success': False, 'message': 'Not Permission'})
    id = request.POST.get("id")
    name = request.POST.get("name") # -- skt name
    chemicalName = request.POST.get("chemicalName") # -- chemical name
    doc = request.FILES.get("doc")
    doctype = request.POST.get("doctype")
    docversion = request.POST.get("docversion")
    casNo = request.POST.get("casno")
    if not id or not ObjectId.is_valid(id):
        return JsonResponse({"success": False, "message": "Invalid SDS ID."})
    if not name or not chemicalName or not doctype or not docversion:
        return JsonResponse({"success": False, "message": "Missing required fields."})
    try:
        sdsDocument: SdsDocument = SdsDocument.objects(id=ObjectId(id)).first()
        if not sdsDocument:
            return JsonResponse({"success": False, "message": "SDS not found."})
        if doc:
            if doc.content_type != "application/pdf":
                return JsonResponse({"success": False, "message": "Document must be a PDF file."})
            if doc.size > MAX_UPLOAD_SIZE:
                return JsonResponse({"success": False, "message": "Document size exceeds the maximum limit of 50MB."})
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, uploadDir))
            safeName = sanitize_filename(doc.name)
            filename = fs.save(safeName, doc)
            new_path = os.path.join(uploadDir, filename)
            if not new_path:
                return JsonResponse({"success": False, "message": "Failed to upload document."})
            # Remove old file
            old_path = os.path.join(settings.MEDIA_ROOT, sdsDocument.docPath) if sdsDocument.docPath else None
            if old_path and os.path.exists(old_path):
                os.remove(old_path)

            sdsDocument.docPath = new_path
        sdsDocument.name = name # -- skt name --
        sdsDocument.chemicalName = chemicalName # -- chemical name --
        sdsDocument.casNo = casNo
        sdsDocument.type = SdsType(int(doctype))
        sdsDocument.docVersion = SdsVersion(int(docversion))
        sdsDocument.updateDate = timezone.now()
        currentUser: User = request.currentUser
        if currentUser:
            uUpdate = UserSnapshot().UserToSnapshot(currentUser)
            if uUpdate:
                sdsDocument.updateBy = uUpdate
        
        sdsDocument.save()
        return JsonResponse({"success": True, "message": "SDS edited successfully."})
    except Exception as e:
        if doc:
            fail_path = os.path.join(settings.MEDIA_ROOT, uploadDir, doc.name)
            if os.path.exists(fail_path):
                os.remove(fail_path)
        return JsonResponse({"success": False, "message": str(e)})
    
@requiredLogin
def deleteSDSJson(request: HttpRequest, id: str):
    try:
        if not request.method == "GET":
            return JsonResponse({"success": False, "message": "Method not allowed."})
        hasPermission = HasSftPermission(id = str(request.currentUser.id), menu= "SDS", checkAdmin = False)
        if not request.currentUser.isAdmin:
            if hasPermission == False:
                return JsonResponse({'success': False, 'message': 'Not Permission'})
        if not id or not ObjectId.is_valid(id):
            return JsonResponse({"success": False, "message": "Invalid SDS ID."})
        sdsDocument: SdsDocument = SdsDocument.objects(id=ObjectId(id)).first()
        if not sdsDocument:
            return JsonResponse({"success": False, "message": "SDS not found."})
        # Remove file
        file_path = os.path.join(settings.MEDIA_ROOT, sdsDocument.docPath) if sdsDocument.docPath else None
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        sdsDocument.delete()
        return JsonResponse({"success": True, "message": "Success."})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})

def sanitize_filename(filename: str) -> str:
    filename = filename.replace(" ", "_")
    filename = re.sub(r"[^A-Za-z0-9\.\-_]", "", filename)
    return filename