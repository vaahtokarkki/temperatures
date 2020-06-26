from django.db import models


class Measurement(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    value = models.FloatField()
    sensor = models.CharField(max_length=100)
    type = models.IntegerField(default=1)
