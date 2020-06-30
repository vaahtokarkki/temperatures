import json
from datetime import timedelta

from django.db.models import Avg, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Measurement
from .utils import get_minutes, get_night_low_measurements, save_measurement, authorized


@csrf_exempt
def create_measurement(request):
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
    latest_measurements = Measurement.objects \
        .filter(timestamp__gt=now - timedelta(days=1)) \
        .order_by('sensor', '-timestamp').distinct('sensor')

    averages = Measurement.objects \
        .filter(timestamp__gt=now - timedelta(hours=1)) \
        .values('sensor').annotate(avg=Avg('value'), sum=Sum('value'))
    
    stats_by_sensor = {
        sensor["sensor"]: {
            "avg": sensor["avg"],
            "sum": sensor["sum"]
        } for sensor in averages
    }

    context = {
        "latest_measurements": [{
            "sensor": measurement.sensor,
            "value": measurement.value,
            "type": "temperature",
            "timestamp": measurement.timestamp.strftime("%H:%M %d.%m."),
            "mins_ago": get_minutes(now - measurement.timestamp),
            "hour_avg": round(stats_by_sensor[measurement.sensor]["avg"], 2),
            "hour_delta": round(stats_by_sensor[measurement.sensor]["sum"], 2)
        } for measurement in latest_measurements],
        "night_low": [{
            "sensor": measurement.sensor,
            "value": measurement.value,
            "timestamp": measurement.timestamp.strftime("%H:%M %d.%m."),
        } for measurement in measurements_of_night]
    }

    return render(request, 'measurements/index.html', context)


def graphs(request):
    try:
        limit_hours = int(request.GET.get("limit", 4))
    except ValueError:
        return render(request, 'measurements/charts.html')

    limit_timestamp = timezone.now() - timedelta(hours=limit_hours)
    measurements_temperature = Measurement.objects \
        .filter(timestamp__gt=limit_timestamp, type=Measurement.TYPE_TEMPERATURE)

    measurements_by_sensor = {}
    all_labels = set()
    for measurement in measurements_temperature:
        items = measurements_by_sensor.get(str(measurement.sensor), [])
        formated_timestamp = measurement.timestamp.strftime("%H:%M %d.%m.")
        items.append({
            "x": formated_timestamp,
            "y": measurement.value
        })
        all_labels.add(formated_timestamp)
        measurements_by_sensor.update({str(measurement.sensor): items})

    context = {
        'datasets': [{"label": f'Sensor {key}', "data": values}
                     for key, values in measurements_by_sensor.items()],
        "labels": list(all_labels)
    }

    return render(request, 'measurements/charts.html', context)
