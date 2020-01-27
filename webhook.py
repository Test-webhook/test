from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from utils import store_data_in_dictionary

app = Flask(__name__)
api = Api(app)
pr_dict = {}


# making a class for a particular resource
# the get, post methods correspond to get and post requests
class PullRequest(Resource):

    # corresponds to the GET request.
    def get(self):
        response = jsonify({'message': 'hello world'})
        response.status_code = 200
        return response

    # Corresponds to POST request
    def post(self):
        global pr_dict
        event_data = request.get_json()  # status code
        print("data: ", event_data)

        pr_dict = store_data_in_dictionary(event_data, pr_dict)
        print("pr_dict:", pr_dict)
        response = jsonify({'message': 'Data Received'})
        response.status_code = 200
        return response


# adding the defined resources along with their corresponding urls
api.add_resource(PullRequest, '/payload')

# driver function
if __name__ == '__main__':
    app.run(debug=True)
