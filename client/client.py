import schedule
import time
import os
import requests

from dotenv import load_dotenv
from temper import Temper

load_dotenv()

temper = Temper()


def get_measurements():
    measurements = temper.read()
    post(measurements)


def post(measurements):
    payload = [{
        "sensor": measurement["devnum"],
        "value": measurement["internal temperature"],
        "type": 1
    } for measurement in measurements]

    if not payload:
        return

    requests.post(os.getenv('BACKEND_URL'), json=payload)


get_measurements()
schedule.every(int(os.getenv('INTERVAL', 5))).minutes.do(get_measurements)

while True:
    schedule.run_pending()
    time.sleep(10)
