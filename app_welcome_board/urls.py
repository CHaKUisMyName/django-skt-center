from django.urls import path

from app_welcome_board import views

urlpatterns = [
    path("gs/", view=views.index, name="indexWelcomeBoard"),
    path("gs/add", view=views.addGuest, name="addGuestWelcomeBoard"),
]