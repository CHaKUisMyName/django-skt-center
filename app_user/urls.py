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
    path('api/list/', view=user_views.listUser, name='listUser'),
    path('alien/', view= user_views.AddAlienUser, name= 'AddAlienUser'),
    # -----------------------------------------------------
    # ------------------- setting user --------------------
    # -----------------------------------------------------
    path('setting/', view=setting__user_views.indexSettingUser, name= 'indexSettingUser'),
    path('setting/add/', view=setting__user_views.addSettingUser, name= 'addSettingUser'),
    path('setting/edit/<str:id>/', view=setting__user_views.editSettingUser, name= 'editSettingUser'),
    path('setting/delete/<str:id>/', view=setting__user_views.deleteSettingUser, name= 'deleteSettingUser'),
    path('setting/import/', view=setting__user_views.importSettingUser, name= 'importSettingUser'),
    path('setting/template/', view=setting__user_views.exportExcelTemplate, name= 'exportExcelTemplate'),
]
