import requests
import json
import socket

IP = socket.gethostbyname(socket.gethostname())
PORT=5000
ENDPOINT="fingerprint"
URI="%s:%s/%s" %(IP,PORT,ENDPOINT)
HEADERS = {'Content-Type': 'application/json'}

def get_fingerprint_should_return_200():
	request = requests.get(URI + "/test")
	assert request.status_code == 200
