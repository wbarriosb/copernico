import os
import json
import urllib.request
from flask import Flask, request, redirect, jsonify
from werkzeug.utils import secure_filename
import executorOCR as exocr

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
# UPLOAD_FOLDER = 'D:/$trabajo/uploads'
UPLOAD_FOLDER = 'PDFs'

app = Flask(__name__)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/file-upload', methods=['POST'])
def upload_file():
	# check if the post request has the file part
	if 'file' not in request.files:
		resp = jsonify({'message' : 'No file part in the request'})
		resp.status_code = 400
		return resp
	file = request.files['file']
	if file.filename == '':
		resp = jsonify({'message' : 'No file selected for uploading'})
		resp.status_code = 400
		return resp
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		resp = jsonify({'message' : 'File successfully uploaded'})
		resp.status_code = 201
		return resp
	else:
		resp = jsonify({'message' : 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
		resp.status_code = 400
		return resp
#
@app.route('/ocr/<string:tipo>/<string:input_file>', methods=['GET'])
def execute_ocr(tipo, input_file):
    exocr.main(tipo, input_file)
	# Reading results in JSON file 
    json_file= open('results.json', 'r')
    json_data = json.load(json_file)
    json_file.close()
    return json_data

if __name__ == "__main__":
    app.run(debug= True, port= 5001)