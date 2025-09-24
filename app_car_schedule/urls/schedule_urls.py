from django.urls import path
from app_car_schedule.views import schedule_views

urlpatterns = [
    path('', view= schedule_views.index, name="indexCarSchedule"),
    path('add/', view= schedule_views.add, name="addCarSchedule"),
    path('edit/<str:id>/', view= schedule_views.edit, name="editCarSchedule"),
    path('delete/<str:id>/', view= schedule_views.delete, name="deleteCarSchedule"),
    path('api/listjs/', view= schedule_views.listCarScheduleJson, name="listCarScheduleJson"),
]