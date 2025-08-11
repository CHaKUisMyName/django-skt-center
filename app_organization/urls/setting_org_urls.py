from django.urls import path
from app_organization.views import setting_org_views as setting_org_views


urlpatterns = [
    path('setting/', view = setting_org_views.indexSettingOrg, name = 'indexSettingOrg')
]