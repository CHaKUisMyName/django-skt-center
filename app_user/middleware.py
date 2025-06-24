from django.http import HttpRequest

from app_user.models.user import User

class UserInjectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        # Code to execute before the view is called
        # For example, you could fetch user data and attach it to the request object
        # request.user_data = fetch_user_data(request)

        user = User.objects.first()
        if not user:
            user = None
        request.currentUser = user
        response = self.get_response(request)

        # Code to execute after the view is called

        return response
