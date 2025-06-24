from django.urls import path

from app_user import views


urlpatterns = [
    path('', view=views.index, name='indexUser'),
    path('add/', view=views.addUser, name='addUser'),
    path('setting/', view=views.indexSettingUser, name= 'indexSettingUser'),
    path('alien/', view= views.AddAlienUser, name= 'AddAlienUser'),
]
