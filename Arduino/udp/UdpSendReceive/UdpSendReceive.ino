#include <WiFiS3.h>
#include <WiFiUdp.h>
#include <Wire.h>
#include "SparkFun_BMI270_Arduino_Library.h"

// Your network credentials
char ssid[] = "SDD_Demo";
char pass[] = "Bobbycar";

// Server IP and port
IPAddress serverIP(192, 168, 0, 101);  // Adjust to your actual server
unsigned int serverPort = 1884;

// UDP object
WiFiUDP Udp;

// IMU
BMI270 imu;
uint8_t i2cAddress = BMI2_I2C_PRIM_ADDR;

void setup() {
  Serial.begin(2000000);
  while (!Serial);

  Wire1.begin();
  while (imu.beginI2C(i2cAddress, Wire1) != BMI2_OK) {
    Serial.println("IMU not detected. Check wiring.");
    delay(1000);
  }

  Serial.println("IMU connected!");

  // Connect to WiFi
  Serial.print("Connecting to WiFi...");
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println(" connected!");

  // Start UDP
  Udp.begin(12345); // Local port can be any unused port
  Serial.println("UDP initialized.");
}

void loop() {
  imu.getSensorData();

  String dataString = 
    String(imu.data.accelX, 3) + "," + 
    String(imu.data.accelY, 3) + "," + 
    String(imu.data.accelZ, 3) + "," + 
    String(imu.data.gyroZ, 3) + "," + 
    String(millis());

 
  // Send IMU data via UDP to server
  Udp.beginPacket(serverIP, serverPort);
  Udp.write(dataString.c_str());
  Udp.endPacket();
 Serial.println(dataString);

}
