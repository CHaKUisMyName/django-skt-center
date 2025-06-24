from django.urls import path

from app_visitor import views


urlpatterns = [
    path('', view=views.index, name='indexVisitor'),
    path('list/', view=views.listVisitor, name='listVisitor'),
    path('add/', view=views.addVisitor, name='addVisitor'),
    path('option/', view=views.listOption, name='listOption'),
    path('addOption/', view=views.addOption, name='addOption'),
    path('room/', view=views.listRoom, name='listRoom'),
    path('addRoom/', view=views.addRoom, name='addRoom'),
    
    
]