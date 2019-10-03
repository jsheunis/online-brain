import logging

from flask import Blueprint, jsonify, render_template, request, abort

from .. import common
from .. import file_monitor
from ..models import Experiment, db

settings_bp = Blueprint('settings_bp', __name__)

logger = logging.getLogger('settings_logger')
logger.setLevel(logging.DEBUG)


def _get_all_experiments_from_database():
    """
    Retrieves all experiments from the database
    :return: exp_name_list, a list containing only the experiment names
    """
    exp_data = Experiment.query.all()
    exp_name_list = [exp.experiment_name for exp in exp_data]

    return exp_name_list


@settings_bp.route('/')
def index():
    # Renders the index page
    exp_list = _get_all_experiments_from_database()
    return render_template('viz_base.html', exp_list=exp_list)


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
                    experiment_name=req_dict['experiment_name'],
                    number_of_volumes=req_dict['number_of_volumes'],
                    repetition_time=req_dict['repetition_time'])
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


def _get_exp_data_from_database(exp_name):
    """
    Returns the experiment object from the database with all the data
    :param exp_name: The name of the experiment
    :return: experiment: The Experiment object
    """

    experiment = Experiment.query.filter_by(experiment_name=exp_name).first()
    return experiment


@settings_bp.route('/api/settings/<string:exp_name>', methods=['GET'])
def get_experiment_settings(exp_name):
    if request.method == 'GET':
        # Get experiment data from database
        exp_data = _get_exp_data_from_database(exp_name)

        if exp_data is not None:
            exp_volumes_nr = exp_data.number_of_volumes
            exp_repetition_time = exp_data.repetition_time

            return jsonify(exp_volumes_nr=exp_volumes_nr,
                           exp_repetition_time=exp_repetition_time)
        abort(404)
