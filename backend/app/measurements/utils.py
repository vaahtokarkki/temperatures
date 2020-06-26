from datetime import timedelta

from django.utils import timezone

from .models import Measurement


NIGHT_START = 22
NIGHT_END = 4


def get_minutes(delta):
    return (delta.seconds % 3600) // 60


def save_measurement(data):
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
    return False


def get_night_low_measurements():
    now = timezone.now()
    yesterday = now - timedelta(days=1)
    tomorrow = now + timedelta(days=1)

    night_start_timestamp = now if now.hour < NIGHT_START else yesterday
    night_start_timestamp = night_start_timestamp \
        .replace(hour=NIGHT_START, minute=0, second=0, microsecond=0)
    night_end_timestamp = tomorrow if now.hour <= 23 else now
    night_end_timestamp = night_end_timestamp \
        .replace(hour=NIGHT_END, minute=0, second=0, microsecond=0)

    return Measurement.objects \
        .filter(timestamp__gt=night_start_timestamp, timestamp__lt=night_end_timestamp) \
        .order_by("sensor", "value").distinct("sensor")
