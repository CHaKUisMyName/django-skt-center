from django.http import HttpRequest

from app_user.models.auth_session import AuthSession
from app_user.models.user import User

class UserInjectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        # Code to execute before the view is called
        # For example, you could fetch user data and attach it to the request object
        # request.user_data = fetch_user_data(request)
        session = request.COOKIES.get("session")
        authSesstion: AuthSession  =  AuthSession.objects.filter(session = session).first()
        
        if authSesstion:
            if not authSesstion.IsExpired():
                data = authSesstion.GetSessionData()
                # print(data)
                user = User.objects.filter(id = data["userId"]).first()
                request.currentUser = user if user else None
            else:
                request.currentUser = None
        else:
            request.currentUser = None
        response = self.get_response(request)
        return response
