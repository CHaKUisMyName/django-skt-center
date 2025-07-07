from datetime import timedelta
from django.http import HttpRequest, HttpResponseRedirect
from django.utils.timezone import now

from app_user.models.auth_session import AuthSession

def requiredLogin(view_func):
    def wrapper(request: HttpRequest, *args, **kwargs):
        clientSession = request.COOKIES.get("session")

        # ลบข้อมูล session ที่เกินเวลาทั้งหมดแแกจาก DB
        expireSeession = AuthSession.objects.filter(expireDate__lt = now())
        if expireSeession:
            expireSeession.delete()

        # หา session
        session: AuthSession = AuthSession.objects.filter(session = clientSession).first()
        if not session:
            return HttpResponseRedirect('/login')
        
        if session.IsExpired():
            session.DeleteSessionData()
            response = HttpResponseRedirect('/login')
            response.delete_cookie('session')
            return response
        else:
            if session.ContinueSession() == True:
                session.expireDate = session.expireDate + timedelta(days = 1)
                session.save()
                response = view_func(request, *args, **kwargs)
                response.set_cookie('session', session.session, expires = session.expireDate)
                return response
            return view_func(request, *args, **kwargs)
    return wrapper