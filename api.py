from flask import Flask, request, jsonify

import pytesseract
import cv2 as cv
import pandas as pd

import docx
from pdf2image import convert_from_bytes
from PIL import Image

app = Flask(__name__)

# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx', 'xls'])

def allowed_file(filename):
    return '.' in filename and file_ext(filename) in ALLOWED_EXTENSIONS

def file_ext(filename):
	return filename.rsplit('.', 1)[1].lower()

def img_to_string(image):
	"""Takes an image, pre-processes it, then parses text into a string"""
	
	#image = cv.cvtColor(cv.imread(image), cv.COLOR_BGR2GRAY)
	string = pytesseract.image_to_string(image, lang='eng', config='--psm 1 --oem 3')
	return string

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
		string = img_to_string(images[0])

	elif ext in ["jpg", "jpeg", "png"]:
		string = img_to_string(Image.open(file))

	elif ext == "docx":
		doc = docx.Document(file)
		fullText = []
		for para in doc.paragraphs:
			fullText.append(para.text)
			string = '\n'.join(fullText)

	elif ext in ["xls", "xlsx"]:
		sheet = pd.read_excel(file, sheet_name=[0])
		string = str(sheet)

	classification = key_classify(string)		

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
		instance = {}
		for file in files:
			if file and allowed_file(file.filename):
				file_type = parse_classify(file)
				data["files"].append({'file': file.filename, 'type': file_type})

	return jsonify(data)
	

if __name__ == '__main__':
    app.run(debug=True)