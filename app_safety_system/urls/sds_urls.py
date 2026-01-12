from django.urls import path

from app_safety_system.views import sds_views


urlpatterns = [
    path('sds/', view= sds_views.index, name= 'indexSDS'),
    path('sds/api/filter/', view= sds_views.filterSDSJson, name= 'filterSDSJson'),
    path('sds/api/get/<str:id>/', view= sds_views.getSDSByIdJson, name= 'getSDSByIdJson'),
    path('sds/addsdsjson/', view= sds_views.addSDSJson, name= 'addSDSJson'),
    path('sds/editsdsjson/', view= sds_views.editSDSJson, name= 'editSDSJson'),
    path('sds/deletesdsjson/<str:id>/', view= sds_views.deleteSDSJson, name= 'deleteSDSJson'),
]