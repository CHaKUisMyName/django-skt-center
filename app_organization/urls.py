from django.urls import path

from app_organization import views

urlpatterns =[
    path('', view= views.index, name= 'indexOrg'),
    path('add/', view= views.addOrg, name= 'addOrg'),
    path('edit/<str:id>/', view= views.editOrg, name= 'editOrg'),
    path('delete/<str:id>/', view= views.deleteOrg, name= 'deleteOrg'),
]