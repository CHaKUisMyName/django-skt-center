from django.urls import path

from app_car_schedule.views import car_views

urlpatterns = [
    path("car/", view=car_views.index, name="indexCar"),
    path("car/add/", view=car_views.add, name="addCar"),
    path("car/edit/<str:id>/", view=car_views.edit, name="editCar"),
    path("car/delete/<str:id>/", view=car_views.delete, name="deleteCar"),

]