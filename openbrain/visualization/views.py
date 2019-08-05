import nibabel
import json
import logging

from flask import request, render_template, jsonify, Blueprint, abort
from typing import Dict

from .utils import get_stat_map, generate_background_sprite
# from .config import SAMPLE_DATA_DIR, VOLUME_FILE_EXTENSION, ROI_FILE_NAME

from ..models import GeneratedImage, Experiment, db
from .. import file_monitor

visualization_bp = Blueprint('visualization_bp', __name__)

logger = logging.getLogger('viz_logger')
logger.setLevel(logging.DEBUG)

# Overlay image params
# overlay_image = nibabel.load(os.path.join(
#     SAMPLE_DATA_DIR, ROI_FILE_NAME + VOLUME_FILE_EXTENSION))
# overlay_sprite_b64, overlay_sprite_json = generate_overlay_sprite(
#     overlay_image)
# overlay_sprite_json.seek(0)
# overlay_params = json.load(overlay_sprite_json)


def _create_generated_image_model(req_dict: Dict[int, str]):
    image_model = GeneratedImage(experiment_name=req_dict['experiment_name'],
                                 volume_name=req_dict['volume_name'])
    return image_model


@visualization_bp.route('/')
def index():
    # sprite_params_v2, bg_sprite_b64, overlay_sprite_b64, colormap_b64 = get_stat_map(overlay_image, bg_img=new_image, opacity=0.6)
    # dumped_sprite_params = json.dumps(sprite_params_v2)

    # return render_template('viz_base.html', SPRITE_BG_IMAGE_B64='data:image/png;base64,' + bg_sprite_b64, SPRITE_JSON_PARAMS=dumped_sprite_params, SPRITE_OVERLAY_B64='data:image/png;base64,' + overlay_sprite_b64, COLORMAP_B64='data:image/png;base64,' + colormap_b64)

    #dumped_sprite_params = json.dumps(sprite_params)
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
def get_sprite(experiment_name, image_id):
    if request.method == 'GET':
        entry = _get_image_entry_by_id(experiment_name, image_id)
        print(entry)
        if entry is not None:
            image_src = entry.volume_name
            nb_image = nibabel.load(image_src)

            bg_sprite_b64, bg_params = generate_background_sprite(nb_image)
            bg_params.seek(0)

            bg_params_json = json.load(bg_params)

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


@visualization_bp.route('/api/settings/<string:experiment_name>')
def get_experiment_settings(experiment_name):
    if request.method == 'GET':
        def experiment_exists(experiment_name):
            entry = Experiment.query.filter_by(
                experiment_name=experiment_name).first()
            return entry is not None

        if experiment_exists(experiment_name):
            logger.log(logging.WARNING, "Experiment already in database")
        else:
            experimentModel = Experiment(experiment_name=experiment_name)
            try:
                db.session.add(experimentModel)
                db.session.commit()
            except Exception as ex:
                logger.log(
                    logging.WARN, "Failed adding experiment to database: " + str(ex))
            logger.log(logging.INFO, "Experiment added to database")

        # Set file monitor JSON_DATA parameters
        file_monitor.JSON_DATA['experiment_name'] = experiment_name

        return jsonify(success=True)
