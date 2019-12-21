import os
import statistics
import re
from flask import Flask, request, jsonify, render_template, Response
from flask_pymongo import PyMongo
from jsonschema import validate
from numpy import std

# TODO: use templates for /fingerprint
# TODO: log?!
# TODO: ..

application = Flask(__name__, template_folder=".")

application.config["MONGO_URI"] = 'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + \
                                  '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_DATABASE']

mongo = PyMongo(application)
db = mongo.db

FINGERPRINT_SCHEMA = {
    "definitions": {},
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://example.com/object1577285629.json",
    "title": "Root",
    "type": "object",
    "required": [
        "id",
        "description",
        "coordinates",
        "additionalInfo",
        "fingerprint"
    ],
    "properties": {
        "id": {
            "$id": "#root/id",
            "title": "Id",
            "type": "string",
            "default": "",
            "examples": [
                "xmas"
            ],
            "pattern": "^.*$"
        },
        "description": {
            "$id": "#root/description",
            "title": "Description",
            "type": "string",
            "default": "",
            "examples": [
                "test desc"
            ],
            "pattern": "^.*$"
        },
        "coordinates": {
            "$id": "#root/coordinates",
            "title": "Coordinates",
            "type": "string",
            "default": "",
            "examples": [
                "52.1212,13.213212"
            ],
            "pattern": "^.*$"
        },
        "additionalInfo": {
            "$id": "#root/additionalInfo",
            "title": "Additionalinfo",
            "type": "string",
            "default": "",
            "examples": [
                "updated"
            ],
            "pattern": "^.*$"
        },
        "fingerprint": {
            "$id": "#root/fingerprint",
            "title": "Fingerprint",
            "type": "array",
            "default": [],
            "items": {
                "$id": "#root/fingerprint/items",
                "title": "Items",
                "type": "object",
                "minItems": 2,
                "maxItems": 60,
                "required": [
                    "timestamp",
                    "signalSample"
                ],
                "properties": {
                    "timestamp": {
                        "$id": "#root/fingerprint/items/timestamp",
                        "title": "Timestamp",
                        "type": "string",
                        "default": "",
                        "examples": [
                            "20-12-2019-02.31.29"
                        ],
                        "pattern": "^.*$"
                    },
                    "signalSample": {
                        "$id": "#root/fingerprint/items/signalSample",
                        "title": "Signalsample",
                        "type": "array",
                        "minItems": 1,
                        "default": [],
                        "items": {
                            "$id": "#root/fingerprint/items/signalSample/items",
                            "title": "Items",
                            "type": "object",
                            "required": [
                                "macAddress",
                                "strength"
                            ],
                            "properties": {
                                "macAddress": {
                                    "$id": "#root/fingerprint/items/signalSample/items/macAddress",
                                    "title": "Macaddress",
                                    "type": "string",
                                    "default": "",
                                    "examples": [
                                        "03:00:00:00:01:00"
                                    ],
                                    "pattern": "^.*$"
                                },
                                "strength": {
                                    "$id": "#root/fingerprint/items/signalSample/items/strength",
                                    "title": "Strength",
                                    "type": "integer",
                                    "examples": [
                                        -50
                                    ],
                                    "default": 0
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}


# /
@application.route('/', methods=["GET"])
def list_fingerprints():
    """
    Prints out all fingerprints
    """

    data = []

    for fp in db.fingerprint.find():
        try:
            item = {
                'id': fp['id'],
                'description': fp['description'],
                'coordinates': fp['coordinates'],
                'additionalInfo': fp['additionalInfo'],
                'fingerprint': fp['fingerprint']
            }
            data.append(item)
        except KeyError as e:
            pass
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
        return jsonify(status=201, message='Fingerprint saved successfully!')
    except Exception as e:
        return Response('Exception while storing fingerprint: %s' % e, status=400)


@application.route('/fingerprint/<string:fingerprint_id>', methods=["PUT"])
def put_fingerprint(fingerprint_id):
    """
    updates a fingerprint
    """

    fp = db.fingerprint.find_one({'id': fingerprint_id})

    if fp:
        try:
            request_fp = request.get_json()
            validate(instance=request_fp, schema=FINGERPRINT_SCHEMA)
            db.fingerprint.find_one_and_update({'id': fingerprint_id}, {'$set': request_fp})
            return jsonify(status=200, message='Fingerprint updated successfully!')
        except Exception as e:
            return jsonify(status=400, message='Exception while updating fingerprint: %s' % e)
    else:
        return jsonify(status=404, message="No fingerprint were found with this ID.")


@application.route('/fingerprint/<string:fingerprint_id>', methods=["DELETE"])
def delete_fingerprint(fingerprint_id):
    """
    deletes a fingerprint
    """

    if db.fingerprint.delete_one({'id': fingerprint_id}):
        return jsonify(status=201, message='Fingerprint deletes successfully!')
    else:
        return jsonify(status=404, message="No fingerprint were found with this ID.")


@application.route('/localize', methods=["GET"])
def get_localize():
    """
    returns the estimates position (lat,long) to a given set of mac and its strengths values
    """

    # build a dict of macs and its strengths that are passed in the request arguments
    url_params = args_to_dict(request.args.to_dict())

    for fp in db.fingerprint.find():
        fingerprint_macs = get_macs(fp)

        # Remove macs from fingerprint which has less then 1/3 occurrences
        for mac, count in fingerprint_macs.items():
            if count < int(1/3 * len(fp['fingerprint'])):
                del fingerprint_macs[mac]

        for url_mac in url_params:
            if url_mac in fingerprint_macs:
                url_strength = url_params['mac']
                fp_strength_std_deviation = get_strength_std_deviation(fp, url_mac)
                fp_average_strength = get_average_strength(fp, url_mac)

                if (abs(fp_average_strength) - abs(fp_strength_std_deviation) <= abs(url_strength) <=
                        abs(fp_average_strength) + abs(fp_strength_std_deviation)):
                    its_a_match = True
                    continue
                else:
                    break

        if its_a_match:
            return jsonify(status=200, data=fp['coordinates'])
    return jsonify(status=204, message="No matching fingerprint were found")


def args_to_dict(args):
    """
    returns a dict of mac and corresponding strength from a given dict of url params
    """

    values = {}

    for k, v in args:
        if re.match(r'mac[0-9]', k):
            values[v] = args['strength' + str(k[-1:])]
    return values


def get_macs(data):
    """
    returns a dict of all macs and its occurrences
    """

    macs = []
    values = {}

    application.logger.info(data)
    for p in data['fingerprint']:
        for v in p['signalSample']:
            macs.append(v['macAddress'])

    for mac in list(set(macs)):
        values[mac] = macs.count(mac)

    return values


def get_average_strength(data, mac):
    """
    returns the average of a mac address
    """

    strength = []

    for p in data['fingerprint']:
        for v in p['signalSample']:
            if v['macAddress'] == mac:
                strength.append(int(v['strength']))

    return statistics.mean(strength)


def get_strength_std_deviation(data, mac):
    """
    returns the standard deviation for a specific mac
    """

    strength = []

    for p in data['fingerprint']:
        for v in p['signalSample']:
            if v['macAddress'] == mac:
                strength.append(abs(int(v['strength'])))

    return std(strength, ddof=1)


if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
