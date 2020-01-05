# ESP8266 Client Code
This directory contains a `main.cpp` that is an example how to communicates with the API.

# ToC
* [Initialization](#Initialization)
* [Schematics](#Schematics) 
* [Upload](#Upload)
* [Example](#Example)  

# Initialization
Make sure the ESP8266 has a functional firmware installed.
You can easily build and receive the firmware on [nodemcu-build.com](https://nodemcu-build.com/).
After you have downloaded the firmware from the link received in the confirmation mail, you can flash the firmware on to the
ESP8266 using the [`esptool.py`](https://nodemcu.readthedocs.io/en/latest/flash/).

Example:

`esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0 /path/to/firmware.bin`
 
 
# Schematics (optional)
The examples uses two LEDs to verify the status of the ESP8266.

* green LED (WIFI connection) GPIO 5
* blue LED (API response received) GPIO 4

See this [tutorial](https://www.instructables.com/id/NodeMCU-Basic-Project-Blink-a-LED/) to combine LEDs to the NodeMCU.
# Usage
Adjust the following parameter in `main.cpp`:

```
const char* api_ip = ""; // IP of the API 
const char *ssid = ""; // SSID 
const char *pass = ""; // Password 
```


# Upload
You can upload the code using the [ARDUINO IDE](https://www.arduino.cc/en/main/software).
It is recommended to install the IDE through the provided donwload files and not the Ubuntu Software Store. Since the
package is broken due to corrupt serial port permissions.

# Verify
After you successfully uploaded and compiled the code onto the NodeMCU, you can verify the results with:

```
curl -i http://IP_OF_NODEMCU/ 
```
