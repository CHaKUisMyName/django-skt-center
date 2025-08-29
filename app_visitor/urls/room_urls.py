from django.urls import path

from app_visitor.views import room_views

urlpatterns =[
    path('ro/', view= room_views.index, name= 'indexRoom'),
    path('ro/add', view= room_views.add, name= 'addRoom'),
    path('ro/edit/<str:id>', view= room_views.edit, name= 'editRoom'),
    path('ro/delete/<str:id>', view= room_views.delete, name= 'deleteRoom'),
]