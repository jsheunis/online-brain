import nibabel
import os
import json
import time
import logging

from flask import Flask, request, send_file, make_response, render_template, jsonify, Blueprint
from io import BytesIO, StringIO
from base64 import encodebytes
from brainsprite import save_sprite
from typing import Dict

from .config import SAMPLE_DATA_DIR, VOLUME_FILE_EXTENSION, TEST_DATA_DIR, VOLUME_FILE_NAME

from ..models import GeneratedImage, db

visualization_bp = Blueprint('visualization_bp', __name__)

new_image = nibabel.load(os.path.join(SAMPLE_DATA_DIR, VOLUME_FILE_NAME + VOLUME_FILE_EXTENSION))

processed_files = []

file_log = open(os.path.join(os.getcwd(), "file_log.txt"), "r")

def follow(log_file):
    while True:
        line = log_file.readline()
        stripped_line = line.rstrip()
        yield stripped_line


def generate_sprite_base64(volume):    
    generated_sprite = BytesIO()
    bg_json = StringIO()
    save_sprite(volume, output_sprite=generated_sprite, output_json=bg_json, format='jpg')

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
                    'colorBackground': '#ffffff',
                    'crosshair': True,
                    'affine': params['affine'],
                    'flagCoordinates': True,
                    'title': False,
                    'flagValue': True,
                    'colorFont': '#000000',
                    'flagValue': False,
                    'colorCrosshair': '#de101d'
                }

def _create_generated_image_model(req_dict: Dict[int, str]):
    image_model = GeneratedImage(experiment_id=req_dict['experiment_id'], 
                        volume_name=req_dict['volume_name'])
    return image_model

@visualization_bp.route('/')
def index():
    dumped_sprite_params = json.dumps(sprite_params)
    return render_template('viz_base.html', SPRITE_BG_IMAGE_B64='data:image/png;base64,' + bg_sprite_b64, SPRITE_JSON_PARAMS=dumped_sprite_params)

@visualization_bp.route('/api/fs-event', methods=['POST'])
def get_fs_event():
        if request.method == 'POST':
            if request.is_json:
                req_dict = request.get_json()
                image_model = _create_generated_image_model(json.loads(req_dict))
                
                db.session.add(image_model)
                
                try:
                    db.session.commit()
                    logging.log(logging.INFO, "New file location added to the database")
                    return jsonify(success=True)
                except Exception as ex:
                    logging.log(logging.INFO, str(ex))
                    return jsonify(success=False)

            return jsonify(success=False)
    
def _get_first_unprocessed_image_entry():
    entry = GeneratedImage.query.filter_by(processed_flag=False).first()
    return entry

@visualization_bp.route('/api/sprite')
def get_sprite():
    if request.method == 'GET':
        entry = _get_first_unprocessed_image_entry()
        if entry is not None:
            file_src = entry.volume_name
            nb_image = nibabel.load(file_src)

            # Mark the image as processed in the database
            entry.processed_flag = True
            db.session.commit()
            processed_files.append(entry.volume_name)

            bg_sprite_b64, _ = generate_sprite_base64(nb_image)
            response = 'data:image/png;base64, {}'.format(bg_sprite_b64)
            
            return response
    
    return jsonify(success=False)

        # if len(files) > 0:
        #     image_src = files.pop(0)
        #     image = nibabel.load(image_src)
        #     bg_sprite_b64, _ = generate_sprite_base64(image)
        #     response = 'data:image/png;base64, {}'.format(bg_sprite_b64)
        #     return response
        
        # Get the generator object
        #files = follow(file_log)

        #next_file = files.__next__()
        #next_file.rstrip()
        # Pass in order to avoid duplicate files
        #if next_file not in processed_files:
        #    processed_files.append(os.path.join(os.getcwd(), next_file))
        
        #print (processed_files)
        
        #if len(processed_files) > 0:
        #    file_to_process = processed_files[0] 
        #    processed_files.pop(0)
        
        #file_to_process = GeneratedImage.query.all()
        #print(file_to_process)

        #image_to_process = nibabel.load(file_to_process)

        #bg_sprite_b64, _ = generate_sprite_base64(image_to_process)
        
        #response = 'data:image/png;base64, {}'.format(bg_sprite_b64)
        
        #return response
