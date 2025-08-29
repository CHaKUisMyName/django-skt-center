from django.urls import path

from app_visitor.views import visitor_views as visitor_views


urlpatterns = [
    path('', view=visitor_views.index, name='indexVisitor'),
]