import nibabel
import numpy as np
import logging

from collections import OrderedDict
from typing import List
from flask import Blueprint, jsonify, request, abort

from ..common import _get_image_entry_by_id

plotting_bp = Blueprint('plotting_bp', __name__)

logger = logging.getLogger('plotting_logger')
logger.setLevel(logging.DEBUG)


def _convert_real_world_to_voxel_coordinates(image: nibabel.nifti1.Nifti1Image,
                                             coordinates) -> List[int]:
    """
    Converts a list of real world coordiantes to voxel coordinates

    :param image: A Nifti image object
    :param coordinates: The real world coordinates to be converted
    :return: A list of voxel coordinates
    """
    voxel_coords = nibabel.affines.apply_affine(
        np.linalg.inv(image.affine), coordinates)
    voxel_coords = [int(coord) for coord in voxel_coords]

    return voxel_coords


def _get_voxel_value_table(experiment_name, image_id,
                           real_world_coordinates_list):
    """
    Computes a list containing the voxel values at a desired location
     of every image which is part of an experiment and has id <= image_id

    :param experiment_name: The name of the experiment
    :param image_id: The id of the current image
    :param real_world_coordinates_list: A list of real world coordinates
     for which the user wants to get the values

    :return: A list containing voxel values at a specified location
     of each image which is part of the experiment and whose order number is
     smaller than the id of the current image
    """
    voxel_values = OrderedDict()
    image_id = int(image_id)
    for id_iter in range(1, image_id + 1):
        # Get volume from database
        image_entry = _get_image_entry_by_id(experiment_name, id_iter)
        if image_entry is not None:
            try:
                # Load the volume
                image = nibabel.load(image_entry.volume_name)

                # Get the voxel data from the image
                image_data = image.get_data()

                # Convert the real world coordinates to voxel coordinates
                voxel_coordinates = _convert_real_world_to_voxel_coordinates(
                    image,
                    real_world_coordinates_list)

                try:
                    # Build the voxel values list
                    voxel_values[id_iter] = image_data[voxel_coordinates[0],
                                                       voxel_coordinates[1],
                                                       voxel_coordinates[2]]
                except IndexError:
                    # If some coordinates that do not exist are entered, then
                    # return 0. This case happens due to the fact that the
                    # 'brainsprite' library displays additional space around
                    #  the brain image.
                    voxel_values[id_iter] = 0
            except FileNotFoundError:
                # This can occur whenever an old experiment is accessed and
                # the Nifti files are not present anymore in the directory
                return None

    return voxel_values


@plotting_bp.route('/api/voxel', methods=['POST'])
def post_voxel_value():
    if request.method == 'POST':
        if request.is_json:
            req_dict = request.get_json()

            # Get the data from the request
            experiment_name = req_dict['experiment_name']
            image_id = req_dict['image_id']
            voxel_coordinates = req_dict['voxel_coordinates']

            coordinate_x = voxel_coordinates['x'][0]
            coordinate_y = voxel_coordinates['y'][0]
            coordinate_z = voxel_coordinates['z'][0]

            # Create a list with the real world coordinates
            real_world_coordinates_list = [coordinate_x,
                                           coordinate_y,
                                           coordinate_z]
            # Get the voxel values at the specified coordinates
            voxel_values = _get_voxel_value_table(experiment_name, image_id,
                                                  real_world_coordinates_list)
            if voxel_values is not None:
                return jsonify(voxel_values=voxel_values)
            else:
                abort(404)
