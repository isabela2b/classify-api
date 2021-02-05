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
- requirements.txt - file of all the dependencies required to run the application
- test folder - for testing the API
    - post-req.py - to check api.py responses
    - data folder - contains sample files to send to api.py when testing

### Dependencies

You can also check for the dependencies by running `pip list` in the terminal. 

| Package      | Version | Description |
|---------------| --------| ------|
|python       |    3.8.3 | 
|click       |    7.1.2 |  
| docx        |    0.2.4 |  |
| Flask        |   1.1.2 | python web app framework used for the API |
| itsdangerous  |  1.1.0 |  |
| Jinja2       |   2.11.3 |  |
| lxml         |   4.6.2 |  |
| MarkupSafe   |   1.1.1 |  |
| numpy        |   1.20.0 |  |
| [opencv-python] |  4.5.1.48 | computer vision library used in this project for image pre-processing  |
| pandas      |    1.2.1 |  |
| pdf2image   |    1.14.0 |  |
| Pillow      |    8.1.0 |  |
| pip        |     21.0.1 |  |
| [pytesseract]  |   0.3.7 | optical character recognition (OCR) tool for parsing text to images  |
| python-dateutil| 2.8.1 |  |
| python-docx  |   0.8.10 |  |
| pytz        |    2021.1 |  |
| setuptools  |    41.2.0 |  |
| six          |   1.15.0 |  |
| [waitress]     |  1.4.4 | production-quality pure-Python WSGI server that can run on UNIX and Windows |
| Werkzeug     |   1.0.1 |  |


## Run

Run venv, install the dependencies, then start the server.

### Development:

```sh
$ cd classify-api
$ python -m venv venv #create venv
$ . venv/bin/activate # activate virtual environment
$ pip install -r requirements.txt #install dependencies
$ export FLASK_APP=api.py
$ export FLASK_ENV=development
$ flask run
```

For Windows cmd, use set instead of export:
```sh
> set FLASK_APP=api.py
> set FLASK_ENV=development
> flask run
```

For Windows PowerShell, use $env: instead of export:
```sh
> $env:FLASK_APP = "api.py"
> $env:FLASK_ENV = "development"
> flask run
```


### Production:
```sh
$ cd classify-api
$ . venv/bin/activate # activate virtual environment
$ pip install -r requirements.txt #install dependencies
$ export FLASK_APP=api.py
$ export FLASK_ENV=production
$ waitress-serve [OPTIONS] "api:app"
```
Options for waitress-serve:
- --host=ADDR
    Hostname or IP address on which to listen, default is '0.0.0.0', which means "all IP addresses on this host".
- --port=PORT
    TCP port on which to listen, default is '8080'

More options can be found [here] ('https://docs.pylonsproject.org/projects/waitress/en/stable/runner.html')

### Todos

 - Train AI classification model once we get more files
 - Check if the auto-capirop feature will still be needed of if it's just an edge case (see test/data/pkd_2.jpg). If yes, include auto-crop + re-orientation in pre-processing method. 



[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)


   [pytesseract]: <https://github.com/madmaze/pytesseract>
   [opencv-python]: <https://github.com/opencv/opencv>
   [waitress]: <https://docs.pylonsproject.org/projects/waitress/en/stable/index.html>

