from flask import Flask, request, jsonify

import pytesseract
import cv2 as cv
import pandas as pd
import numpy as np
import io
import csv

import docx
from pdf2image import convert_from_bytes
from PIL import Image
from sklearn import preprocessing

import tensorflow as tf
from tensorflow import keras
from keras.models import load_model

import traceback
import logging
#from logging.handlers import RotatingFileHandler
#from logging.config import dictConfig

app = Flask(__name__)

#logging.basicConfig(filename='demo.log', level=logging.DEBUG)
#handler = RotatingFileHandler(os.path.join(app.root_path, 'logs', 'error_log.log'), maxBytes=102400, backupCount=10)

model = load_model('models/classify_256.h5')
doc_type = []

# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx', 'xls'])
THRESHOLD = 80

with open('doc_type.csv', newline='') as inputfile:
    for row in csv.reader(inputfile):
        doc_type.append(row[0])

doc_type.sort()


def allowed_file(filename):
    return '.' in filename and file_ext(filename) in ALLOWED_EXTENSIONS

def file_ext(filename):
	return filename.rsplit('.', 1)[1].lower()

def img_to_string(image):
	"""Takes an image then parses text into a string"""
	image_string = pytesseract.image_to_string(image, lang='eng', config='--psm 1 --oem 3')
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
	gray = grayscale(image)
	image = img_preprocess(gray)
	holistic_pred=model.predict(image)

	sort_index=np.argsort(holistic_pred)[::-1]
	df=pd.DataFrame({'Document_Type':doc_type,
                         'Percentage':holistic_pred[0]})
	df=df.sort_values('Percentage',ascending=False)
	labels=df['Document_Type']
	classification = df.iloc[0]['Document_Type']
	percentage =  df.iloc[0]['Percentage']*100
	df['Percentage'] = df['Percentage']*100
	rank = df.iloc[0:5].reset_index(drop=True).set_index('Document_Type')['Percentage'].to_dict()

	if percentage < THRESHOLD: # and percentage != "other":
		try:
			image_string = img_to_string(gray)
			key_classification = key_classify(image_string)
		except Exception as e:
			f = open("log.txt", "a")
			f.write(str(e))
			f.write(traceback.format_exc())
			f.close()
		return key_classification, percentage, rank
	else:
		return classification, percentage, rank

def key_classify(string):
	string = string.lower()
	if "packing declaration" in string:
		return "pkd"
	elif "packing list" in string:
		return "pkl"
	elif "bill of lading" in string:
		return "hbl"
	elif "invoice" in string:
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

def update_model(X,y):
	try:
		gray = grayscale(X)
		X = img_preprocess(gray)
		le = preprocessing.LabelBinarizer()
		le.fit(doc_type)
		y = le.transform([y])
		model.fit(X,y)
		model.save('models/classify_256.h5', overwrite=True)
		return "Success!"
	except Exception as e:
		#f = open("log.txt", "a")
		#f.write(str(e))
		#f.write(traceback.format_exc())
		#f.close()
		return e
	#return "Success!"

@app.route('/check' , methods=['POST'])
def check():
	params = request.args
	
	print(params)

	return "Success"
	
@app.route('/' , methods=['GET'])
def home():
	return "Success"

if __name__ == '__main__':
    app.run() #debug=True
