import requests
import json
import codecs
import docker


def get_ip_from_container(container_name, network):
	"""
	returns the ip of docker container
	"""

	client = docker.DockerClient()
	container = client.containers.get(container_name)
	return container.attrs['NetworkSettings']['Networks'][network]['IPAddress']


API_IP = get_ip_from_container("api", "accesspointfingerprintapi_frontend")
PORT = 5000
ENDPOINT = "fingerprint"
URI = "http://" + API_IP + ":" + str(PORT) + "/" + ENDPOINT
HEADERS = {'Content-Type': 'application/json'}


###########
#   POST  #
###########


def test_post_fingerprint_should_return_201():
	with codecs.open('tests/test_fp.json', 'r', 'utf-8-sig') as json_file:
		data = json.load(json_file)

	assert requests.post(URI, json=data, headers=HEADERS).status_code == 201


def test_post_fingerprint_should_return_400():
	assert requests.post(URI, json={'some': 'Data'}, headers=HEADERS).status_code == 400

###########
#   GET   #
###########


def test_get_fingerprint_should_return_200():
	assert requests.get(URI + "/test_id").status_code == 200


def test_get_fingerprint_should_return_404():
	assert requests.get(URI + "/invalid").status_code == 404


###########
#   PUT   #
###########


def test_put_fingerprint_should_return_400():
	assert requests.put(URI + "/test_id", json={'some': 'Data'}, headers=HEADERS).status_code == 400


def test_put_fingerprint_should_return_404():
	assert requests.put(URI + "/invalid", json={'some': 'Data'}, headers=HEADERS).status_code == 404


def test_put_fingerprint_should_return_201():
	with codecs.open('tests/test_fp.json', 'r', 'utf-8-sig') as json_file:
		data = json.load(json_file)

	assert requests.put(URI + "/test_id", json=data, headers=HEADERS).status_code == 201


#############
#   DELETE  #
#############


def test_delete_fingerprint_should_return_201():
	assert requests.delete(URI + "/test_id").status_code == 201


def test_delete_fingerprint_should_return_404():
	assert requests.delete(URI + "/invalid").status_code == 404
