from django.urls import path

from app_visitor.views import visitor_views as visitor_views


urlpatterns = [
    path('', view=visitor_views.index, name='indexVisitor'),
    path('add', view=visitor_views.add, name='addVisitor'),
    path('edit/<str:id>', view=visitor_views.edit, name='editVisitor'),
    path('delete/<str:id>', view=visitor_views.delete, name='deleteVisitor'),
    path('api/listjs/', view=visitor_views.listVisitorsJson, name='listVisitorsJson'),
    path('show', view= visitor_views.show, name= 'showVisitor'),
    path('list', view= visitor_views.listPage, name= 'listVisitor'),
    path('api/get/<str:id>', view= visitor_views.getVisitorJson, name= 'getVisitorJson'),
    path('api/filter/', view= visitor_views.fileterVisitorsJson, name= 'filterVisitorsJson'),

]