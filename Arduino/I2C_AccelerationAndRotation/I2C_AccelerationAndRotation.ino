#include <Wire.h>
#include "SparkFun_BMI270_Arduino_Library.h"
#include <ArduinoJson.h>
#include <WiFiS3.h>


// Create a new sensor object
BMI270 imu;

// I2C address selection
uint8_t i2cAddress = BMI2_I2C_PRIM_ADDR;  // 0x68
//uint8_t i2cAddress = BMI2_I2C_SEC_ADDR; // 0x69
const size_t jsonDocumentCapacity = 256;
StaticJsonDocument<jsonDocumentCapacity> jsonDocument;


const char ssid[] = "SDD_Demo";
const char pass[] = "Bobbycar";
const char server[] = "192.168.0.100";
const int port = 5050;


// const char ssid[] = "AgboIphone";
// const char pass[] = "chinonso39?";
// const char server[] = "172.20.10.14";
// const int port = 5050;

WiFiClient client;

void setup() {
  // Start serial
  Serial.begin(115200);
  Serial.println("BMI270 Example 1 - Basic Readings I2C");

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

  Serial.println("BMI270 SparkFun connected!");

  // Wifi connection
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
  // Get measurements from the sensor. This must be called before accessing
  // the sensor data, otherwise it will never update
  if (imu.getSensorData() == BMI2_OK) {
    imu.getSensorData();

    // get the current time milisec
    unsigned long currentTimeMillis = millis();

    jsonDocument.clear();  // clear for new data
    JsonObject imuData = jsonDocument.createNestedObject("imuData");


    JsonObject accelerationInGs = imuData.createNestedObject("accelerationInGs");
    accelerationInGs["x"] = imu.data.accelX;
    accelerationInGs["y"] = imu.data.accelY;
    accelerationInGs["z"] = imu.data.accelZ;

    JsonObject rotationInDegSec = imuData.createNestedObject("rotationInDegSec");
    //rotationInDegSec["x"] = imu.data.gyroX;
    //rotationInDegSec["y"] = imu.data.gyroY;
    rotationInDegSec["z"] = imu.data.gyroZ;

    imuData["timestampMillis"] = currentTimeMillis;


    if (client.connected()) {
      // Serialize the JSON document to the Serial Monitor
      serializeJson(jsonDocument, Serial);
      //Serial.println();

      // Serialize the JSON document to to Buffer
      char jsonBuffer[jsonDocumentCapacity + 1];  // ensure enough space
      serializeJson(jsonDocument, jsonBuffer);
      client.println(jsonBuffer);  // send the flask client server



    } else {
      Serial.println("Connection to server lost. Reconnecting...");
      client.connect(server, port);
      if (client.connect(server, port)) {
        Serial.println("Reconnected to Flask server");
      } else {
        Serial.println("Reconnection failed.");
      }
    }
  }
  // delay(10);  // 10 for 100 hz
}