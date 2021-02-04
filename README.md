# Document Classification API

This is a Flask API that classifies files into various document types. 

# Features

  - Receives POST request and returns a JSON file containing the client name, file name, file size (in bytes), and document classification
  - Can classify documents into the following priority formats: CIV, HBL, PKL, PKD. It returns "other" when it does not fall into any of the mentioned formats
  - Accepts the following file formats: pdf, png, jpg, jpeg, docx, xls, xlsx
  - Uses AI to parse text in images 
  
# How it Classifies
- After receiving the POST request, it checks if the given files belong to the accepted file formats (pdf, jpg, etc.)
- If pdf, converts it to image. 
- Images are pre-processed (converted to grayscale, will add thresholding if it produces better results but so far it hasn't)
- Files are parsed into text using the relevant library. Note that it only reads the first page, since it's usually all you need to identify the format. In most cases the first page contains the format name in large letters, and the following pages contain either legalese or more tables.  
- Look for format keyword (e.g. "invoice" for CIV) in the text, then classify

### Classification Accuracy
Accuracy hasn't really been tested yet because we're still waiting for more client files. It can correctly classify most of the files in the test folder. The exception is hbl_1.pdf, since it doesn't contain the keyword "bill of lading." It's recommended that we roll out the classification feature to a select few clients first until the AI model gets completed.  

### Project Structure
- api.py - API file to be integrated with the hub
- test folder - for testing the API
    - post-req.py - to check api.py responses
    - data folder - contains sample files to send to api.py when testing

### Dependencies

* python 3.8.3
* flask 1.1.2 - python web app framework used for the API
* werkzeug 1.0.1
* [pytesseract] 0.3.7 - optical character recognition (OCR) tool for parsing text to images
* [cv2] 4.5.1 - computer vision library used in this project for image pre-processing 
* pandas 1.0.5
* numpy 1.18.5
* docx 0.8.10
* pdf2image 1.14.0
* PIL 8.1.0

### Installation

Install the dependencies and start the server.

```sh
$ cd classify-api
$ python3 api.py
```


### Todos

 - Train AI classification model once we get more files
 - Check if the auto-crop feature will still be needed of if it's just an edge case (see test/data/pkd_2.jpg). If yes, include auto-crop + re-orientation in pre-processing method. 



[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)


   [pytesseract]: <https://github.com/madmaze/pytesseract>
   [cv2]: <https://github.com/opencv/opencv>

