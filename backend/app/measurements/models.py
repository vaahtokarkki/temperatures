from django.db import models


class Measurement(models.Model):
    TYPE_TEMPERATURE = 1
    TYPE_SOIL_MOISTURE = 2

    timestamp = models.DateTimeField(auto_now=True)
    value = models.FloatField()
    sensor = models.CharField(max_length=100)
    type = models.IntegerField(default=1)
