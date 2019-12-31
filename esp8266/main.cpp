#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WebServer.h>

// Server
WiFiServer server(80);
String header;

// API
const char* host = "http://192.168.178.70:5000/localize?";

// WiFi
const char *ssid = "";
const char *pass = "";

// LEDs
const int WIFI_LED = D1;  // GPIO 5
const int PROBE_LED = D2;  // GPIO 4

void connect_to_wifi(){
  pinMode(WIFI_LED, OUTPUT);
  digitalWrite(WIFI_LED, LOW);
  Serial.print("connecting to ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, pass);

  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }

  digitalWrite(WIFI_LED, HIGH);
  Serial.println(" WiFi connected.");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);
  connect_to_wifi();
  Serial.println("WiFi Network Scan Started");
  server.begin();
}

const char* build_request(char *urlout){
  int n = WiFi.scanNetworks();

  // char urlout[512] = 0;

  strcpy(urlout, host);

  for (int i = 0; i < n; ++i){
    char buffer[8];
    if (i == 0){
      strcat(urlout, "mac");
    } else {
      strcat(urlout, "&mac");
    }
    sprintf(buffer, "%d", i+1);
    strcat(urlout, buffer);
    strcat(urlout, "=");
    strcat(urlout, WiFi.BSSIDstr(i).c_str());
    strcat(urlout, "&strength");
    strcat(urlout, buffer);
    strcat(urlout, "=");
    sprintf(buffer, "%d", WiFi.RSSI(i));
    strcat(urlout, buffer);
  }

  return urlout;
}

void loop() {
WiFiClient client = server.available();
HTTPClient http;
char urlout[512] = "";
const char* request = build_request(urlout);
http.begin(request);
int httpCode = http.GET();
String payload;
if (httpCode > 0) {
  payload = http.getString();
}

  if (client) {                             // Falls sich ein neuer Client verbindet,
    Serial.println("Neuer Client.");          // Ausgabe auf den seriellen Monitor
    String currentLine = "";                // erstelle einen String mit den eingehenden Daten vom Client
    while (client.connected()) {            // wiederholen so lange der Client verbunden ist
      if (client.available()) {             // Fall ein Byte zum lesen da ist,
        char c = client.read();             // lese das Byte, und dann
        Serial.write(c);                    // gebe es auf dem seriellen Monitor aus
        header += c;
        if (c == '\n') {                    // wenn das Byte eine Neue-Zeile Char ist
          // wenn die aktuelle Zeile leer ist, kamen 2 in folge.
          // dies ist das Ende der HTTP-Anfrage vom Client, also senden wir eine Antwort:
          if (currentLine.length() == 0) {
            // HTTP-Header fangen immer mit einem Response-Code an (z.B. HTTP/1.1 200 OK)
            // gefolgt vom Content-Type damit der Client weiss was folgt, gefolgt von einer Leerzeile:
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println("Connection: close");
            client.println();

            // Hier wird nun die HTML Seite angezeigt:
            client.println("<!DOCTYPE html><html>");
            client.println("<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">");
            client.println("<link rel=\"icon\" href=\"data:,\">");
            // Es folgen der CSS-Code um die Ein/Aus Buttons zu gestalten
            // Hier können Sie die Hintergrundfarge (background-color) und Schriftgröße (font-size) anpassen
            client.println("<style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}");
            client.println(".button { background-color: #333344; border: none; color: white; padding: 16px 40px;");
            client.println("text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}");
            client.println(".button2 {background-color: #888899;}</style></head>");

            // Webseiten-Überschrift
            client.println("<body><h1>ESP8266 Web Server</h1>");
            client.println(payload);
            client.println("</body></html>");
            client.println();
            // und wir verlassen mit einem break die Schleife
            break;
          } else { // falls eine neue Zeile kommt, lösche die aktuelle Zeile
            currentLine = "";
          }
        } else if (c != '\r') {  // wenn etwas kommt was kein Zeilenumbruch ist,
          currentLine += c;      // füge es am Ende von currentLine an
        }
      }
    }
    // Die Header-Variable für den nächsten Durchlauf löschen
    header = "";
    // Die Verbindung schließen
    client.stop();
    Serial.println("Client getrennt.");
    Serial.println("");
  }
  delay(10000);
}
