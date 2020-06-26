import json
from datetime import timedelta

from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Measurement
from .utils import get_minutes, get_night_low_measurements, save_measurement


@csrf_exempt
def create_measurement(request):
    data = json.loads(request.body)

    for entry in data:
        try:
            save_measurement(entry)
        except ValueError as error:
            return HttpResponse(error, status=400)

    return HttpResponse(status=201)


def index(request):
    now = timezone.now()

    measurements_of_night = get_night_low_measurements()
    latest_measurements = Measurement.objects \
        .filter(timestamp__gt=now - timedelta(days=1)) \
        .order_by('sensor', '-timestamp').distinct('sensor')

    print(measurements_of_night, latest_measurements)

    context = {
        "latest_measurements": [{
            "sensor": measurement.sensor,
            "value": measurement.value,
            "type": "temperature",
            "timestamp": measurement.timestamp.strftime("%H:%M %d.%m."),
            "mins_ago": get_minutes(now - measurement.timestamp)
        } for measurement in latest_measurements],
        "night_low": [{
            "sensor": measurement.sensor,
            "value": measurement.value,
            "timestamp": measurement.timestamp.strftime("%H:%M %d.%m."),
        } for measurement in measurements_of_night]
    }

    return render(request, 'measurements/index.html', context)
