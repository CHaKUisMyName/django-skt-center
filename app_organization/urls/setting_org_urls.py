from django.urls import path
from app_organization.views import setting_org_views as setting_org_views


urlpatterns = [
    path('setting/', view = setting_org_views.indexSettingOrg, name = 'indexSettingOrg'),
    path('setting/add/', view = setting_org_views.addSettingOrg, name = 'addSettingOrg'),
    path('setting/edit/<str:id>/', view=setting_org_views.editSettingOrg, name='editSettingOrg'),
    path('setting/delete/<str:id>/', view=setting_org_views.deleteSettingOrg, name='deleteSettingOrg'),
]