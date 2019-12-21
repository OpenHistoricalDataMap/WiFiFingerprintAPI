#!/usr/bin/env bash
#
# unit test (CRUD) /fingerprint endpoint
#
##########################################
IP=$(hostname -I | cut -d " " -f1)

###########
#   POST  #
###########

# Create valid fingerprint / status 201
# Create invalid fingerprint / status 400


###########
#   GET   #
###########

# Read existing fingerprint / 200
curl -i -X POST -H "Content-Type: application/json" -d @fp.json ${IP}:5000/fingerprint
# Read non existing fingerprint / 404

###########
#   PUT   #
###########

# Update existing fingerprint / 200
# Update non existing fingerprint / 404
# Update existing fingerprint with invalid fingerprint / 404


#############
#   DELETE  #
#############

# Delete existing fingerprint / 200
# Delete non existing fingerprint / 404

