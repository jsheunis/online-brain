import time
import collections
import logging
import requests
import json

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DEFAULT_DIRECTORY_TO_WATCH = 'test_data/'

DEFAULT_URL = 'http://0.0.0.0:8080/api/fs-event'

JSON_DATA = {
            "experiment_name": 1,
            "volume_name": None
            }

REQ_HEADERS = {
            "Content-Type": "application/json"
            }

logger = logging.getLogger('viz_logger')
logger.setLevel(logging.DEBUG)

class Handler(FileSystemEventHandler):

    def __init__(self):
        logger.log(logging.INFO, "Handler initialized")

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Send a POST request if the file is not a hidden file (stating with '.')
            if (str(event.src_path)[len(DEFAULT_DIRECTORY_TO_WATCH)] != '.'):
                print("Received created event - %s." % event.src_path)
                try:
                    JSON_DATA["volume_name"] = str(event.src_path)
                    r = requests.post(DEFAULT_URL, json=json.dumps(JSON_DATA), headers=REQ_HEADERS)
                    logger.log(logging.INFO, r)
                except Exception as e:
                    logger.log(logging.INFO, str(e))

observer = Observer()
        
def run():
    event_handler = Handler()
    observer.schedule(event_handler, DEFAULT_DIRECTORY_TO_WATCH, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(5)
    except:
        observer.stop()
        logger.log(logging.WARNING, "Error")
    observer.join()
