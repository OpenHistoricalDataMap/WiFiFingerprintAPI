#!/usr/bin/env bash
#
# unit test /localize endpoint with various combionations
#
###########################################################
IP=$(hostname -I | cut -d " " -f1)

# one mac and ssid / matching
curl -i ${IP}:5000/localize?mac1=02:00:00:00:01:00&strength1=-50

# two mac and ssids / both matching
curl -i ${IP}:5000/localize?mac1=02:00:00:00:01:00&strength1=-50

# one mac and ssid / not matching
curl -i ${IP}:5000/localize?mac1=04:00:00:00:01:00&strength1=-50


# two mac and ssids / not matching
curl -i ${IP}:5000/localize?mac1=04:00:00:00:01:00&strength1=-50&mac2=04:34:00:00:01:00&strength1=-12

# two mac and ssids / one matching one not matching