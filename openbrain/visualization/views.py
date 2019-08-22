import json
import logging

from typing import Dict
from flask import Blueprint, abort, jsonify, request

from ..cache import cache
from ..models import GeneratedImage, db
from ..common import _get_image_entry_by_id
from ..file_copy_script import MRIFileSimulator

visualization_bp = Blueprint('visualization_bp', __name__)

logger = logging.getLogger('viz_logger')
logger.setLevel(logging.DEBUG)

mri_simulator = None


def _create_generated_image_model(req_dict: Dict[str, str]):
    """
    Creates a GeneratedImage model from a dictionary

    :param req_dict: Dictionary object containing request parameters
    from a filesystem event
    :return: A GeneratedImage model
    """
    image_model = GeneratedImage(experiment_name=req_dict['experiment_name'],
                                 volume_name=req_dict['volume_name'],
                                 sprite_b64=req_dict['sprite_b64'],
                                 sprite_json=req_dict['sprite_json'],
                                 stat_map_b64=req_dict['stat_map_b64'],
                                 colormap_b64=req_dict['colormap_b64'])
    return image_model


@visualization_bp.route('/api/fs-event', methods=['POST'])
def post_fs_event():
    if request.method == 'POST':
        if request.is_json:
            # Get JSON data from request
            req_dict = request.get_json()

            # Create a GeneratedImage model from the JSON data
            # obtained earlier
            image_model = _create_generated_image_model(json.loads(req_dict))

            # Add the GeneratedImage model to the current session
            db.session.add(image_model)

            # Attempt to push changes to database
            try:
                db.session.commit()
                logger.log(
                    logging.INFO, "New file location added to the database")
                return jsonify(success=True)
            except Exception as ex:
                logger.log(logging.WARNING,
                           "Failed adding to the database: " + str(ex))
                return jsonify(success=False)

        return jsonify(success=False)


@visualization_bp.route('/api/sprite/<string:experiment_name>/<int:image_id>')
@cache.cached(timeout=600)
def get_sprite(experiment_name, image_id):
    if request.method == 'GET':
        # Get volume from database
        entry = _get_image_entry_by_id(experiment_name, image_id)

        if entry is not None:
            # Get the sprite and the parameters associated with
            # the current volume
            bg_sprite_b64 = entry.sprite_b64
            bg_params = entry.sprite_json

            bg_params_json = json.loads(bg_params)

            # Format image as an inline base64 PNG image
            sprite_img = 'data:image/png;base64, {}'.format(bg_sprite_b64)

            # Define the brainsprite params
            # noinspection PyDictCreation
            sprite_params = {
                'canvas': '3Dviewer',
                'sprite': 'spriteImg',
                'colorBackground': '#000000',
                'crosshair': True,
                'flagCoordinates': True,
                'title': False,
                'colorFont': '#ffffff',
                'flagValue': False,
                'colorCrosshair': '#de101d',
                'voxelSize': '1',
            }

            sprite_params['nbSlice'] = bg_params_json['nbSlice']
            sprite_params['affine'] = bg_params_json['affine']

            return jsonify(sprite_img=sprite_img, sprite_params=sprite_params)

    # Return a 404 response when a volume is not found or request
    # method is not GET
    return abort(404)


@visualization_bp.route(
    '/api/sprite/overlay/<string:experiment_name>/<int:image_id>')
@cache.cached(timeout=600)
def get_sprite_stat_map(experiment_name, image_id):
    if request.method == 'GET':
        # Get volume from database
        entry = _get_image_entry_by_id(experiment_name, image_id)

        if entry is not None:
            # Get sprites and parameters associated with the current volume
            bg_img_b64 = entry.sprite_b64
            sprite_params_json = entry.sprite_json
            sprite_params = json.loads(sprite_params_json)
            stat_map_b64 = entry.stat_map_b64
            colormap_b64 = entry.colormap_b64

            return jsonify(sprite_img='data:image/png;base64,' + bg_img_b64,
                           sprite_params=sprite_params,
                           stat_map_b64='data:image/png;base64,' +
                                        stat_map_b64,
                           cm_b64='data:image/jpg;base64,' + colormap_b64)

    return abort(404)


@visualization_bp.route('/api/sim/<int:repetition_time>/<int:num_of_volumes>',
                        methods=['GET'])
def start_real_time_simulation(repetition_time, num_of_volumes):
    if request.method == 'GET':
        mri_simulator = MRIFileSimulator(repetition_time, num_of_volumes)
        mri_simulator.run()
        return jsonify(success=True)
    else:
        abort(405)
