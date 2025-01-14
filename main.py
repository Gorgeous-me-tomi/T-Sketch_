import os
import cv2
import io
import random
from PIL import Image
from werkzeug.utils import secure_filename
from flask import Flask, render_template, redirect, url_for, request, flash

import requests as r
from my_requests import Connect
import json

from dotenv import load_dotenv
load_dotenv(override=True)

UPLOAD_FOLDER = 'static/uploads'
SUPPORTED_EXTENSIONS = ['png', 'jpg', 'jpeg']
# Image.LOAD_TRUNCATED_IMAGES = True


# text_to_img_bytes("An apple on a bicycle")

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.getenv('app_secret_key')

requests = Connect()

def allowed_file(filename):
    if filename.split('.')[1] in SUPPORTED_EXTENSIONS:
        print(filename.split('.')[1])
        return True
    return False



def make_sketch(img, thickness):
    grey_scale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # grey_scale = img
    # inverted_img = cv2.bitwise_not(grey_scale)
    inverted_img = 255-grey_scale
    blurred_img = cv2.GaussianBlur(inverted_img, thickness, sigmaX=0, sigmaY=0)
    sketched_img = cv2.divide(grey_scale, 255-blurred_img, scale=256)
    final_result = cv2.cvtColor(sketched_img, cv2.COLOR_BGR2RGB)
    return final_result


def sketch_process_complete(filename, thickness_value = (11, 11)):
    img = cv2.imread(f'{UPLOAD_FOLDER}/{filename}')
    sketch_img = make_sketch(img, thickness_value)
    sketch_img_name = filename.split('.')[0] + "-TSketch.jpg"
    cv2.imwrite(UPLOAD_FOLDER + '/' + sketch_img_name, sketch_img)

    # Check if image is blurry
    grey_scale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    fm = cv2.Laplacian(grey_scale, cv2.CV_64F).var()
    is_blurry = False
    if fm > 230:
        is_blurry = True
        print('Image is blurry')

    return render_template('sketch.html', org_img_name=filename, sketch_img_name=sketch_img_name, blurry=is_blurry)

def text_to_img_bytes(text):
    import base64
    response = r.post('https://clipdrop-api.co/text-to-image/v1',
    files = {
        'prompt': (None, text, 'text/plain')
    },
    headers = { 'x-api-key': os.getenv('text_image_key')}
    )
    if (response.ok):
    # r.content contains the bytes of the returned image#
        print(response.content)
        filename = f"Text-to-image bytes{random.randint(0,3000)}.png"
        # image_data = base64.b64decode(response.content)
        image = Image.open(io.BytesIO(response.content))
        image.save(f'{UPLOAD_FOLDER}/{filename}')
        return sketch_process_complete(filename)
    else:
        response.raise_for_status()

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/sketch', methods=['POST'])
def sketch():
    if request.args.get('type') == 'edit':
        filename = request.args.get('image')
        thickness_value = request.form['thickness']
        thickness = (int(thickness_value), int(thickness_value))
        return sketch_process_complete(filename, thickness)

    if request.args.get('type') == 'file' or request.args.get('type') == 'text_img':
        if request.args.get('type') == 'text_img':
            return text_to_img_bytes(text=request.form.get('described_img'))

        file = request.files['file']
        filename = secure_filename(file.filename)

        if file and allowed_file(filename):
            file.save(f'{UPLOAD_FOLDER}/{filename}')
            return sketch_process_complete(filename)

   
        else:
            flash(f'Try uploading images with these extension {SUPPORTED_EXTENSIONS}')
            return render_template('sketch.html')

    elif request.args.get('type') == 'url':
        
        if 'http://' not in request.form['link'] and 'https://' not in request.form['link']:
            flash(f"Insert a recognised Url rather than '{request.form['link']}' ")
            return render_template('sketch.html')

        img_url = request.form['link']
            
        # Handling the requesting image url errors
        try:
            res = r.get(img_url, stream=True)
        except:
            flash(f'Failed to establish a new connection')
            return render_template('sketch.html')
        else:
            pass

        filename = 'uploaded-image.jpg'
        if res.status_code == 200:
            if img_url and allowed_file(filename):
                try:
                    img = Image.open(res.raw)
                    img.save(f'{UPLOAD_FOLDER}/{filename}')

                except:
                    flash('An error occurred setting up the image. Make sure you have the correct image url that is not a JPEG extension')
                    return render_template('sketch.html')

                else:
                    return sketch_process_complete(filename)

        elif res.status_code == 404:
            flash('Image url not found on the internet')
            return render_template('sketch.html')

        else:
            flash(f'A {res.status_code} error occurred while getting the url, try using a different img url.')
            return render_template('sketch.html', status_code=res.status_code)


@app.route('/share', methods=['POST'])
def share():
    image_name = request.args.get('file')

    if request.args.get('download'):
        # image = cv2.imread(f"{UPLOAD_FOLDER}/{image_name}")
        # cv2.imwrite(f"{DOWNLOAD_PATH}/{image_name}", image)
        success_msg = 'Sketched picture have been downloaded'
        return render_template('response.html', msg=success_msg)

    if request.args.get('email'):
        sending_email = requests.send_email_pic(r_email=request.form['email'], img_loc=f"{UPLOAD_FOLDER}/{image_name}", img_name=image_name)
        if sending_email is False:
            err_msg = 'An error occurred while trying to send the email. Check internet connection and try again or you can also try re-uploading the image'
            return render_template('response.html', msg=err_msg, status=False)

        success_msg = f"Email has been sent to {request.form['email']}"
        return render_template('response.html', msg=success_msg, status=True)


if __name__ == '__main__':
    app.run(debug=True)
    