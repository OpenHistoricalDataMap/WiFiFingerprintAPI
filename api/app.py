import os
from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from jsonschema import validate

application = Flask(__name__, template_folder=".")

application.config["MONGO_URI"] = 'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + \
                                  '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_DATABASE']

mongo = PyMongo(application)
db = mongo.db

FINGERPRINT_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "description": {"type": "string"},
        "coordinates": {"type": "string"},
        "additionalInfo": {"type": "string"},
        "fingerprint": {
            "type": "array",
            "minItems": 2,
            "maxItems": 60,
            "items": [
                {
                    "type": "object",
                    "properties": {
                        "timestamp": {"type": "string"},
                        "signalSample": {
                            "type": "array",
                            "items": [
                                {
                                    "type": "object",
                                    "properties": {
                                        "macAddress": {"type": "string"},
                                        "strength": {"type": "integer"}
                                    },
                                    "required": [
                                        "macAddress",
                                        "strength"
                                    ]
                                }
                            ]
                        }
                    }
                }]
        }
    }
}


# /
@application.route('/', methods=["GET"])
def list_fingerprints():

    data = []
    for fp in db.fingerprint.find():
        data.append(fp['todo'])
    return render_template('table.html', fingerprints=data)


# /fingerprint
@application.route('/fingerprint/<string:fingerprint_id>', methods=["GET"])
def get_fingerprint(fingerprint_id):
    """
    returns the fingerprint for a specified ID
    """
    fp = db.fingerprint.find_one({'id': fingerprint_id})

    if fp:
        data = [{
            'id': fp['id'],
            'description': fp['description'],
            'coordinates': fp['coordinates'],
            'additionalInfo': fp['additionalInfo'],
            'fingerprint': fp['fingerprint']
        }]
        return jsonify(status=200, data=data)
    else:
        return jsonify(status=404, message="No fingerprint were found with this ID.")


@application.route('/fingerprint', methods=["POST"])
def post_fingerprint():
    """
    stores the specified fingerprint
    """

    try:
        fp = request.get_json()
        validate(instance=fp, schema=FINGERPRINT_SCHEMA)
        db.fingerprint.insert_one(fp)
        return jsonify(status=201, message='To-do saved successfully!')
    except Exception as e:
        return jsonify(status=400, message='Exception: %s' % e)


if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)