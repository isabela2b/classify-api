from flask import Flask, request, jsonify
from functions import parse_classify, update_model, model_classify, allowed_file

import numpy as np
import cv2 as cv
from PIL import Image
import traceback
import logging
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig

app = Flask(__name__)

#logging.basicConfig(filename='demo.log', level=logging.DEBUG)
#handler = RotatingFileHandler(os.path.join(app.root_path, 'logs', 'error_log.log'), maxBytes=102400, backupCount=10)

poppler_path = r"C:\Program Files\poppler-21.03.0\Library\bin"

@app.route('/classify' , methods=['POST'])
def classify():
	"""
	Receives POST request containing files
	Returns JSON of files and their classification
	"""
	try:
		data = {'client': 'None','files': []}

		#get the request parameters
		params = request.json
		if (params == None):
			params = request.args

		# if parameters are found, return a prediction
		if (params != None):
			client_name = request.form['client']
			data['client'] = client_name

			files = request.files.getlist('file')
			instance = {}
			for file in files:
				if file and allowed_file(file.filename):
					file_type, accuracy, rank = parse_classify(file)
					data["files"].append({'file name': file.filename, 'file size in bytes': file.seek(0,2) ,'type': file_type, 'accuracy':accuracy, 'rank': rank})

		return jsonify(data)
	except Exception as ex:
		return str(ex)

@app.route('/learn' , methods=['POST'])
def learn():
	"""
	Receives JSON with the file and classification
	"""
	data = {'files': []}

	params = request.json
	if (params == None):
		params = request.args

	if (params != None):
		target = request.form['type']
		files = request.files.getlist('file')
		for file in files:
			if file and allowed_file(file.filename):
				file_type, prediction = parse_classify(file)
				data["files"].append({'file name': file.filename, 'file size in bytes': file.seek(0,2), 'file type': file_type, 'prediction': prediction})		
	return jsonify(data)

@app.route('/learn' , methods=['POST'])
def learn():
	"""
	Receives JSON with the file and classification
	"""

	data = {'files': []}

	params = request.json
	if (params == None):
		params = request.args

	if (params != None):
		target = request.form['type']
		files = request.files.getlist('file')
		for file in files:
			ext = file_ext(file.filename)
			if file and ext in ['pdf','jpg','jpeg','png'] and target in doc_type:

				if ext == 'pdf':
					images = convert_from_bytes(file.read())
					try:
						update_model(np.asarray(images[0]),target)
						file_type, accuracy, rank = model_classify(np.asarray(images[0]))
					except Exception as e:
						f = open("log.txt", "a")
						f.write(str(e))
						f.write(traceback.format_exc())
						f.close()					

				else:
					image = Image.open(file)
					opencvImage = cv.cvtColor(np.array(image), cv.COLOR_RGB2BGR)
					update_model(opencvImage, target)
					file_type, accuracy, rank = model_classify(opencvImage)				

				data["files"].append({'file name': file.filename, 'file size in bytes': file.seek(0,2) ,'type': file_type, 'accuracy':accuracy, 'rank': rank})
				return jsonify(data)

			else:
				return "File format not supported."


@app.route('/check' , methods=['POST'])
def check():
	params = request.args
	
	print(params)

	return "Success"
	
@app.route('/' , methods=['GET'])
def home():
	try:
		return "Success"
	except Exception as ex:
		return str(ex)

if __name__ == '__main__':
    app.run() #debug=True
