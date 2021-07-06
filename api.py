from flask import Flask, request, jsonify

import pytesseract
import cv2 as cv
import pandas as pd
import numpy as np
import io
import time
from collections import OrderedDict

import docx
from pdf2image import convert_from_bytes
from PIL import Image

import tensorflow as tf
from tensorflow import keras
from keras.models import load_model

import river

app = Flask(__name__)

poppler_path = r"C:\Users\fora2\Documents\poppler-21.03.0\Library\bin" #for windows

model = load_model('base.hdf5')
doc_type = ['civ', 'coo', 'hbl', 'mbl', 'other', 'pkd', 'pkl']

# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx', 'xls'])
THRESHOLD = 90

def allowed_file(filename):
    return '.' in filename and file_ext(filename) in ALLOWED_EXTENSIONS

def file_ext(filename):
	return filename.rsplit('.', 1)[1].lower()

"""
def ResizeWithAspectRatio(image, width=None, height=None, inter=cv.INTER_AREA):
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv.resize(image, dim, interpolation=inter)
"""

def img_to_string(image):
	"""Takes an image then parses text into a string"""
	#print("time before image to string : ", time.ctime())
	image_string = pytesseract.image_to_string(image, lang='eng', config='--psm 1 --oem 3')
	#print("time of image to string: ", time.ctime())
	return image_string

def grayscale(image):
	return cv.cvtColor(image, cv.COLOR_BGR2GRAY)

def img_preprocess(image):
	image = cv.resize(image, (256,256))
	cv.imwrite('convert.jpg', image)
	im=cv.imread('convert.jpg')

	im = im/255
	im = np.expand_dims(im, axis=0)
	return im

def model_classify(image):
	print("time before prediction: ", time.ctime())
	gray = grayscale(image)
	image = img_preprocess(gray)
	holistic_pred=model.predict(image)
	#print("time after prediction: ", time.ctime())

	sort_index=np.argsort(holistic_pred)[::-1]
	df=pd.DataFrame({'Document_Type':doc_type,
                         'Percentage':holistic_pred[0]})
	df=df.sort_values('Percentage',ascending=False)
	labels=df['Document_Type']
	classification = df.iloc[0]['Document_Type'], df.iloc[0]['Percentage'] *100
	df['Percentage'] = df['Percentage']*100
	rank = df.iloc[0:5].reset_index(drop=True).set_index('Document_Type')['Percentage'].to_dict()

	if classification[1] < THRESHOLD and classification[0] != "other":
		image_string = img_to_string(gray)
		key_classification = key_classify(image_string)
		return key_classification, classification[1], rank
	else:
		return classification, rank
	#return image

def key_classify(string):
	string = string.lower()
	if "packing declaration" in string:
		print("pkd check done")
		return "pkd"
	elif "packing list" in string:
		print("pkl check done")
		return "pkl"
	elif "bill of lading" in string:
		print("hbl check done")
		return "hbl"
	elif "invoice" in string:
		print("civ check done: ")
		return "civ"
	else:
		return "other" 

def parse_classify(file):
	"""
	Receives file 
	Note that this only reads the first sheet or page of the document,
	since that's where the header/title is usually located. 

	Returns classification of document based on keyword
	"""

	ext = file_ext(file.filename)
	string = ""
	accuracy = 0
	rank = {}

	if ext == "pdf":
		images = convert_from_bytes(file.read())
		classification, accuracy, rank = model_classify(np.asarray(images[0]))


	elif ext in ["jpg", "jpeg", "png"]:
		pil_image = Image.open(file)
		opencvImage = cv.cvtColor(np.array(pil_image), cv.COLOR_RGB2BGR)
		classification, accuracy, rank = model_classify(opencvImage)		

	elif ext == "docx":
		doc = docx.Document(file)
		fullText = []
		for para in doc.paragraphs:
			fullText.append(para.text)
			string = '\n'.join(fullText)
		classification = key_classify(string)

	elif ext in ["xls", "xlsx"]:
		sheet = pd.read_excel(file, sheet_name=[0])
		string = str(sheet)
		classification = key_classify(string)

	return classification, accuracy, rank

@app.route('/classify' , methods=['POST'])
def classify():
	"""
	Receives POST request containing files

	Returns JSON of files and their classification
	"""

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

@app.route('/learn' , methods=['POST'])
def learn():
	"""
	Receives JSON with the file and classification
	"""
	payload = request.json
	#ext = file_ext(file.filename)
	#model.learn_one(payload['file'], payload['type'])

	params = request.json
	if (params == None):
		params = request.args

	if (params != None):
		doc_type = request.form['type']
		files = request.files.getlist('file')
		for file in files:
			#print(file)
			if file and allowed_file(file.filename):
				images = convert_from_bytes(file.read())
				gray = grayscale(np.asarray(images[0]))
				image = img_preprocess(gray)
				#model.learn_one(image, doc_type)

	return "Success!"

@app.route('/newtype' , methods=['POST'])
def new_type():
	params = request.json
	if (params == None):
		params = request.args

	if (params != None):
		doc_type = request.form['type']
		files = request.files.getlist('file')
	return "Success!"

@app.route('/check' , methods=['POST'])
def check():
	params = request.args
	
	print(params)

	return {"Success"}
	

if __name__ == '__main__':
    app.run(debug=True) #debug=True