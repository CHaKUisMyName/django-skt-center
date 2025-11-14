from django.urls import path

from app_reminder.views import reminder_views


urlpatterns = [
    path('', view= reminder_views.index, name= 'indexReminder'),
    path('api/filter/', view= reminder_views.filter, name= 'filterReminder'),
    path('add/', view= reminder_views.AddJson, name= 'addReminder'),
    path('delete/<str:id>/', view= reminder_views.deleteJson, name= 'deleteReminder'),
]