import json
import random

from django.db.models import Avg, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.timezone import get_current_timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Measurement
from .utils import COLORS, authorized, get_measurements_from_now, get_minutes, \
    get_night_low_measurements, save_measurement


@csrf_exempt
def create_measurement(request):
    """
    Create a measurement record to database. Endpoint excepts to receive a list of
    measurements.

    If server configuration includes API_TOKEN environment variable, it must be included
    in authorazion header. See more about authentication from documentation.

    Required fields for measurement object are:
        value (float): Value to record, e.g. temperature
        sensor (string): A identifier for sensor where the value is from
    """
    if not authorized(request):
        return HttpResponse("Unauthorized", status=401)
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
    latest_measurements = get_measurements_from_now(1) \
        .order_by('sensor', '-timestamp').distinct('sensor')

    averages = get_measurements_from_now(1) \
        .values('sensor').annotate(avg=Avg('value'), sum=Sum('value'))

    stats_by_sensor = {}
    for measurement in averages:
        last_hours = get_measurements_from_now(1, sensor=measurement["sensor"])
        stats_by_sensor[measurement["sensor"]] = {
            "avg": measurement["avg"],
            "sum": (last_hours.latest("timestamp").value -
                    last_hours.earliest("timestamp").value)
        }

    context = {
        "latest_measurements": [{
            "sensor": measurement.sensor,
            "value": measurement.value,
            "type": "temperature",
            "timestamp": measurement.timestamp.astimezone(get_current_timezone())
                    .strftime("%H:%M %d.%m."),
            "mins_ago": get_minutes(now - measurement.timestamp),
            "hour_avg": round(stats_by_sensor[measurement.sensor]["avg"], 2),
            "hour_delta": round(stats_by_sensor[measurement.sensor]["sum"], 2)
        } for measurement in latest_measurements],
        "night_low": [{
            "sensor": measurement.sensor,
            "value": measurement.value,
            "timestamp": measurement.timestamp.astimezone(get_current_timezone())
            .strftime("%H:%M %d.%m."),
        } for measurement in measurements_of_night]
    }

    return render(request, 'measurements/index.html', context)


def graphs(request):
    try:
        limit_hours = int(request.GET.get("limit", 4))
    except ValueError:
        return render(request, 'measurements/charts.html')

    measurements_temperature = get_measurements_from_now(
        limit_hours, measurement_type=Measurement.TYPE_TEMPERATURE
    )

    measurements_by_sensor = {}
    all_labels = set()
    for measurement in measurements_temperature:
        items = measurements_by_sensor.get(str(measurement.sensor), [])
        items.append({
            "x": measurement.timestamp.astimezone(get_current_timezone())
            .strftime("%H:%M %d.%m."),
            "y": measurement.value
        })
        all_labels.add(measurement.timestamp)
        measurements_by_sensor.update({str(measurement.sensor): items})

    context = {
        'datasets': [{"label": f'Sensor {key}', "data": values, "fill": "false",
                      "borderColor": random.choice(COLORS)}
                     for key, values in measurements_by_sensor.items()],
        "labels": [i.astimezone(get_current_timezone()).strftime("%H:%M %d.%m.")
                   for i in sorted(list(all_labels))],
        "limit": limit_hours
    }

    return render(request, 'measurements/charts.html', context)
