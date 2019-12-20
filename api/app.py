import os
from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo

application = Flask(__name__, template_folder=".")

application.config["MONGO_URI"] = 'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + \
                                  '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_DATABASE']

mongo = PyMongo(application)
db = mongo.db


# /
@application.route('/', methods=["GET"])
def list_fingerprints():

    data = []
    for fp in db.todo.find():
        data.append(fp['todo'])
    return render_template('table.html', fingerprints=data)


# /fingerprint
@application.route('/fingerprint/<int:fingerprint_id>', methods=["GET"])
def get_fingerprint(fingerprint_id):
    """
    returns the fingerprint for a specified ID
    """
    fp = db.todo.find({"_id": fingerprint_id}).limit(1)

    if not fp:
        status = {"message:": "No fingerprint were found with this ID."}
        return jsonify(status=404, data=status)
    return render_template('table.html', fingerprints=fp['todo'])


if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)