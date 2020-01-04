# AccessPointFingerprintAPI
[![Build Status](https://travis-ci.com/FalcoSuessgott/AccessPointFingerprintAPI.svg?branch=master)](https://travis-ci.com/FalcoSuessgott/AccessPointFingerprintAPI)
> HTTP API that stores Wifi Fingerprints and responds with the matching fingerprint for indoor localization.


# ToC
* [Introduction](Introduction)
* [Project Setup](Project Setup)
* [Installation and usage](Installation and Usage)
* [Endpoint Descriptions](Endpoint Descriptions)
* [Examples](Examples)
* [ToDos](Todos)

# Introduction
This project serves a HTTP API that stores WiFi fingerprints (CRUD) from the 
[BVGDetection](https://github.com/OpenHistoricalDataMap/BVGDetection) Android Application. 

Devices, (for now only the ESP8266) can request the API with their current WIFI fingerprint to verify their current location.

# Project Setup
The project contains 3 services / Docker Container:
* `IP:5000` HTTP API
* `IP:27017` MongoDB
* `ÌP:3100` [Mongoku](https://github.com/huggingface/Mongoku) (WebUI for MongoDB)
 

# Installation and Usage
In order to run the application, you´ll need a running docker daemon and docker-compose installed.
For the tests, you will need pytest installed.

```
git clone https://github.com/FalcoSuessgott/AccessPointFingerprintAPI
cd AccessPointFingerprintAPI
# start the application
docker-compuse up
# running tests
pytest tests/
```

# Endpoint Descriptions
This application exposes two endpoints:
* `/fingerprint` manages the WiFI fingerprints (CRUD)
* `/localize` returns the most matching fingerprint based on clients available WiFi's

## `/fingerprint`
Exposes a HTTP API to create, read, update and delete WiFI fingerprint APIs.

See all fingerprints currently stored under `http://IP:5000/fingeprint`.
### Get
> Returns the WiFi fingerprint with the matching id

`$> curl http://IP:5000/fingerprint/fingerprint_id`

Returns:
 * `200` Request was successful
 * `404` No fingerprint were found with the ID
 
### Post 
> Creates a fingerprint

`$› cat fp.json `
```json
{
      "id": "fingerprint_id",
      "description": "Room 4.56 Bulding C",
      "coordinates": "52.56645,12.23232",
      "additionalInfo": "Taken by TM",
      "fingerprint": [
        {
          "timestamp": "20-12-2019-02.31.29",
          "signalSample": [
            {
              "macAddress": "02:00:00:00:01:00",
              "strength": -50
            }
          ]
        },
        {
          "timestamp": "20-12-2019-02.32.32",
          "signalSample": [
            {
              "macAddress": "02:00:00:00:01:00",
              "strength": -50
            }
          ]
        }
  ]
}
```
`$> curl -i -H "Content-Type: application/json" -X POST -d @fp.json http://IP:5000/fingerprint`

Returns:
 * `201` Request was successful
 * `400` Fingerprint does already exist with this ID
 * `404` Invalid Fingerprint
 

### Put
> Updates the fingerprint wit the corresponding ID

`$> curl -i -H "Content-Type: application/json" -X DELETE -d @fp.json http://IP:5000/fingerprint/fingeprint_id`

Returns:
 * `201` Request was successful
 * `400` Invalid fingerprint.
 * `404` No fingerprint were found with this ID.

### Delete
> Deletes the fingerprint with the specified ID

`$> curl -i -X DELETE http://IP:5000/fingerprint/fingerprint_id`

Returns:
 * `201` Request was successful
 * `404` No fingerprint were found with this ID.

## `localize`

### Get
Returns the most matching fingerprint based on specified WiFis, that are currently available for the client.
For example, the ESP8266 does currently see 2 available WiFi`s then the request URI would look like:
 
`http://IP:5000/localize?mac1=00:AA:11:BB:CC:44&strength1=-58&mac2=00:AA:11:BB:DD:44&&strength2=-34`

For the calculation, see [...](...)

# ToDos
*
*
