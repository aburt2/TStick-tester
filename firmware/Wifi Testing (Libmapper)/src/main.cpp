#include <WiFi.h>
#include <mapper.h>

// For disabling power saving
#include "esp_wifi.h"

const char* ssid     = "***********";     // replace with your SSID
const char* password = "***********"; // replace with your password

mpr_dev dev = 0;
mpr_sig inputSignal = 0;
mpr_sig outputSignal = 0;
mpr_sig repeater = 0;
float seqNumber = 0;
float receivedValue = 0;

// Define delay
int LIBMAPPER_DELAY = 500;

// Set if we are connecting to another ESP32
bool ESP_CONNECTED = false;

// Name of device
const char * DEVICE_NAME = "ESP32-Receiver";

void inputSignalHandler(mpr_sig sig, mpr_sig_evt evt, mpr_id inst, int length,
                        mpr_type type, const void* value, mpr_time time);

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  // Disable WiFi power save (huge latency improvements)
  esp_wifi_set_ps(WIFI_PS_NONE);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  float signalMin = 0.0f;
  float signalMax = 5.0f;

  dev = mpr_dev_new(DEVICE_NAME, 0);
  outputSignal = mpr_sig_new(dev, MPR_DIR_OUT, "output", 1, MPR_FLT, 0,
                             &signalMin, &signalMax, 0, 0, 0);
  inputSignal = mpr_sig_new(dev, MPR_DIR_IN, "input", 1, MPR_FLT, 0,
                            &signalMin, &signalMax, 0, inputSignalHandler,
                            MPR_SIG_UPDATE);
  repeater = mpr_sig_new(dev, MPR_DIR_OUT, "echo", 1, MPR_FLT, 0, &signalMin, &signalMax, 0, 0, 0);
}

void loop() {
  // Increment number and send
  seqNumber += 0.01f;
  mpr_sig_set_value(outputSignal, 0, 1, MPR_FLT, &seqNumber);

  // Print received value
  if (ESP_CONNECTED) {
    Serial.println(receivedValue);
  }

  // Update libmapper device
  mpr_dev_poll(dev, 0);

  // Sleep for delay
  delay(LIBMAPPER_DELAY);
}

void inputSignalHandler(mpr_sig sig, mpr_sig_evt evt, mpr_id inst, int length,
                        mpr_type type, const void* value, mpr_time time) {
  receivedValue = *((float*)value);
  mpr_sig_set_value(repeater, 0, 1, MPR_FLT, value);
}