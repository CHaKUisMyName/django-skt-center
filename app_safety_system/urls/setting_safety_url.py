from django.urls import path
from app_safety_system.views import setting_safety_views as setting_safety_views


urlpatterns = [
    path('setting/', view= setting_safety_views.indexSettingSafety, name='indexSettingSafety'),
    path('setting/add/', view= setting_safety_views.addSettingSafety, name='addSettingSafety'),
    path('setting/edit/<str:id>/', view= setting_safety_views.editSettingSafety, name='editSettingSafety'),
    path('setting/delete/<str:id>/', view= setting_safety_views.deleteSettingSafety, name='deleteSettingSafety'),
    path('setting/import/', view= setting_safety_views.importSettingSafety, name='importSettingSafety'),
    path('setting/template/', view= setting_safety_views.exportExcelTemplate, name='safetyExcelTemplate'),

]