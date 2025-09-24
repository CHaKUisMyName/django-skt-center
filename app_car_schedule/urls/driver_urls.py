from django.urls import path

from app_car_schedule.views import driver_views

urlpatterns = [
    path('dv/', view= driver_views.index, name= 'indexDriver'),
    path('dv/add', view= driver_views.add, name= 'addDriver'),
    path('dv/edit/<str:id>', view= driver_views.edit, name= 'editDriver'),
    path('dv/delete/<str:id>', view= driver_views.delete, name= 'deleteDriver'),

]