from datetime import timedelta
from bson import ObjectId
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.timezone import now
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.dateparse import parse_datetime
import pytz

from app_user.models.auth_session import AuthSession
from app_user.models.immigration import Immigration
from app_user.models.user import User
from app_user.models.user_setting import UserSetting

mail_it = settings.MAIL_IT
mail_ga = settings.MAIL_GA

tz = pytz.timezone("Asia/Bangkok")

def requiredLogin(view_func):
    def wrapper(request: HttpRequest, *args, **kwargs):
        clientSession = request.COOKIES.get("session")
        clientIP = request.META.get('REMOTE_ADDR', '')
        clientUA = request.META.get('HTTP_USER_AGENT', '')

        # ไม่มี cookie หรือ session key
        if not clientSession:
            response = HttpResponseRedirect('/login')
            response.delete_cookie('session')
            return response

        # หา session
        session: AuthSession = AuthSession.objects.filter(session = clientSession).first()
        if not session:
            response = HttpResponseRedirect('/login')
            response.delete_cookie('session')
            return response
        
        # 🔐 ดึงข้อมูลใน token (ซึ่งคุณเก็บ user data ไว้)
        data = session.GetSessionData()
        if not data:
            session.DeleteSessionData()
            response = HttpResponseRedirect('/login')
            response.delete_cookie('session')
            return response
        
        # 🧍 ตรวจสอบ IP / User-Agent ตรงกับตอนสร้าง session ไหม
        savedIP = data.get("ip", "")
        savedUA = data.get("ua", "")
        if savedIP != clientIP or savedUA != clientUA:
            # ป้องกัน cookie ถูกขโมยแล้วนำไปใช้จากเครื่องอื่น
            session.DeleteSessionData()
            response = HttpResponseRedirect('/login')
            response.delete_cookie('session')
            return response
        
        # ⏰ ตรวจสอบว่าหมดอายุหรือยัง
        if session.IsExpired():
            session.DeleteSessionData()
            response = HttpResponseRedirect('/login')
            response.delete_cookie('session')
            return response

        # 🔁 ต่ออายุ session ถ้ายัง active ภายในวันเดียวกัน
        if session.ContinueSession():
            session.expireDate = session.expireDate + timedelta(days=1)
            session.save()

        # ✅ เข้าถึง view ปกติ
        response = view_func(request, *args, **kwargs)

        # 🍪 ตั้งค่า cookie แบบปลอดภัย
        response.set_cookie(
            'session',
            session.session,
            expires=session.expireDate,
            # secure=True,      # ✅ ส่งเฉพาะผ่าน HTTPS
            # httponly=True,    # ✅ JS อ่านไม่ได้
            # samesite='Lax'    # ✅ ป้องกัน CSRF จาก site อื่น
        )
        return response
        
    return wrapper

def requiredSuperAdmin(view_func):
    def wrapper(request: HttpRequest, *args, **kwargs):
        user: User = request.currentUser
        if user.isAdmin == False:
            messages.error(request, "Not Permission")
            return HttpResponseRedirect('/')
        return view_func(request, *args, **kwargs)
    return wrapper

def isSettingUserAdmin(id):
    try:
        result = False
        userSetting: UserSetting = UserSetting.objects.filter(user = ObjectId(id), isActive = True).first()
        if userSetting:
            if userSetting.isAdmin == True:
                result = True
        return result
    except Exception as e:
        print(e)
        return False
    
def HasUsPermission(id: str, menu: str = None, checkAdmin: bool = False):
    try:
        result = False
        userSetting: UserSetting = UserSetting.objects.filter(user = ObjectId(id)).first()
        if userSetting:
            if checkAdmin == True:
                if userSetting.isAdmin == True and userSetting.isActive == True:
                    result = True
            else:
                if userSetting.isActive == True:
                    if menu:
                        result = any(m.name == menu for m in userSetting.menus)
        return result
    except Exception as e:
        print(e)
        return False
    
def sendImmigration(immigration: Immigration):
    subject = 'Immigration Data'
    from_email = 'Immigration System <it.report@sanyo-kasei.co.th>'
    to_email = [str(settings.MAIL_CHAKU)]
    # to_email = [str(mail_ga)]
    # cc = [str(mail_it)]
    imm = immigration.serialize()
    context = {
        "imm": imm,
        "dueDate": parse_datetime(imm["dueDate"]).astimezone(tz).strftime("%d/%m/%Y"),
    }
    html_content = render_to_string('email/immigration.html', context)
    # เผื่อ fallback เป็น text
    text_content = "Immigration This is an alternative message in plain text."
    # สร้าง object email
    # email = EmailMultiAlternatives(subject, text_content, from_email, to_email, cc= cc)
    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    email.attach_alternative(html_content, "text/html")
    email.send()

def jobDeleteSessionExpired():
    # ลบข้อมูล session ที่เกินเวลาทั้งหมดแแกจาก DB
        expireSeession = AuthSession.objects.filter(expireDate__lt = now())
        if expireSeession:
            expireSeession.delete()