"""
Config file containing hardcoded app information and methods used by multiple
app modules
"""

from enum import Enum
from .models import GeneratedImage
from flask_socketio import SocketIO

SAMPLE_DATA_DIR = 'sample_data/'

TEST_DATA_DIR = 'test_data/'

socketio = SocketIO()


class DisplayMode(Enum):
    FMRI = 1
    OVERLAY = 2


def _get_image_entry_by_id(experiment_name, volume_id):
    """
    Queries the database regarding the volume with order number <volume_id>
    that is part of experiment <experiment_name>

    :param experiment_name: The name of the experiment
    :param volume_id: The order number of the volume in the experiment
    :return: GeneratedImage model that satisfies query
    """
    try:
        entries = GeneratedImage.query.filter_by(
            experiment_name=experiment_name).all()
        entry = entries[volume_id - 1]
    except IndexError:
        entry = None

    return entry
