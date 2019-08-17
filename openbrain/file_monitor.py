import json
import logging
import os
import time
import nibabel
import requests

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from openbrain.common import DisplayMode, SAMPLE_DATA_DIR, TEST_DATA_DIR

from .visualization import utils

logger = logging.getLogger('fm_logger')
logger.setLevel(logging.DEBUG)

DEFAULT_DIRECTORY_TO_WATCH = TEST_DATA_DIR

DEFAULT_URL = 'http://0.0.0.0:8080/api/fs-event'

REQ_HEADERS = {
    "Content-Type": "application/json"
}

ROI_FILE_NAME = ''

json_data = {
    "experiment_name": None,
    "volume_name": None,
    "sprite_b64": None,
    "sprite_json": None,
    "stat_map_b64": None,
    "colormap_b64": None
}

display_mode = DisplayMode.FMRI


class Handler(FileSystemEventHandler):

    def __init__(self):
        logger.log(logging.INFO, "Handler initialized")

    @staticmethod
    def on_any_event(event, **kwargs):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Send a POST request if the file is not a hidden file
            # (filename starting with a dot)
            if str(event.src_path)[len(DEFAULT_DIRECTORY_TO_WATCH)] != '.':
                print("Received created event - %s." % event.src_path)
                try:
                    if display_mode == DisplayMode.FMRI:
                        # Load the generated volume and create sprite base64
                        # and the corresponding JSON parameters
                        bg_image = nibabel.load(event.src_path)
                        sprite_b64, sprite_json = \
                            utils.generate_background_sprite(bg_image)

                        # Update request parameters in the request JSON
                        # dictionary
                        json_data["volume_name"] = str(event.src_path)
                        json_data["sprite_b64"] = sprite_b64
                        json_data["sprite_json"] = sprite_json.getvalue()

                    elif display_mode == DisplayMode.OVERLAY:
                        # Load the generated image
                        bg_image = nibabel.load(event.src_path)

                        # Load the ROI image
                        stat_map_img = nibabel.load(os.path.join(
                            SAMPLE_DATA_DIR,
                            ROI_FILE_NAME))

                        # Get the JSON parameters of the sprite, and the
                        # base64 encoded sprite, stat map and colormap
                        sprite_json, sprite_b64, stat_map_b64, colormap_b64 = \
                            utils.get_stat_map(
                                stat_map_img,
                                bg_image,
                                opacity=0.7,
                                annotate=True,
                                colorbar=True)

                        # Update request parameters in the request JSON
                        # dictionary
                        json_data["volume_name"] = str(event.src_path)
                        json_data["sprite_b64"] = sprite_b64
                        json_data["sprite_json"] = json.dumps(sprite_json)
                        json_data["stat_map_b64"] = stat_map_b64
                        json_data["colormap_b64"] = colormap_b64

                    # Send the POST request in order to notify the server
                    # regarding the newly generated image and the
                    # corresponding sprites and parameters
                    r = requests.post(DEFAULT_URL, json=json.dumps(
                        json_data), headers=REQ_HEADERS)

                    logger.log(logging.INFO, r)
                except Exception as e:
                    logger.log(logging.WARN, str(e))


# Initiate a watchdog observer
observer = Observer()


def run():
    """
    Starts the file system monitoring process
    """

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
