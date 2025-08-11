from django.urls import path

from app_organization.views import position_views as position_views

urlpatterns = [
    path('pos/', view= position_views.index, name='indexPosition'),
    path('pos/add/', view= position_views.addPosition, name='addPosition'),
    path('pos/edit/<str:id>/', view= position_views.editPosition, name='editPosition'),
    path('pos/delete/<str:id>/', view= position_views.deletePosition, name='deletePosition'),
    path('pos/api/list/', view= position_views.listPosition, name='listPosition'),
]