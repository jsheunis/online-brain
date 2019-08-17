import logging

from flask import Blueprint, jsonify, render_template, request

from .. import common
from .. import file_monitor
from ..models import Experiment, db

settings_bp = Blueprint('settings_bp', __name__)

logger = logging.getLogger('settings_logger')
logger.setLevel(logging.DEBUG)


@settings_bp.route('/')
def index():
    # Renders the index page
    return render_template('viz_base.html')


@settings_bp.route('/api/settings', methods=['POST'])
def post_experiment_settings():
    if request.method == 'POST':
        if request.is_json:
            req_dict = request.get_json()

            def experiment_exists(experiment_name):
                """
                Check whether an experiment already exists in the database

                :param experiment_name: The name of the experiment
                :return: True if experiment already exists, False otherwise
                """
                entry = Experiment.query.filter_by(
                    experiment_name=experiment_name).first()

                return entry is not None

            if experiment_exists(req_dict['experiment_name']):
                logger.log(logging.WARNING, "Experiment already in database")
            else:
                # If the experiment is new, create an experiment model
                experiment_model = Experiment(
                    experiment_name=req_dict['experiment_name'])
                try:
                    # Push the experiment to the database
                    db.session.add(experiment_model)
                    db.session.commit()
                    logger.log(logging.INFO, "Experiment added to database")
                except Exception as ex:
                    logger.log(
                        logging.WARN, "Failed adding experiment to database: "
                                      + str(ex))

            # Update the file monitor json_data parameters
            file_monitor.json_data['experiment_name'] = \
                req_dict['experiment_name']

            # Set file monitor display_mode
            if req_dict['display_mode'] == 'fMRI':
                file_monitor.display_mode = common.DisplayMode.FMRI
            elif req_dict['display_mode'] == 'overlay':
                file_monitor.display_mode = common.DisplayMode.OVERLAY
                file_monitor.ROI_FILE_NAME = req_dict['overlay_filename']

            return jsonify(success=True)

        return jsonify(success=False)

