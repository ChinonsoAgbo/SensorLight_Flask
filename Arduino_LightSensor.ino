#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_TSL2561_U.h>
#include <WiFiS3.h> // Correct WiFi library for Uno R4 WiFi

// WiFi credentials
const char* ssid = "AgboIphone";
const char* password = "chinonso39?";

// Server details
const char* host = "172.20.10.14"; // Flask server IP
const int port = 5050;             // Flask server port

// Light sensor
Adafruit_TSL2561_Unified tsl = Adafruit_TSL2561_Unified(TSL2561_ADDR_FLOAT, 12345);

WiFiClient client;
unsigned long lastSendTime = 0;
const int sendInterval = 250; // Send data every 250ms

void setup() {
  Serial.begin(9600);
  Serial.println("Light Sensor TCP Test");

  // Initialize WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected. IP address: " + WiFi.localIP().toString());

  // Try connecting to the server
  connectToServer();

  // Initialize sensor
  if (!tsl.begin()) {
    Serial.println("Ooops, no TSL2561 detected ... Check your wiring or I2C ADDR!");
    while (1);
  }

  configureSensor();
  displaySensorDetails();
}

void loop() {
  sensors_event_t event;
  tsl.getEvent(&event);

  if (event.light) {
    String luxData = String(event.light, 2) + "\n";
    Serial.print("Sending: ");
    Serial.print(luxData);

    if (client.connected()) {
      client.print(luxData);
    } else {
      Serial.println("Connection lost. Reconnecting...");
      connectToServer();
    }
  } else {
    Serial.println("Sensor overload");
  }

  // Send heartbeat message every 5 seconds
  if (millis() - lastSendTime >= 5000) {
    if (client.connected()) {
      client.print("heartbeat\n");  // Send heartbeat to keep connection alive
      Serial.println("💓 Sent heartbeat");
    }
    lastSendTime = millis();
  }

  delay(sendInterval);
}

void configureSensor() {
  tsl.enableAutoRange(true);
  tsl.setIntegrationTime(TSL2561_INTEGRATIONTIME_13MS);

  Serial.println("------------------------------------");
  Serial.print("Gain:          "); Serial.println("Auto");
  Serial.print("Timing:        "); Serial.println("13 ms");
  Serial.println("------------------------------------");
}

void displaySensorDetails() {
  sensor_t sensor;
  tsl.getSensor(&sensor);
  Serial.println("------------------------------------");
  Serial.print("Sensor:        "); Serial.println(sensor.name);
  Serial.print("Driver Ver:    "); Serial.println(sensor.version);
  Serial.print("Unique ID:     "); Serial.println(sensor.sensor_id);
  Serial.print("Max Value:     "); Serial.print(sensor.max_value); Serial.println(" lux");
  Serial.print("Min Value:     "); Serial.print(sensor.min_value); Serial.println(" lux");
  Serial.print("Resolution:    "); Serial.print(sensor.resolution); Serial.println(" lux");
  Serial.println("------------------------------------");
  Serial.println("");
  delay(500);
}

void connectToServer() {
  Serial.println("🔄 Connecting to server...");
  if (client.connect(host, port)) {
    Serial.println("✅ Connected to server");
  } else {
    Serial.println("❌ Connection failed");
  }
}
