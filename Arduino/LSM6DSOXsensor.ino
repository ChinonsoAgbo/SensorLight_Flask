#include <Arduino_LSM6DSOX.h>
#include <Wire.h>
#include <WiFiS3.h>
#include <ArduinoJson.h>

const char ssid[] = "AgboIphone";
const char pass[] = "chinonso39?";
const char server[] = "172.20.10.14";
const int port = 5050;

WiFiClient client;
unsigned long lastSendTime = 0;
unsigned long previousMillis = 0;
const int sendInterval = 10; // Send data every 250ms
void setup() {
  Serial.begin(115200);
  Wire.begin();

  // if (!IMU.begin()) {
  //   Serial.println("Failed to initialize IMU.");
  //   while (1);
  // }

  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.println(WiFi.localIP());

  if (client.connect(server, port)) {
    Serial.println("Connected to Flask server");
  } else {
    Serial.println("Connection to Flask server failed");
  }
}

void loop() {
  static float x, y, z;
  
  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(x, y, z);
  }

  if (client.connected()) {
    StaticJsonDocument<128> doc;
    
    // Get the current timestamp in milliseconds since boot
    unsigned long timestamp = millis();
    doc["timestamp"] = timestamp;  // Add timestamp from Arduino
    doc["x"] = x;
    doc["y"] = y;
    doc["z"] = z;
    
    char jsonBuffer[128];
    serializeJson(doc, jsonBuffer);
    
    client.println(jsonBuffer);  
    Serial.println(jsonBuffer);
  } else {
    Serial.println("Connection lost. Reconnecting...");
    client.connect(server, port);
  }
}
