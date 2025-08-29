from django.urls import path

from app_visitor.views import option_views


urlpatterns = [
    path('op/', view=option_views.index, name='indexOption'),
    path('op/add', view=option_views.add, name='addOption'),
    path('op/edit/<str:id>', view=option_views.edit, name='editOption'),
    path('op/delete/<str:id>', view=option_views.delete, name='deleteOption'),
]