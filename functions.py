import pytesseract
import cv2 as cv
import pandas as pd
import numpy as np
import io, csv, time, os, traceback

import docx
from pdf2image import convert_from_bytes
from PIL import Image
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger
from sklearn import preprocessing

import tensorflow as tf
from tensorflow import keras
from keras.models import load_model

model = load_model('models/classify_512.h5')
data_folder = "merge/"
doc_type = []

# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'docx', 'xlsx', 'xls'])
THRESHOLD = 90

with open('doc_type.csv', newline='') as inputfile:
    for row in csv.reader(inputfile):
        doc_type.append(row[0])

doc_type.sort()

def allowed_file(filename):
    return '.' in filename and file_ext(filename) in ALLOWED_EXTENSIONS

def file_ext(filename):
	return filename.rsplit('.', 1)[1].lower()

def file_name(filename):
    return filename.rsplit('.', 1)[0]

def img_to_string(image):
	"""Takes an image then parses text into a string"""
	image_string = pytesseract.image_to_string(image, lang='eng', config='--psm 1 --oem 3')
	return image_string

def grayscale(image):
	return cv.cvtColor(image, cv.COLOR_BGR2GRAY)

def img_preprocess(image):
	image = cv.resize(image, (512,512))
	cv.imwrite('convert.jpg', image)
	im=cv.imread('convert.jpg')
	im = im/255
	im = np.expand_dims(im, axis=0)
	return im

def model_classify(image):
	gray = grayscale(np.asarray(image))
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

	if percentage < THRESHOLD and percentage != "other":
		key_classification = "other"		
		#image_string = img_to_string(gray)
		#key_classification = key_classify(image_string)
		return {'classification':key_classification, 'accuracy': percentage, 'rank': rank} 
	else:
		return {'classification':classification, 'accuracy': percentage, 'rank': rank}

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

def multipage_combine(predictions, file):
	shared_type = {key:value['classification'] for key, value in predictions.items()}
	res = {}
	for i, v in shared_type.items():
		res[v] = [i] if v not in res.keys() else res[v] + [i]
	print(res)
	merged_predictions = {}
	inputpdf = PdfFileReader(file)
	if inputpdf.isEncrypted:
		try:
			inputpdf.decrypt('')
			print('File Decrypted (PyPDF2)')
		except:
			print("Decryption error")

	for classification, pages in res.items():
		average_accuracy = 0
		output = PdfFileWriter()
		for page in pages:
			output.addPage(inputpdf.getPage(page-1))
			average_accuracy += predictions[page]["accuracy"] 
		split_file_name = file_name(file.filename)+"_"+classification+".pdf"
		with open(data_folder+split_file_name, "wb") as outputStream:
			output.write(outputStream)
		average_accuracy = average_accuracy/len(pages)
		merged_predictions[split_file_name] = {'classification':classification, 'pages':pages, 'accuracy':average_accuracy, 'path':'https://cargomation.com/merged_classify/'+split_file_name}

	return merged_predictions

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
		images = convert_from_bytes(file.read()) #, grayscale=True
		prediction = {}
		for idx, image in enumerate(images):
			prediction[idx+1]  = model_classify(image) # prediction should return page indexes to be merged and separated and classification
		predictions = multipage_combine(prediction, file)
	elif ext in ["jpg", "jpeg", "png"]:
		pil_image = Image.open(file)
		opencvImage = cv.cvtColor(np.array(pil_image), cv.COLOR_RGB2BGR)
		predictions = model_classify(opencvImage)
	elif ext == "docx":
		doc = docx.Document(file)
		fullText = []
		for para in doc.paragraphs:
			fullText.append(para.text)
			string = '\n'.join(fullText)
		classification = key_classify(string)
		predictions = {'classification': classification}

	elif ext in ["xls", "xlsx"]:
		sheet = pd.read_excel(file, sheet_name=[0])
		string = str(sheet)
		classification = key_classify(string)
		predictions = {'classification'}

	return ext, predictions

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