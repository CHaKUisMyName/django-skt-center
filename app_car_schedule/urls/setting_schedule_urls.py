from django.urls import path
from app_car_schedule.views import setting_schedule_views



urlpatterns = [
    path('stcsh/', view = setting_schedule_views.index, name= 'indexSettingCsh'),
    path('stcsh/add', view = setting_schedule_views.add, name= 'addSettingCsh'),
    path('stcsh/edit/<str:id>', view = setting_schedule_views.edit, name= 'editSettingCsh'),
    path('stcsh/delete/<str:id>', view = setting_schedule_views.delete, name= 'deleteSettingCsh'),
]