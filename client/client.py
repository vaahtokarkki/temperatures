import hashlib
import logging
import os
import time

import requests
import schedule
from dotenv import load_dotenv

from temper import Temper

load_dotenv()

temper = Temper()
logger = logging.getLogger("main")
logger.setLevel(os.getenv("LOG_LEVEL"), logging.ERROR)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s',
                              datefmt='%d.%m.%y %H:%M')
console = logging.StreamHandler()
console.setFormatter(formatter)
logger.addHandler(console)


def get_measurements():
    measurements = temper.read()
    logger.debug('Read measurements: {measurements}')
    post(measurements)


def _get_headers():
    token = os.getenv('API_TOKEN', None)
    if not token:
        return {}

    hash = hashlib.sha256(bytes(token, 'utf-8')).hexdigest()
    return {
        'Authorazion': f'Basic {hash}'
    }


def post(measurements):
    payload = [{
        "sensor": measurement["devnum"],
        "value": measurement["internal temperature"],
        "type": 1
    } for measurement in measurements]

    if not payload:
        return

    logger.debug(f'Posting: {payload}')
    requests.post(os.getenv('BACKEND_URL'), json=payload, headers=_get_headers())


get_measurements()
schedule.every(int(os.getenv('INTERVAL', 5))).minutes.do(get_measurements)

while True:
    schedule.run_pending()
    time.sleep(10)
