import requests
import docker
import pytest
import json
import codecs


def get_ip_from_container(container_name, network):
	"""
	returns the ip of docker container
	"""

	client = docker.DockerClient()
	container = client.containers.get(container_name)
	return container.attrs['NetworkSettings']['Networks'][network]['IPAddress']


API_IP = get_ip_from_container("api", "accesspointfingerprintapi_frontend")
PORT = 5000
ENDPOINT = "localize"
URI = "http://" + API_IP + ":" + str(PORT) + "/" + ENDPOINT
HEADERS = {'Content-Type': 'application/json'}
FINGERPRINTS = ['00_fp_floor.json', '01_fp_kitchen.json', '02_fp_room_pw.json', '03_fp_room_tm.json', '04_fp_room_pw.json']


#################
#   BEFORE_ALL  #
#################
@pytest.fixture(scope="module")
def add_fp(request):
	for fingerprint in FINGERPRINTS:
		with codecs.open('tests/fingerprints/' + fingerprint, 'r', 'utf-8-sig') as json_file:
			data = json.load(json_file)
			requests.post("http://" + API_IP + ":" + str(PORT) + "/fingerprint", json=data, headers=HEADERS)
	print("Fingerprints posted.")

	def del_fp():
		for fp in FINGERPRINTS:
			requests.delete("http://" + API_IP + ":" + str(PORT) + "/fingerprint/" + fp)
	print("Fingerprints deleted.")
	request.addfinalizer(del_fp())

################
#   AFTER_ALL  #
################
#@pytest.fixture(scope="session", autouse=True)
#def del_fp():#
	#for fingerprint in FINGERPRINTS:
#		requests.delete("http://" + API_IP + ":" + str(PORT) + "/fingerprint/" + fingerprint)
	#print("Fingerprints deleted.")

##########
#   GET  #
##########


def test_get_localize_one_matching_mac_should_return_200():
	assert requests.get(URI + "?mac1=02:00:00:00:01:00&strength1=-50").status_code == 200


def test_get_localize_two_matching_mac_should_return_200():
	assert requests.get(
		URI + "?mac1=02:00:00:00:01:00&strength1=-50&mac2=03:00:00:00:01:00&strength2=-25").status_code == 200


def test_get_localize_one_mac_should_return_404():
	assert requests.get(URI + "?mac1=00:00:00:00:00:00strength1=-50").status_code == 404


def test_get_localize_one_matching_mac_should_return_200_1():
	assert requests.get(
		URI + "?mac1=00:00:00:00:00:00&strength1=-50&mac2=03:00:00:00:01:00&strength2=-25").status_code == 200


def test_get_localize_two_mac_should_return_404():
	assert requests.get(
		URI + "?mac1=00:00:00:00:00:00&strength1=-50&mac2=00:00:00:00:01:00&strength2=-25").status_code == 404


def test_get_localize_invalid_request_should_return_400():
	assert requests.get(URI + "?tes=1&invalid=ok").status_code == 400


def test_get_localize_invalid_request_should_return_400_1():
	assert requests.get(URI + "?mac1=00:00:00:00:00:00&strength2=-25").status_code == 400


def test_get_localize_invalid_request_should_return_400_2():
	assert requests.get(URI + "?mac1=00:as:00:00:00:00&strength1=ok").status_code == 400


def test_get_localize_invalid_request_should_return_400_3():
	assert requests.get(URI + "?mac1=03:00:00:00:01:00&strength1=112").status_code == 400


def test_get_localize_invalid_request_should_return_400_4():
	assert requests.get(URI).status_code == 400

