#!/usr/bin/env bash
#
# Uploads and compiles and runs lua code.
# Requires nodemcu-uploader (https://github.com/kmpm/nodemcu-uploader)
#
# Author:   Tom Morelly
# Date:     30.12.2019
#
#######################################################################

nodemcu-uploader upload esp8266/init.lua --verify=raw
nodemcu-uploader file do init.lua

# Code:
* connect to wifi
* scan and parse AP, MAC and Strength
* build http request
* parse response
* display on webserver
* loop