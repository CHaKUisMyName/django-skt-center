from django.urls import path

from app_user import views


urlpatterns = [
    path('', view=views.index, name='indexUser'),
    path('add/', view=views.addUser, name='addUser'),
    path('edit/<str:id>/', view=views.editUser, name='editUser'),
    path('delete/<str:id>/', view=views.deleteUser, name='deleteUser'),
    path('regisuser/<str:id>/', view=views.regisUser, name='regisUser'),
    path('setting/', view=views.indexSettingUser, name= 'indexSettingUser'),
    path('alien/', view= views.AddAlienUser, name= 'AddAlienUser'),
]
