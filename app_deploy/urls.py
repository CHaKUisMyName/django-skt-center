from django.urls import path

from app_deploy import views


urlpatterns = [
    path('', view= views.indexDeploy, name= 'indexDeploy'),
    path('chakudeploy/', view= views.deploy, name= 'deploy'),

]