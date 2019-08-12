import json
import logging
import nibabel
import numpy as np

from typing import Dict, List
from collections import OrderedDict

from flask import Blueprint, abort, jsonify, render_template, request

from .. import file_monitor
from ..cache import cache
from ..models import Experiment, GeneratedImage, db
from . import config

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


def _convert_real_world_to_voxel_coordinates(image: nibabel.nifti1.Nifti1Image, coordinates) -> List[int]:
    voxel_coords = nibabel.affines.apply_affine(
        np.linalg.inv(image.affine), coordinates)
    voxel_coords = [int(coord) for coord in voxel_coords]

    return voxel_coords

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
    try:
        entries = GeneratedImage.query.filter_by(
            experiment_name=experiment_name).all()
        entry = entries[volume_id - 1]
    except IndexError:
        entry = None

    return entry


@visualization_bp.route('/api/sprite/<string:experiment_name>/<int:image_id>')
@cache.cached(timeout=600)
def get_sprite(experiment_name, image_id):
    if request.method == 'GET':
        entry = _get_image_entry_by_id(experiment_name, image_id)
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
def post_experiment_settings():
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
                file_monitor.display_mode = config.DisplayMode.FMRI
            elif req_dict['display_mode'] == 'overlay':
                file_monitor.display_mode = config.DisplayMode.OVERLAY
                file_monitor.ROI_FILE_NAME = req_dict['overlay_filename']

            return jsonify(success=True)

        return jsonify(success=False)


def _get_voxel_value_table(experiment_name, image_id, real_world_coordinates_list):
    voxel_values = OrderedDict()

    for id in range(1, image_id + 1):
        image_entry = _get_image_entry_by_id(experiment_name, id)
        if image_entry is not None:
            image = nibabel.load(image_entry.volume_name)
            image_data = image.get_data()
            voxel_coordinates = _convert_real_world_to_voxel_coordinates(image, real_world_coordinates_list)

            try:
                voxel_values[id] = image_data[voxel_coordinates[0], voxel_coordinates[1], voxel_coordinates[2]]
            except IndexError:
                voxel_values[id] = 0

    return voxel_values


@visualization_bp.route('/api/voxel', methods=['POST'])
def post_voxel_value():
    if request.method == 'POST':
        if request.is_json:
            req_dict = request.get_json()

            experiment_name = req_dict['experiment_name']
            image_id = req_dict['image_id']
            voxel_coordinates = req_dict['voxel_coordinates']

            coordinate_x = voxel_coordinates['x'][0]
            coordinate_y = voxel_coordinates['y'][0]
            coordinate_z = voxel_coordinates['z'][0]

            real_world_coordinates_list = [coordinate_x, coordinate_y, coordinate_z]

            voxel_values = _get_voxel_value_table(experiment_name, image_id, real_world_coordinates_list)

            return jsonify(voxel_values=voxel_values)
