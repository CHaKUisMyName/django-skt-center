from django.urls import path

from app_safety_system.views import greencard_views


urlpatterns = [
    path('gy/', view= greencard_views.index, name= 'indexGreenCard'),
    path('gy/search/', view= greencard_views.search, name= 'searchGreenCard'),
    path('gy/api/filter/', view= greencard_views.filterGreenYellowCardJson, name= 'filterGreenYellowCardJson'),
    path('gy/api/userjson/', view= greencard_views.getUserJson, name= 'getUserJson'),
    path('gy/api/orgjson/', view= greencard_views.getOrgJson, name= 'getOrgJson'),
    path('gy/addgreencardjson/', view= greencard_views.addGreenCardJson, name= 'addGreenCardJson'),
    path('gy/addyellowcardjson/', view= greencard_views.addYellowCardJson, name= 'addYellowCardJson'),
    path('gy/delete/<str:id>/', view= greencard_views.deleteGreenYellowCardJson, name= 'delete'),
    path('gy/api/count/', view= greencard_views.conutGreenYellowCurMonth, name= 'conutGreenYellowCurMonth'),
    path('gy/api/countorg/', view= greencard_views.countALLOrgByMonAndYear, name= 'countALLOrgByMonAndYear'),
    path('gy/changedept/', view= greencard_views.userChangeDept, name= 'userChangeDept'),
]