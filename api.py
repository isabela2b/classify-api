from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
import json


app = Flask(__name__)
api = Api(app)

# Allowed extension you can set your own
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx'])

parser = reqparse.RequestParser()
parser.add_argument('client')


class Classify(Resource):
    def post(self):
    	args = parser.parse_args()
    	classification = "civ"
    	client_name = request.form['client']
    	file_name = 'rando.pdf'
    	return {'client': client_name, 
    	file_name:classification}

api.add_resource(Classify, '/')

if __name__ == '__main__':
    app.run(debug=True)