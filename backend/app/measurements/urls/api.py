from django.urls import path

from ..views import create_measurement


urlpatterns = [
    path('measurement/', create_measurement)
]
