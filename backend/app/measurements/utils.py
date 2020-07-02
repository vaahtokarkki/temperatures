import hashlib
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import Measurement


NIGHT_START = 22
NIGHT_END = 4
COLORS = ["#f44336", "#E91E63", "#9C27B0", "#3F51B5", "#2196F3", "#009688", "#4CAF50",
          "#FFEB3B", "#795548"]


def get_minutes(delta):
    """
    Get minutes from a timedelta object.

    Args:
        delta (Timedelta): A timedelta object
    Returns:
        int: Minutes from timedelta
    """
    return (delta.seconds % 3600) // 60


def authorized(request):
    """
    Check if given request is authorized.

    Args:
        request: A Django request
    Returns:
        boolean: True if correct token is present, or authorazion is disabled.
    """
    if not settings.API_TOKEN:
        return True

    if 'Authorazion' not in request.headers:
        return False
    token = request.headers["Authorazion"]
    hash = hashlib.sha256(bytes(settings.API_TOKEN, 'utf-8')).hexdigest()
    return token == f'Basic {hash}'


def save_measurement(data):
    """
    Create measurement objects from given data.

    Args:
        data (List): List containing dicts with sensor and value attribute. Type is an
        optional, and will default to temperature.
    """
    sensor = data.get('sensor', None)
    value = data.get('value', None)
    type = data.get('type', None)

    if not sensor or not value:
        raise ValueError("Sensor or value missing")

    try:
        value = float(value)
        type = int(type)
    except ValueError:
        return ValueError("Invalid value. Value must be an integer or float.")

    measurement = Measurement(sensor=sensor, value=value, type=type)
    measurement.save()
    return True


def get_night_low_measurements():
    """
    Retrieve measurements for all sensors containing lowest value of last night. Night is
    treated as interval from 22.00 to 5.00. If method is run in this interval, last night
    is used, not the current night, which is not over.

    Returns:
        Queryset containing lowest values for all sensors with measurements on last night
    """
    now = timezone.now()
    yesterday = now - timedelta(days=1)
    tomorrow = now + timedelta(days=1)

    night_start_timestamp = now if now.hour > NIGHT_START else yesterday
    night_start_timestamp = night_start_timestamp \
        .replace(hour=NIGHT_START, minute=0, second=0, microsecond=0)
    night_end_timestamp = tomorrow if now.hour >= 23 else now
    night_end_timestamp = night_end_timestamp \
        .replace(hour=NIGHT_END, minute=0, second=0, microsecond=0)

    return Measurement.objects \
        .filter(timestamp__gt=night_start_timestamp, timestamp__lt=night_end_timestamp) \
        .order_by("sensor", "value").distinct("sensor")


def get_measurements_from_now(hours, sensor=None, measurement_type=None):
    """
    Retrieve measurements from current time until given amount of hours. If a sensor is
    given, include only measurements from given sensor. If a type is given, include only
    measurements of given type.

    Args:
        hours (int): Limit results to only hours old measurements
        sensor (String, List<String>): Filter measurements to only given sensor
        measurement_type: (int, List<int>): Filter measurements to only given type
    Returns:
        A queryset
    """
    limit_timestamp = timezone.now() - timedelta(hours=hours)
    queryset = Measurement.objects.filter(timestamp__gt=limit_timestamp)

    if isinstance(sensor, list):
        queryset = queryset.filter(sensor__in=sensor)
    elif sensor:
        queryset = queryset.filter(sensor=sensor)

    if isinstance(measurement_type, list):
        queryset = queryset.filter(type__in=measurement_type)
    elif measurement_type:
        queryset = queryset.filter(type=measurement_type)

    return queryset.order_by("timestamp")
