from django.urls import path

from app_organization.views import organization_views as org_views

urlpatterns =[
    path('', view= org_views.index, name= 'indexOrg'),
    path('add/', view= org_views.addOrg, name= 'addOrg'),
    path('edit/<str:id>/', view= org_views.editOrg, name= 'editOrg'),
    path('delete/<str:id>/', view= org_views.deleteOrg, name= 'deleteOrg'),
    path('api/list/', view= org_views.listOrg, name= 'listOrg'),

]