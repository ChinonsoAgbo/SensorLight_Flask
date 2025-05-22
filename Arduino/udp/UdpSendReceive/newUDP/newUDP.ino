#include <SPI.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <Wire.h>
#include "SparkFun_BMI270_Arduino_Library.h"

// Your network credentials
char ssid[] = "SDD_Demo";
char pass[] = "Bobbycar";
// Server IP and port
IPAddress serverIP(192, 168, 0, 100);  // Adjust to your actual server
unsigned int serverPort = 1881;
unsigned int localPort = 2390;      // local port to listen on

// UDP object
WiFiUDP Udp;

// IMU
BMI270 imu;
uint8_t i2cAddress = BMI2_I2C_PRIM_ADDR;
//uint8_t i2cAddress = BMI2_I2C_SEC_ADDR; // 0x69

uint8_t acc_odr = BMI2_ACC_ODR_800HZ;
uint8_t gyro_odr = BMI2_GYR_ODR_800HZ;
uint8_t gyr_Range = BMI2_GYR_RANGE_250;

int count;
int idx;
char packetBuffer[256]; //buffer to hold incoming packet

void setup() {
  Serial.begin(500000);
  while (!Serial)
    ;

  Wire.begin();
   while(imu.beginI2C(i2cAddress) != BMI2_OK)
    {
        // Not connected, inform user
        Serial.println("Error: BMI270 not connected, check wiring and I2C address!");

        // Wait a bit to see if connection is established
        delay(1000);
    }

    imu.setAccelODR(acc_odr);
    imu.setGyroODR(gyro_odr);
  Serial.println("BMI270 connected!");


    count = 1;
    delay(1000);

  // Connect to WiFi
  Serial.print("Connecting to WiFi...");
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println(" connected!");

  // Start UDP
  Udp.begin(localPort);  // Local port can be any unused port
  Serial.println("UDP initialized.");
}

// String DataFrame = String(imu.data.accelX, 3) + ',' + String(imu.data.accelY, 3) + ',' + String(imu.data.accelZ, 3) + ',' + String(imu.data.gyroZ, 3)+ ','+ String(millis(), DEC) ;


void loop() {
  idx = 1;

    long int startTime = millis();

  while (idx <= 10000) {
    imu.getSensorData();
    String DataFrame = String(imu.data.accelX, 3) + ',' + String(imu.data.accelY, 3) + ',' + String(imu.data.accelZ, 3) + ',' + String(imu.data.gyroZ, 3) + ',' + String(millis(), DEC);

    int str_len = DataFrame.length() + 1;
    char DataSample[str_len];
    DataFrame.toCharArray(DataSample, str_len);

    // Send IMU data via UDP to server
    Udp.beginPacket(serverIP, serverPort);
    // Udp.write(DataFrame.c_str());
    Udp.write(DataFrame.c_str());
    Udp.endPacket();
    delay(1);
    idx = idx + 1;

    long int endTime = millis();
    Serial.println(endTime);
    long int duration = endTime - startTime;
    Serial.println("Duration for " + String(idx - 1) + " samples: " + String(duration) + " msec");
  }
}


void printWifiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  Serial.println(" dBm");
}