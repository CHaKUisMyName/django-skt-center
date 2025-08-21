from django.urls import path

from app_deploy import views


urlpatterns = [
    path('', view= views.indexDeploy, name= 'indexDeploy'),
]