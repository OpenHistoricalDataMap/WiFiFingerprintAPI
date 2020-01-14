# Start Application
`docker-compose up`

# tests
`pytest`

# Get
`curl -i http://192.168.178.72:5000/fingerprint/00_fp_floor`

# Post
`curl -i -X POST -H "Content-Type: application/json" -d @test_fp.json http://192.168.178.72:5000/fingerprint`

# Put
`curl -i -X PUT -H "Content-Type: application/json" -d @test_fp.json http://192.168.178.72:5000/fingerprint/test_id`

# Delete
`curl -i -X DELETE http://192.168.178.72:5000/fingerprint/test_id`


