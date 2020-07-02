from django.urls import path

from ..views import graphs, index


urlpatterns = [
    path('', index),
    path('graphs/', graphs)
]
