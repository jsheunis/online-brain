import nibabel
import json
import logging
import os

from flask import request, render_template, jsonify, Blueprint, abort
from typing import Dict

from .config import DisplayMode

from ..models import GeneratedImage, Experiment, db
from .. import file_monitor
from ..cache import cache

visualization_bp = Blueprint('visualization_bp', __name__)

logger = logging.getLogger('viz_logger')
logger.setLevel(logging.DEBUG)


def _create_generated_image_model(req_dict: Dict[int, str]):

    image_model = GeneratedImage(experiment_name=req_dict['experiment_name'],
                                 volume_name=req_dict['volume_name'],
                                 sprite_b64=req_dict['sprite_b64'],
                                 sprite_json=req_dict['sprite_json'],
                                 stat_map_b64=req_dict['stat_map_b64'],
                                 colormap_b64=req_dict['colormap_b64'])
    return image_model


@visualization_bp.route('/')
def index():
    return render_template('viz_base.html')


@visualization_bp.route('/api/fs-event', methods=['POST'])
def post_fs_event():
    if request.method == 'POST':
        if request.is_json:
            req_dict = request.get_json()
            image_model = _create_generated_image_model(json.loads(req_dict))

            db.session.add(image_model)

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


def _get_image_entry_by_id(experiment_name, volume_id):
    entries = GeneratedImage.query.filter_by(
        experiment_name=experiment_name).all()
    entry = entries[volume_id - 1]
    return entry


@visualization_bp.route('/api/sprite/<string:experiment_name>/<int:image_id>')
@cache.cached(timeout=600)
def get_sprite(experiment_name, image_id):
    if request.method == 'GET':
        entry = _get_image_entry_by_id(experiment_name, image_id)
        print(entry)
        if entry is not None:
            bg_sprite_b64 = entry.sprite_b64
            bg_params = entry.sprite_json

            bg_params_json = json.loads(bg_params)

            sprite_img = 'data:image/png;base64, {}'.format(bg_sprite_b64)

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
    return abort(404)


@visualization_bp.route('/api/sprite/overlay/<string:experiment_name>/<int:image_id>')
@cache.cached(timeout=600)
def get_sprite_stat_map(experiment_name, image_id):
    if request.method == 'GET':
        entry = _get_image_entry_by_id(experiment_name, image_id)
        if entry is not None:
            bg_img_b64 = entry.sprite_b64
            sprite_params_json = entry.sprite_json
            sprite_params = json.loads(sprite_params_json)
            stat_map_b64 = entry.stat_map_b64
            colormap_b64 = entry.colormap_b64

            return jsonify(sprite_img='data:image/png;base64,' + bg_img_b64,
                           sprite_params=sprite_params,
                           stat_map_b64='data:image/png;base64,' + stat_map_b64,
                           cm_b64='data:image/jpg;base64,' + colormap_b64)
    return abort(404)


@visualization_bp.route('/api/settings', methods=['POST'])
def get_experiment_settings():
    if request.method == 'POST':
        if request.is_json:
            req_dict = request.get_json()

            def experiment_exists(experiment_name):
                entry = Experiment.query.filter_by(
                    experiment_name=experiment_name).first()
                return entry is not None

            if experiment_exists(req_dict['experiment_name']):
                logger.log(logging.WARNING, "Experiment already in database")
            else:
                experimentModel = Experiment(
                    experiment_name=req_dict['experiment_name'])
                try:
                    db.session.add(experimentModel)
                    db.session.commit()
                    logger.log(logging.INFO, "Experiment added to database")
                except Exception as ex:
                    logger.log(
                        logging.WARN, "Failed adding experiment to database: " + str(ex))

            # Set file monitor JSON_DATA parameters
            file_monitor.JSON_DATA['experiment_name'] = req_dict['experiment_name']
            
            # Set file monitor display_mode
            if req_dict['display_mode'] == 'fMRI':
                file_monitor.display_mode = DisplayMode.FMRI
            elif req_dict['display_mode'] == 'overlay':
                file_monitor.display_mode = DisplayMode.OVERLAY

            return jsonify(success=True)
        return jsonify(success=False)
