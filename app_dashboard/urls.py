from django.urls import path

from app_dashboard import views


urlpatterns = [
    path('', view=views.index, name='indexDashboard'),
]