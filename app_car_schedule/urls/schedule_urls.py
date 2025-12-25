from django.urls import path
from app_car_schedule.views import schedule_views

urlpatterns = [
    path('', view= schedule_views.index, name="indexCarSchedule"),
    path('add/', view= schedule_views.add, name="addCarSchedule"),
    path('edit/<str:id>/', view= schedule_views.edit, name="editCarSchedule"),
    path('delete/<str:id>/', view= schedule_views.delete, name="deleteCarSchedule"),
    path('list/', view= schedule_views.listPage, name="listCarSchedule"),
    path('api/listjs/', view= schedule_views.listCarScheduleJson, name="listCarScheduleJson"),
    path('api/filter/', view= schedule_views.filterCarScheduleJson, name="filterCarScheduleJson"),
    path('api/excelyear/<str:year>/', view= schedule_views.excelYear, name="excelYear"),
    path('api/export/', view= schedule_views.exportByDateRange, name="exportByDateRange"),

]