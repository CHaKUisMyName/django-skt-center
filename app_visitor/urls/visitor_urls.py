from django.urls import path

from app_visitor.views import visitor_views as visitor_views


urlpatterns = [
    path('', view=visitor_views.index, name='indexVisitor'),
    path('add', view=visitor_views.add, name='addVisitor'),
    path('edit/<str:id>', view=visitor_views.edit, name='editVisitor'),
    path('delete/<str:id>', view=visitor_views.delete, name='deleteVisitor'),
    path('api/listjs/', view=visitor_views.listVisitorsJson, name='listVisitorsJson'),
]