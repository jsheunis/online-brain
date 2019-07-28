import brainsprite
import nibabel
import nilearn
import json
import os
from io import BytesIO, StringIO
from base64 import encodebytes
from nilearn._utils.niimg import _safe_get_data

DATA_DIR = 'sample_data/'
VOLUME_FILE_NAME = 'fanon-0007_00005'
VOLUME_FILE_EXTENSION = '.nii'
GENERATED_SPRITE_FILE_NAME = VOLUME_FILE_NAME + '-sprite'  

volume = nibabel.load(os.path.join(DATA_DIR, VOLUME_FILE_NAME + VOLUME_FILE_EXTENSION))
volume_data = volume.get_data()

def generate_sprite_base64(volume):    
    generated_sprite = BytesIO()
    bg_json = StringIO()
    brainsprite.save_sprite(volume, output_sprite=generated_sprite, output_json=bg_json, format='jpg')
    generated_sprite.seek(0)
    bg_base64 = encodebytes(generated_sprite.read()).decode('utf-8')
    generated_sprite.close()

    return bg_base64, bg_json


generated_sprite_b64, generated_sprite_json = generate_sprite_base64(volume)
generated_sprite_json.seek(0)
params = json.load(generated_sprite_json)

# Create a json-like structure with all the brain sprite parameters
sprite_params = {
                    'canvas': '3Dviewer',
                    'sprite': 'spriteImg',
                    'nbSlice': params['nbSlice'],
                    'colorBackground': '#000000',
                    'crosshair': True,
                    'affine': params['affine'],
                    'flagCoordinates': True,
                    'title': None,
                    'flagValue': True,
                }

html = brainsprite.get_html_template('../../viz.html')
html = html.replace('INSERT_SPRITE_PARAMS_HERE', json.dumps(sprite_params))
html = html.replace('INSERT_BG_DATA_HERE', generated_sprite_b64)

html_file = open("test.html", "w")
html_file.write(html)
