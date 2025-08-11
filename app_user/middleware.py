from django.http import HttpRequest

from app_user.models.auth_session import AuthSession
from app_user.models.user import User

class UserInjectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        # Code to execute before the view is called
        request.currentUser = None
        session_id = request.COOKIES.get("session")

        if session_id:
            auth_session = AuthSession.objects.filter(session=session_id).first()

            if auth_session and not auth_session.IsExpired():
                session_data = auth_session.GetSessionData()
                user_id = session_data.get("userId")
                if user_id:
                    request.currentUser = User.objects.filter(id=user_id, isActive=True).first()

        response = self.get_response(request)
        return response
