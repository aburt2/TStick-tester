/*---------------------------------------------------------------------------------------------

  Open Sound Control (OSC) library for the ESP8266/ESP32

  Example for sending messages from the ESP8266/ESP32 to a remote computer
  The example is sending "hello, osc." to the address "/test".

  This example code is in the public domain. 

--------------------------------------------------------------------------------------------- */
// Example code from OSC Arduino Github
// https://github.com/CNMAT/OSC
#include <WiFi.h>
#include <WiFiUdp.h>
#include <OSCMessage.h>
#include <OSCBundle.h>

char ssid[] = "*****************";          // your network SSID (name)
char pass[] = "*******";                    // your network password

WiFiUDP Udp;                                // A UDP instance to let us send and receive packets over UDP
const IPAddress outIp(10,40,10,105);        // remote IP of your computer
const unsigned int outPort = 8000;          // remote port to receive OSC
const unsigned int localPort = 8888;        // local port to listen for OSC packets (actually not used for sending)

// Setup test
int OSC_DELAY = 500; // ms delay
int seq = 0; // sequence
int last_time = 0;
bool first = true;

// OSC messages
OSCMessage rxmsg;
OSCMessage txmsg;
int rx_num;

void setup() {
    Serial.begin(115200);

    // Connect to WiFi network
    Serial.println();
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);
    WiFi.begin(ssid, pass);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("");

    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());

    Serial.println("Starting UDP");
    Udp.begin(localPort);
    Serial.print("Local port: ");
#ifdef ESP32
    Serial.println(localPort);
#else
    Serial.println(Udp.localPort());
#endif

}

void rxnum(OSCMessage &msg) {
  rx_num = msg.getInt(0);
  Serial.println(rx_num);
}

void loop() {
    // Receive OSC Messages
    int size = Udp.parsePacket();

    if (size > 0) {
      while (size--) {
        rxmsg.fill(Udp.read());
      }
      if (!rxmsg.hasError()) {
        rxmsg.dispatch("/test", rxnum);
        Serial.println(rx_num);
      }
    }

    if ((millis() - last_time) > OSC_DELAY)  {
      // set new time
      last_time = millis();
      
      // Send message
      OSCMessage msg("/test");
      msg.add(seq);
      Udp.beginPacket(outIp, outPort);
      msg.send(Udp);
      Udp.endPacket();
      msg.empty();
      delay(OSC_DELAY);

      // Increase sequence
      seq++;
    }
}
