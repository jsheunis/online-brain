import nibabel
import os
import json
import time
import logging

from flask import request, render_template, jsonify, Blueprint, abort
from io import BytesIO, StringIO
from base64 import encodebytes
from brainsprite import save_sprite
from typing import Dict

from .config import SAMPLE_DATA_DIR, VOLUME_FILE_EXTENSION, TEST_DATA_DIR, VOLUME_FILE_NAME

from ..models import GeneratedImage, Experiment, db
from .. import file_monitor

visualization_bp = Blueprint('visualization_bp', __name__)

logger = logging.getLogger('viz_logger')
logger.setLevel(logging.DEBUG)

new_image = nibabel.load(os.path.join(SAMPLE_DATA_DIR, VOLUME_FILE_NAME + VOLUME_FILE_EXTENSION))

def generate_sprite_base64(volume):    
    generated_sprite = BytesIO()
    bg_json = StringIO()
    save_sprite(volume, output_sprite=generated_sprite, output_json=bg_json, format='jpg', resample=True, cmap='Greys_r')
    generated_sprite.seek(0)
    bg_base64 = encodebytes(generated_sprite.read()).decode('utf-8')
    generated_sprite.close()

    return bg_base64, bg_json

bg_sprite_b64, bg_sprite_json = generate_sprite_base64(new_image)
bg_sprite_json.seek(0)
params = json.load(bg_sprite_json)

sprite_params = {
                    'canvas': '3Dviewer',
                    'sprite': 'spriteImg',
                    'nbSlice': params['nbSlice'],
                    'colorBackground': '#000000',
                    'crosshair': True,
                    'affine': params['affine'],
                    'flagCoordinates': True,
                    'title': False,
                    'colorFont': '#ffffff',
                    'flagValue': False,
                    'colorCrosshair': '#de101d',
                    'voxelSize': '1',
                }

def _create_generated_image_model(req_dict: Dict[int, str]):
    image_model = GeneratedImage(experiment_name=req_dict['experiment_name'], 
                        volume_name=req_dict['volume_name'])
    return image_model

@visualization_bp.route('/')
def index():
    dumped_sprite_params = json.dumps(sprite_params)
    return render_template('viz_base.html', SPRITE_BG_IMAGE_B64='data:image/png;base64,' + bg_sprite_b64, SPRITE_JSON_PARAMS=dumped_sprite_params)
 
@visualization_bp.route('/api/fs-event', methods=['POST'])
def post_fs_event():
        if request.method == 'POST':
            if request.is_json:
                req_dict = request.get_json()
                image_model = _create_generated_image_model(json.loads(req_dict))
                
                db.session.add(image_model)
                
                try:
                    db.session.commit()
                    logger.log(logging.INFO, "New file location added to the database")
                    return jsonify(success=True)
                except Exception as ex:
                    logger.log(logging.WARNING, "Failed adding to the database: " + str(ex))
                    return jsonify(success=False)

            return jsonify(success=False)
    
def _get_image_entry_by_id(experiment_name, volume_id):
    entries = GeneratedImage.query.filter_by(experiment_name=experiment_name).all()
    entry = entries[volume_id - 1]
    return entry

@visualization_bp.route('/api/sprite/<string:experiment_name>/<int:image_id>')
def get_sprite(experiment_name, image_id):
    if request.method == 'GET':
        entry = _get_image_entry_by_id(experiment_name, image_id)
        print(entry)
        if entry is not None:
            image_src = entry.volume_name
            nb_image = nibabel.load(image_src)
            
            bg_sprite_b64, _ = generate_sprite_base64(nb_image)
            response = 'data:image/png;base64, {}'.format(bg_sprite_b64)

            return response
    return abort(404)

@visualization_bp.route('/api/settings/<string:experiment_name>')
def get_experiment_settings(experiment_name):
    if request.method == 'GET':
        def experiment_exists(experiment_name):
            entry = Experiment.query.filter_by(experiment_name=experiment_name).first()
            return entry is not None

        if experiment_exists(experiment_name): 
            logger.log(logging.WARNING, "Experiment already in database")
        else:
            experimentModel = Experiment(experiment_name=experiment_name)
            try:
                db.session.add(experimentModel)
                db.session.commit()
            except Exception as ex:
                logger.log(logging.WARN, "Failed adding experiment to database: " + str(ex))
            logger.log(logging.INFO, "Experiment added to database")

        # Set file monitor JSON_DATA parameters
        file_monitor.JSON_DATA['experiment_name'] = experiment_name

        return jsonify(success=True)
        