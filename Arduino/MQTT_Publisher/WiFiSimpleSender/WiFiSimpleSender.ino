/*
  ArduinoMqttClient - WiFi Simple Sender

  This example connects to a MQTT broker and publishes a message to
  a topic once a second.

  The circuit:
  - Arduino MKR 1000, MKR 1010 or Uno WiFi Rev2 board

  This example code is in the public domain.
*/

#include <ArduinoMqttClient.h>
#if defined(ARDUINO_SAMD_MKRWIFI1010) || defined(ARDUINO_SAMD_NANO_33_IOT) || defined(ARDUINO_AVR_UNO_WIFI_REV2)
#include <WiFiNINA.h>
#elif defined(ARDUINO_SAMD_MKR1000)
#include <WiFi101.h>
#elif defined(ARDUINO_ARCH_ESP8266)
#include <ESP8266WiFi.h>
#elif defined(ARDUINO_PORTENTA_H7_M7) || defined(ARDUINO_NICLA_VISION) || defined(ARDUINO_ARCH_ESP32) || defined(ARDUINO_GIGA) || defined(ARDUINO_OPTA)
#include <WiFi.h>
#elif defined(ARDUINO_PORTENTA_C33)
#include <WiFiC3.h>
#elif defined(ARDUINO_UNOR4_WIFI)
#include <WiFiS3.h>
#endif

#include <Wire.h>
#include "SparkFun_BMI270_Arduino_Library.h"
#include <ArduinoJson.h>

///////please enter your sensitive data in the Secret tab/arduino_secrets.h
// char ssid[] = "SDD_Demo";    // your network SSID (name)
// char pass[] = "Bobbycar";    // your network password (use for WPA, or use as key for WEP)

// phone network
char ssid[] = "AgboIphone";   // your network SSID (name)
char pass[] = "chinonso39?";  // your network password (use for WPA, or use as key for WEP)


const char broker[] = "172.20.10.14";  // handy network broker
// const char broker[] = "192.168.0.100"; // router network broker

// To connect with SSL/TLS:
// 1) Change WiFiClient to WiFiSSLClient.
// 2) Change port value from 1883 to 8883.
// 3) Change broker value to a server with a known SSL/TLS root certificate
//    flashed in the WiFi module.

WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);

int port = 1883;
const char topic[] = "arduino/imuDaten";


// Create a new sensor object
BMI270 imu;
// I2C address selection
uint8_t i2cAddress = BMI2_I2C_PRIM_ADDR;  // 0x68
//uint8_t i2cAddress = BMI2_I2C_SEC_ADDR; // 0x69

const size_t jsonDocumentCapacity = 256;
StaticJsonDocument<jsonDocumentCapacity> jsonDocument;

// uint8_t acc_odr = BMI2_ACC_ODR_400HZ;
// uint8_t gyro_odr = BMI2_GYR_ODR_400HZ;
// uint8_t gyr_Range = BMI2_GYR_RANGE_250;


void setup() {
  //Initialize serial and wait for port to open:
  Serial.begin(115200);
  Serial.println("BMI270 400Hz Mqtt broker Test");

  while (!Serial) {
    ;  // wait for serial port to connect. Needed for native USB port only
  }
  // Initialize the I2C library
  Wire1.begin();

  // Check if sensor is connected and initialize
  // Address is optional (defaults to 0x68)
  while (imu.beginI2C(i2cAddress, Wire1) != BMI2_OK) {
    // Not connected, inform user
    Serial.println("Error: BMI270 not connected, check wiring and I2C address!");

    // Wait a bit to see if connection is established
    delay(1000);
  }
  Serial.println("BMI270 connected!");

  // imu.setAccelODR(acc_odr);
  // imu.setGyroODR(gyro_odr);
  // imu.convertRawToDegSecScalar(gyr_Range);
  // Wifi connection
  // attempt to connect to WiFi network:
  Serial.print("Attempting to connect to WPA SSID: ");
  Serial.println(ssid);
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    // failed, retry
    Serial.print(".");
    delay(1000);
  }

  Serial.println("You're connected to the network");
  Serial.println();

  // You can provide a unique client ID, if not set the library uses Arduino-millis()
  // Each client must have a unique client ID
  // mqttClient.setId("clientId");

  // You can provide a username and password for authentication
  mqttClient.setUsernamePassword("chinonso", "passingBroker39?");

  Serial.print("Attempting to connect to the MQTT broker: ");
  Serial.println(broker);

  if (!mqttClient.connect(broker, port)) {
    Serial.print("MQTT connection failed! Error code = ");
    Serial.println(mqttClient.connectError());

    while (1)
      ;
  }

  Serial.println("You're connected to the MQTT broker!");
  Serial.println();
}

const unsigned long interval = 10; // For a target of 100 Hz (every 10 milliseconds)
unsigned long previousMillis = 0;

void loop() {
  mqttClient.poll();
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    if (imu.getSensorData() == BMI2_OK) {
      jsonDocument.clear();
      JsonObject imuData = jsonDocument.createNestedObject("imuData");
      JsonObject accelerationInGs = imuData.createNestedObject("accelerationInGs");
      accelerationInGs["x"] = imu.data.accelX;
      accelerationInGs["y"] = imu.data.accelY;
      accelerationInGs["z"] = imu.data.accelZ;
      JsonObject rotationInDegSec = imuData.createNestedObject("rotationInDegSec");
      rotationInDegSec["z"] = imu.data.gyroZ;
      imuData["timestampMillis"] = currentMillis;

      char jsonBuffer[jsonDocumentCapacity + 1];
      serializeJson(jsonDocument, jsonBuffer);

      // Serial.println(topic); // Keep these for debugging if needed
      Serial.println(jsonBuffer);

      mqttClient.beginMessage(topic, true, 2);
      mqttClient.print(jsonBuffer);
      mqttClient.endMessage();

    } else {
      Serial.println("Error reading sensor data!"); // Handle potential sensor read errors
    }
  }
}