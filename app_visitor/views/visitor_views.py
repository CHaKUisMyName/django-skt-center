from datetime import datetime
from bson import ObjectId
import pytz
from typing import List
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.dateparse import parse_datetime
from django.conf import settings

from app_user.models.user import User
from app_user.utils import requiredLogin
from app_visitor.models.option import Option
from app_visitor.models.room import Room
from app_visitor.models.visitor import Visitor
from app_visitor.models.visitor_setting import VisitorSetting
from base_models.basemodel import UserSnapshot

mail_it = settings.MAIL_IT
mail_ga = settings.MAIL_GA

tz = pytz.timezone("Asia/Bangkok")

# Create your views here.
def index(request: HttpRequest):
    checkCurUserSettingAdmin = VisitorSetting.objects.filter(user = request.currentUser.id, isAdmin = True, isActive = True).first()
    isSettingAdmin = False
    if checkCurUserSettingAdmin:
        isSettingAdmin = True
    context = {
        "isSettingAdmin": isSettingAdmin,
    }
    return render(request,'visitor/index.html', context)

def listVisitorsJson(request: HttpRequest):
    try:
        if not request.method == "GET":
            return JsonResponse({'success': False, 'message': 'Method not allowed'})
        sdate = request.GET.get('sdate')
        edate = request.GET.get('edate')
        if not sdate or not edate:
            return JsonResponse({'success': False, 'message': 'Date is required'})
        listData: List[Visitor] = Visitor.objects.filter(
            sDate__gte=sdate,
            eDate__lte=edate,
            isActive=True
        ).order_by('sDate')
        if not listData:
            return JsonResponse({'success': True, 'data': [], 'message': 'Success'})
        visitors = [ vst.serialize() for vst in listData]
        return JsonResponse({'success': True, 'data': visitors, 'message': 'Success'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@requiredLogin
def add(request: HttpRequest):
    if request.method == 'POST':
        response = HttpResponseRedirect(reverse('indexVisitor'))
        try:
            topic = request.POST.get('topic')
            if not topic:
                messages.error(request, "Topic is required")
                return response
            sDate = request.POST.get("sdate")
            if sDate:
                sDate = datetime.strptime(sDate, "%d/%m/%Y %H:%M")
                sDate = tz.localize(sDate)
                sDate = sDate.astimezone(pytz.utc)
                print(f"Sdate : {sDate} {sDate.tzinfo}")
            else:
                messages.error(request, "Start Job Date is required")
                return response
            
            eDate = request.POST.get("edate")
            if eDate:
                eDate = datetime.strptime(eDate, "%d/%m/%Y %H:%M")
                eDate = tz.localize(eDate)
                eDate = eDate.astimezone(pytz.utc)
                print(f"Edate : {eDate} {eDate.tzinfo}")
            else:
                messages.error(request, "End Job Date is required")
                return response
            if sDate >= eDate:
                messages.error(request, 'Start date must be before end date.')
                return response
            guestCompany = request.POST.get('guestCompany')
            guestName = request.POST.get('guestName')
            member = request.POST.get('member')
            room = request.POST.get('room')
            if not room:
                messages.error(request, "Room is required")
                return response
            note = request.POST.get('note')
            duplicateMeeting = Visitor.objects.filter(
                room=room,
                sDate__lt=eDate,
                eDate__gt=sDate,
                isActive = True
            ).first()
            if duplicateMeeting:
                messages.error(request, "Duplicate meeting")
                return response
            arrOptions = []
            options = request.POST.getlist('options[]')
            if options:
                for option in options:
                    arrOptions.append(ObjectId(option))
            visitor: Visitor = Visitor()
            visitor.topic = topic
            visitor.sDate = sDate
            visitor.eDate = eDate
            visitor.guestCompany = guestCompany
            visitor.guestMember = guestName
            visitor.sktMember = member
            visitor.note = note
            visitor.room = ObjectId(room)
            visitor.isActive = True
            if len(arrOptions) > 0:
                visitor.options = arrOptions
            currentUser: User = request.currentUser
            if currentUser:
                uCreate = UserSnapshot().UserToSnapshot(currentUser)
                if uCreate:
                    visitor.createBy = uCreate
            visitor.save()
            sendMailBooking(visitor)
            messages.success(request, 'Save Success')
            return response
        except Exception as e:
            print(e)
            messages.error(request, str(e))
        return response
        
    else:
        rooms: List[Room] = Room.objects.filter(isActive = True)
        qDate = request.GET.get('d')
        if not qDate:
            qDate = ""

        options: List[Option] = Option.objects.filter(isActive = True)
        context = {
            "rooms": rooms,
            "qDate": qDate,
            "options": options,
        }
        return render(request,'visitor/add.html', context)
    
@requiredLogin
def edit(request: HttpRequest, id: str):
    if request.method == 'POST':
        response = HttpResponseRedirect(reverse('indexVisitor'))
        try:
            vstid = request.POST.get('vstid')
            if not vstid:
                messages.error(request, "Not found id")
                return response
            visitor: Visitor = Visitor.objects.filter(id = vstid).first()
            if not visitor:
                messages.error(request, "Visitor not found")
                return response
            topic = request.POST.get('topic')
            if not topic:
                messages.error(request, "Topic is required")
                return response
            sDate = request.POST.get("sdate")
            if sDate:
                sDate = datetime.strptime(sDate, "%d/%m/%Y %H:%M")
                sDate = tz.localize(sDate)
                sDate = sDate.astimezone(pytz.utc)
                print(f"Sdate : {sDate} {sDate.tzinfo}")
            else:
                messages.error(request, "Start Job Date is required")
                return response
            
            eDate = request.POST.get("edate")
            if eDate:
                eDate = datetime.strptime(eDate, "%d/%m/%Y %H:%M")
                eDate = tz.localize(eDate)
                eDate = eDate.astimezone(pytz.utc)
                print(f"Edate : {eDate} {eDate.tzinfo}")
            else:
                messages.error(request, "End Job Date is required")
                return response
            if sDate >= eDate:
                messages.error(request, 'Start date must be before end date.')
                return response
            room = request.POST.get('room')
            if not room:
                messages.error(request, "Room is required")
                return response
            duplicateMeeting = Visitor.objects.filter(
                room=room,
                sDate__lt=eDate,
                eDate__gt=sDate,
                isActive = True
            )
            isDup = duplicateMeeting.filter(pk__ne=vstid).first()
            if isDup:
                messages.error(request, "Duplicate meeting")
                return response
            note = request.POST.get('note')
            guestCompany = request.POST.get('guestCompany')
            guestName = request.POST.get('guestName')
            member = request.POST.get('member')

            arrOptions = []
            options = request.POST.getlist('options[]')
            if options:
                for option in options:
                    arrOptions.append(ObjectId(option))

            # -- map to visitor
            visitor.topic = topic
            visitor.sDate = sDate
            visitor.eDate = eDate
            visitor.guestCompany = guestCompany
            visitor.guestMember = guestName
            visitor.sktMember = member
            visitor.note = note
            visitor.room = ObjectId(room)
            visitor.isActive = True
            visitor.options = arrOptions
            visitor.update = timezone.now()
            currentUser: User = request.currentUser
            if currentUser:
                uUpdate = UserSnapshot().UserToSnapshot(currentUser)
                if uUpdate:
                    visitor.updateBy = uUpdate
            visitor.save()
            messages.success(request, 'Save Success')
            return response
        except Exception as e:
            print(e)
            messages.error(request, str(e))
        return response
    else:
        if not id:
            messages.error(request, "Not found id")
            return HttpResponseRedirect(reverse('indexVisitor'))
        visitor: Visitor = Visitor.objects.filter(id = id).first()
        if not visitor:
            messages.error(request, "Visitor not found")
            return HttpResponseRedirect(reverse('indexVisitor'))
        rooms: List[Room] = Room.objects.filter(isActive = True)
        options: List[Option] = Option.objects.filter(isActive = True)
        context = {
            "rooms": rooms,
            "visitor": visitor,
            "options": options,
        }
        return render(request,'visitor/edit.html', context)
    
@requiredLogin
def delete(request: HttpRequest, id: str):
    try:
        if not request.method == "GET":
            return JsonResponse({'deleted': False, 'message': 'Method not allowed'})
        if not id:
            return JsonResponse({'deleted': False, 'message': 'Not found id'})
        visitor: Visitor = Visitor.objects.filter(id = id).first()
        if not visitor:
            return JsonResponse({'deleted': False, 'message': 'Visitor not found'})
        visitor.isActive = False
        visitor.update = timezone.now()
        currentUser: User = request.currentUser
        if currentUser:
            uDelete = UserSnapshot().UserToSnapshot(currentUser)
            if uDelete:
                visitor.updateBy = uDelete
        visitor.save()
        return JsonResponse({'deleted': True, 'message': 'Delete success'})
    except Exception as e:
        print(e)
        return JsonResponse({'deleted': False, 'message': str(e)})

def sendMailBooking(visitor: Visitor):
    subject = 'Booking Visitor Data'
    from_email = 'Visitor System <it.report@sanyo-kasei.co.th>'
    # to_email = [str(settings.MAIL_CHAKU)]
    to_email = [str(mail_ga)]
    cc = [str(mail_it)]
    vst = visitor.serialize()
    context = {
        "vst": vst,
        "sDate": parse_datetime(vst["sDate"]).astimezone(tz).strftime("%d/%m/%Y %H:%M"),
        "eDate": parse_datetime(vst["eDate"]).astimezone(tz).strftime("%d/%m/%Y %H:%M"),
    }
    html_content = render_to_string("email/booking.html", context)
    # เผื่อ fallback เป็น text
    text_content = "Visitor Booking This is an alternative message in plain text."
    # สร้าง object email
    email = EmailMultiAlternatives(subject, text_content, from_email, to_email, cc= cc)
    # email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    email.send()
        