from .models import Measurement


def test_add_measurement(client):
    response = client.post('/api/measurement/', {"sensor": 1, "value": 1.337})
    assert response.status_code == 201
    assert Measurement.objects.count() == 1


def test_add_invalid_measurement(client):
    response = client.post('/api/measurement/', {"sensor": 1})
    assert response.status_code == 400
    assert Measurement.objects.count() == 0


def test_add_missing_sensor(client):
    response = client.post('/api/measurement/', {"value": 1.337})
    assert response.status_code == 400
    assert Measurement.objects.count() == 0
