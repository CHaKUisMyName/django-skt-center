from django.urls import path
from app_visitor.views import setting_visitor_views


urlpatterns = [
    path('stvst/', view = setting_visitor_views.index, name= 'indexSettingVst'),
    path('stvst/add', view = setting_visitor_views.add, name= 'addSettingVst'),
    path('stvst/edit/<str:id>', view = setting_visitor_views.edit, name= 'editSettingVst'),
    path('stvst/delete/<str:id>', view = setting_visitor_views.delete, name= 'deleteSettingVst'),
    path('stvst/import', view = setting_visitor_views.importSettingVst, name= 'importSettingVst'),
    path('stvst/export', view = setting_visitor_views.exportExcelTemplate, name= 'exportExcelTemplateVst'),
]