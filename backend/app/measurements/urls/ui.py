from django.urls import path

from ..views import index, graphs


urlpatterns = [
    path('', index),
    path('graphs/', graphs)
]
