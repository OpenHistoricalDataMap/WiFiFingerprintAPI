import os
import statistics
import re
from flask import Flask, request, jsonify, render_template, Response
from flask_pymongo import PyMongo
from jsonschema import validate
from numpy import std

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
        return jsonify(data=data), 200
    else:
        return jsonify(message="No fingerprint were found with this ID."), 404


@application.route('/fingerprint', methods=["POST"])
def post_fingerprint():
    """
    stores the specified fingerprint
    """

    try:
        fp = request.get_json()
        if db.fingerprint.find_one({'id': fp['id']}):
            return jsonify(message='A Fingerprint with this ID does already exist'), 400
        else:
            validate(instance=fp, schema=FINGERPRINT_SCHEMA)
            db.fingerprint.insert_one(fp)
            return jsonify(message='Fingerprint saved successfully!'), 201
    except Exception as e:
        return jsonify(message='Fingerprint could not be saved', error=str(e)), 400


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
            return jsonify(message='Fingerprint updated successfully!'), 201
        except Exception as e:
            return jsonify(message='Fingerprint could not be updated', error=str(e)), 400
    else:
        return jsonify(message="No fingerprint were found with this ID."), 404


@application.route('/fingerprint/<string:fingerprint_id>', methods=["DELETE"])
def delete_fingerprint(fingerprint_id):
    """
    deletes a fingerprint
    """

    fp = db.fingerprint.find_one({'id': fingerprint_id})

    if fp:
        db.fingerprint.delete_one({'id': fingerprint_id})
        return jsonify(message='Fingerprint deletes successfully!'), 201
    else:
        return jsonify(message="No fingerprint were found with this ID."), 404


@application.route('/localize', methods=["GET"])
def get_localize():
    """
    returns the most matching fingerprint to a given set of mac and its strengths values
    """

    best_match = None

    # build a dict of macs and its strengths that are passed in the request arguments
    try:
        url_params = args_to_dict(request.args.to_dict())
    except ValueError as e:
        return jsonify(message='Invalid request parameter.', error=str(e)), 400

    for fp in db.fingerprint.find():
        # Remove macs from fingerprint which has less then 1/3 occurrences in all timestamps
        fingerprint_macs = {mac: count for mac, count in get_macs(fp).items()
                            if count >= int(1/3 * len(fp['fingerprint']))
                            }

        # If the match probability of this fingerprint is better, then assign this was one as the result
        if not best_match:
            application.logger.info("Current Best match: %s" % str(best_match))
            best_match = calculate_match_probability(url_params, fingerprint_macs, fp)
        else:
            application.logger.info("Current Best match: %s" % str(best_match))
            if calculate_match_probability(url_params, fingerprint_macs, fp)[1] > best_match[1]:
                best_match = calculate_match_probability(url_params, fingerprint_macs, fp)

    # Return the best matched fingerprint
    result_fp = db.fingerprint.find_one({'id': best_match[0]})

    if result_fp:
        return jsonify(message="Found a matching fingerprint!", fingeprint_id=result_fp['id'],
                       ratio=str(best_match[1]) + "%", fingeprint_description=result_fp['description'],
                       fingerprint_coordinates=result_fp['coordinates'],
                       fingeprint_additionalInfo=result_fp['additionalInfo']), 200
    else:
        return jsonify(message="No Fingerprint were found, which matches the given macs and its strength."), 404


def calculate_match_probability(url_params, fingerprint_macs, fingerprint):
    """
    Iterates through the url params and does the following:
    If the strength of a url_param mac is in between the range of the average strength of a fingerprint and its standard
    deviation then go to the next one. If every url_param were successfully found in the fingerprint, we then return
    the difference between the fingerprint average strength and the url strength average.
    """

    application.logger.info("Compare url %s & fingerprint: Id: %s" % (str(url_params), fingerprint['id']))
    application.logger.info(url_params)

    i = 0
    average = 0

    for url_mac, url_strength in url_params.items():
        # If the url mac is in the current fingerprint
        if url_mac in fingerprint_macs:
            application.logger.info("Current url mac: %s" % url_mac)
            fp_average_strength = get_average_strength(fingerprint, url_mac.lower())

            application.logger.info("Fingerprints mac average strength: %d" % fp_average_strength)
            average += ratio_in_percent(abs(fp_average_strength), abs(float(url_strength)))

            i += 1
            if i == len(url_params):
                try:
                    application.logger.info("Relation: " + str(average / len(url_params)))
                    return fingerprint['id'], average / len(url_params)
                except ZeroDivisionError:
                    application.logger.info("Relation: 0 %")
                    return fingerprint['id'], 0


def ratio_in_percent(a, b):
    """
    returns the ratio between to numbers in percent
    """

    result = float(((b - a) * 100) / a)
    return 100 - abs(result)


def args_to_dict(args):
    """
    Parses the url params to the following dict:
    values = {
        MAC_1: STRENGTH_1,
        MAC_2: STRENGTH_2,
        ...
    }
    Throws an ValueError if the dict is empty after parsing.
    """

    values = {}
    min_rssi = -26
    max_rssi = -100

    for k, v in args.items():
        if re.match(r'mac[0-9]+', k) and re.match(r'(?:[0-9a-fA-F]:?){12}', v):
            try:
                strength = args['strength' + str(k[-1:])]
                if abs(min_rssi) <= abs(int(strength)) <= abs(max_rssi) and int(strength) < 0:
                    values[v] = strength
                else:
                    raise ValueError(
                        "Strength value for mac: %s (param: %s) missing. Strength Range: -26 - -100." % (v, k))
            except KeyError:
                raise ValueError(
                    'Invalid request params found (%s : %s). Use: \"/localize?mac1=A:B:C:D:E:F&strength1=[-26 .. -100]\"' %
                    (v, k)
                )

    if len(values) == 0:
        raise ValueError('No valid request params found. Use: \"/localize?mac1=A:B:C:D:E:F&strength1=[-26 .. -100]\"')
    else:
        return values


def get_macs(data):
    """
    returns a dict of all macs and its occurrences of a given fingerprint
    """

    macs = []
    values = {}

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


if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
