# AccessPointFingerprintAPI
This Project stores Access Points Fingerprints from mobile devices (e.g smartphone, esp8266, ..) and its geolocation.
If requested, the API responds with the corresponding geolocation for a specific fingerprint.

It is adapted to the [BVGDetection](https://github.com/OpenHistoricalDataMap/BVGDetection) Android Application.

## Example Format
```json
{
      "id": "test",
      "description": "test desc",
      "coordinates": "",
      "additionalInfo": "",
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

# Usage
```
git clone https://github.com/FalcoSuessgott/AccessPointFingerprintAPI
cd AccessPointFingerprintAPI
docker-compuse up
```

# Project Setup 
* `IP:5000` HTTP API
* `IP:27017` MONGODB
* `ÌP:3100` [Mongoku](https://github.com/huggingface/Mongoku) (WebUI for MongoDB)

# HTTP API
## Get
> Returns the fingeprint with the matching id
>
`$> curl http://IP:5000/fingerprint/test`

## Post 
> Creates a fingerprint
`$› cat fp.json `
```json
{
      "id": "test",
      "description": "test desc",
      "coordinates": "52.56645,12.23232",
      "additionalInfo": "blabla",
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
## Put

## Delete

