from flask import Flask, request, jsonify

import pytesseract
import cv2 as cv
import pandas as pd
import numpy as np
import io

import docx
from pdf2image import convert_from_bytes
from PIL import Image

import tensorflow as tf
from tensorflow import keras
from keras.models import load_model

app = Flask(__name__)

poppler_path = r"C:\Users\fora2\Documents\poppler-21.03.0\Library\bin" #for windows

model = load_model('base.hdf5')
doc_type = ['civ', 'coo', 'hbl', 'mbl', 'other', 'pkd', 'pkl']

# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx', 'xls'])
THRESHOLD = 70

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
	"""Takes an image, pre-processes it, then parses text into a string"""
	#image = cv.cvtColor(np.asarray(image), cv.COLOR_BGR2GRAY)
	image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
	"""resize = ResizeWithAspectRatio(image, width=980)
	cv.imshow("grayscale", resize)
	cv.waitKey(0)
	cv.destroyAllWindows() """  
	string = pytesseract.image_to_string(image, lang='eng', config='--psm 1 --oem 3')
	return string

def img_preprocess(image):
	gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY) # for some reason the dims differ
	image = cv.resize(gray, (256,256))

	cv.imwrite('convert.jpg', image)
	im=cv.imread('convert.jpg')

	im = im/255
	im = np.expand_dims(im, axis=0)

	return im

def model_classify(image):
	image = img_preprocess(image)
	holistic_pred=model.predict(image)

	sort_index=np.argsort(holistic_pred)[::-1]
	df=pd.DataFrame({'Document_Type':doc_type,
                         'Percentage':holistic_pred[0]})
	df=df.sort_values('Percentage',ascending=False)
	labels=df['Document_Type']
	classification = df.iloc[0]['Document_Type'], df.iloc[0]['Percentage']*100
	print(classification[1])
	print(classification[0])

	if classification[1] < THRESHOLD and classification[0] != "other":
		classification = key_classify(img_to_string(image))
		return classification
	else:
		return classification[0]
	#return image

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

	if ext == "pdf":
		images = convert_from_bytes(file.read())
		classification = model_classify(np.asarray(images[0]))


	elif ext in ["jpg", "jpeg", "png"]:
		pil_image = Image.open(file)
		opencvImage = cv.cvtColor(np.array(pil_image), cv.COLOR_RGB2BGR)
		classification = model_classify(opencvImage)		

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

	#classification = key_classify(string)	

		#maybe you can make a clear way by checking list of keywords to key in dict
	return classification

@app.route('/classify' , methods=['POST'])
def classify():
	"""
	Receives POST request containing files
	Files are of the format:
		mult_files = [
		('file',('civ_1.pdf', open('data/civ/civ_1.pdf', 'rb'), 'file/pdf')),
		('file',('civ_2.pdf', open('data/civ/civ_2.pdf', 'rb'), 'file/pdf'))]

		r = requests.post(url, data=payload, files=mult_files)

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
		#print(files)
		instance = {}
		for file in files:
			#print(file.filename)
			if file and allowed_file(file.filename):
				file_type = parse_classify(file)
				data["files"].append({'file name': file.filename, 'file size in bytes': file.seek(0,2) ,'type': file_type})

	return jsonify(data)

@app.route('/check' , methods=['POST'])
def check():
	params = request.args
	
	print(params)

	return {"Success"}
	

if __name__ == '__main__':
    app.run(debug=True) #debug=True