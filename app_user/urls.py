from django.urls import path

from app_user.views import user_views as user_views
from app_user.views import setting_user_views as setting__user_views



urlpatterns = [
    path('', view=user_views.index, name='indexUser'),
    path('add/', view=user_views.addUser, name='addUser'),
    path('edit/<str:id>/', view=user_views.editUser, name='editUser'),
    path('delete/<str:id>/', view=user_views.deleteUser, name='deleteUser'),
    path('regisuser/<str:id>/', view=user_views.regisUser, name='regisUser'),
    path('repass/<str:id>/', view=user_views.resetPassword, name='rePassUser'),
    path('setting/', view=setting__user_views.indexSettingUser, name= 'indexSettingUser'),
    path('alien/', view= user_views.AddAlienUser, name= 'AddAlienUser'),
]
