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
            "experiment_id": 1,
            "volume_name": None
            }

REQ_HEADERS = {
            "Content-Type": "application/json"
            }

class Watcher:

    def __init__(self, directory_to_watch=DEFAULT_DIRECTORY_TO_WATCH):
        self.observer = Observer()
        self.DIRECTORY_TO_WATCH = directory_to_watch
        
    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Error")
            
        self.observer.join()

class Handler(FileSystemEventHandler):

    def __init__(self):
        logging.info("Handler initialized")

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print("Received created event - %s." % event.src_path)
            try:
                #file_log = open("file_log.txt", "a")
                #file_log.write(event.src_path + '\n')
                JSON_DATA["volume_name"] = str(event.src_path)
                r = requests.post(DEFAULT_URL, json=json.dumps(JSON_DATA), headers=REQ_HEADERS)
                logging.log(logging.INFO, r)
            except Exception as e:
                logging.log(logging.INFO, str(e))

if __name__=='__main__':
    w = Watcher()
    w.run()