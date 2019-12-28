import requests
import json
import codecs

IP = "192.168.178.70"
PORT = 5000
ENDPOINT = "fingerprint"
URI = "http://" +  IP + ":" + str(PORT) + "/" + ENDPOINT
HEADERS = {'Content-Type': 'application/json'}


###########
#   GET   #
###########


def test_get_fingerprint_should_return_200():
	assert requests.get(URI + "/test").status_code == 200


def test_get_fingerprint_should_return_404():
	assert requests.get(URI + "/invalid").status_code == 404


###########
#   POST  #
###########


def test_post_fingerprint_should_return_201():
	with codecs.open('test_fp.json', 'r', 'utf-8-sig') as json_file:
		data = json.load(json_file)

	assert requests.post(URI, data=json.dumps(data), headers=HEADERS).status_code == 201


def test_post_fingerprint_should_return_400():
	assert requests.post(URI, data=json.dumps({'some' : 'Data'}), headers=HEADERS).status_code == 400


###########
#   PUT   #
###########


def test_put_fingerprint_should_return_400():
	assert requests.post(URI + "/test_id", data=json.dumps({'some' : 'Data'}), headers=HEADERS).status_code == 400


def test_put_fingerprint_should_return_404():
	assert requests.post(URI + "/invalid", data=json.dumps({'some' : 'Data'}), headers=HEADERS).status_code == 400


def test_put_fingerprint_should_return_200():
	with codecs.open('test_fp.json', 'r', 'utf-8-sig') as json_file:
		data = json.load(json_file)

	assert requests.post(URI + "/test_id", data=json.dumps(data), headers=HEADERS).status_code == 200

#############
#   DELETE  #
#############


def test_delete_fingerprint_should_return_200():
	assert requests.post(URI + "/test_id", data=json.dumps({'some' : 'Data'}), headers=HEADERS).status_code == 200


def test_delete_fingerprint_should_return_404():
	assert requests.post(URI + "/test_id", data=json.dumps({'some' : 'Data'}), headers=HEADERS).status_code == 404
