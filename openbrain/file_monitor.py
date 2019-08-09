import time
import logging
import requests
import json
import nibabel
import os

from .visualization import utils
from .visualization.config import DisplayMode, SAMPLE_DATA_DIR

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DEFAULT_DIRECTORY_TO_WATCH = 'test_data/'

DEFAULT_URL = 'http://0.0.0.0:8080/api/fs-event'

JSON_DATA = {
    "experiment_name": None,
    "volume_name": None,
    "sprite_b64": None,
    "sprite_json": None,
    "stat_map_b64": None,
    "colormap_b64": None
}

REQ_HEADERS = {
    "Content-Type": "application/json"
}

ROI_FILE_NAME = ''

display_mode = DisplayMode.FMRI

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
            # Send a POST request if the file is not a hidden file (starting with '.')
            if (str(event.src_path)[len(DEFAULT_DIRECTORY_TO_WATCH)] != '.'):
                print("Received created event - %s." % event.src_path)
                try:
                    if display_mode == DisplayMode.FMRI:
                        bg_image = nibabel.load(event.src_path)
                        sprite_b64, sprite_json = utils.generate_background_sprite(
                            bg_image)

                        JSON_DATA["volume_name"] = str(event.src_path)
                        JSON_DATA["sprite_b64"] = sprite_b64
                        JSON_DATA["sprite_json"] = sprite_json.getvalue()

                    elif display_mode == DisplayMode.OVERLAY:
                        bg_image = nibabel.load(event.src_path)
                        stat_map_img = nibabel.load(os.path.join(
                            SAMPLE_DATA_DIR,
                            ROI_FILE_NAME))
                        print(ROI_FILE_NAME)
                        sprite_json, sprite_b64, stat_map_b64, colormap_b64 = utils.get_stat_map(
                            stat_map_img, bg_image, opacity=0.7, annotate=True, colorbar=True)
                        JSON_DATA["volume_name"] = str(event.src_path)
                        JSON_DATA["sprite_b64"] = sprite_b64
                        JSON_DATA["sprite_json"] = json.dumps(sprite_json)
                        JSON_DATA["stat_map_b64"] = stat_map_b64
                        JSON_DATA["colormap_b64"] = colormap_b64
                        
                    r = requests.post(DEFAULT_URL, json=json.dumps(
                        JSON_DATA), headers=REQ_HEADERS)

                    logger.log(logging.INFO, r)
                except Exception as e:
                    logger.log(logging.WARN, str(e))


observer = Observer()


def run():
    event_handler = Handler()
    observer.schedule(
        event_handler, DEFAULT_DIRECTORY_TO_WATCH, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(5)
    except Exception as ex:
        observer.stop()
        logger.log(logging.WARNING, str(ex))
    observer.join()
