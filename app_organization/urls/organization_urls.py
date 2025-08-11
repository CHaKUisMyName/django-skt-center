from django.urls import path

from app_organization.views import organization_views as org_views

urlpatterns =[
    path('og/', view= org_views.index, name= 'indexOrg'),
    path('og/add/', view= org_views.addOrg, name= 'addOrg'),
    path('og/edit/<str:id>/', view= org_views.editOrg, name= 'editOrg'),
    path('og/delete/<str:id>/', view= org_views.deleteOrg, name= 'deleteOrg'),
    path('og/api/list/', view= org_views.listOrg, name= 'listOrg'),

]