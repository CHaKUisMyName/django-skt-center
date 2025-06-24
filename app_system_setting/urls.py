from django.urls import path

from app_system_setting import views


urlpatterns = [
    path('', view= views.indexApp, name= 'indexApp'),
    path('add/', view= views.addApp, name= 'addApp'),
    path('edit/<id>', view= views.editApp, name= 'editApp'),
    path('delete/<id>', view= views.deleteApp, name= 'deleteApp'),
    path('menu/', view= views.indexMenu, name= 'indexMenu'),
    path('menu/add/', view= views.addMenu, name= 'addMenu'),
    path('menu/edit/<id>', view= views.editMenu, name= 'editMenu'),
    path('menu/delete/<id>', view= views.deleteMenu, name= 'deleteMenu'),

    
]