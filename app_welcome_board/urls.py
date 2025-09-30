from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from app_welcome_board import views

urlpatterns = [
    path("gs/", view=views.index, name="indexWelcomeBoard"),
    path("gs/add", view=views.addGuest, name="addGuestWelcomeBoard"),
    path("gs/edit/<str:id>", view=views.editGuest, name="editGuestWelcomeBoard"),
    path("gs/delete/<str:id>", view=views.deleteGuest, name="deleteGuestWelcomeBoard"),
    path("show/", view=views.showWelcomeBoard, name="showWelcomeBoard"),
    path("df/add", view=views.addDefault, name="addDefaultWelcomeBoard"),
    path("setting/", view=views.indexSetting, name="indexSettingWelcomeBoard"),
    path("setting/add", view=views.addSetting, name="addSettingWelcomeBoard"),
    path("setting/edit/<str:id>", view=views.editSetting, name="editSettingWelcomeBoard"),
    path("setting/delete/<str:id>", view=views.deleteSetting, name="deleteSettingWelcomeBoard"),

]